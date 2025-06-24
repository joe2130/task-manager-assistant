import os
import sys
import json
import sqlite3
import requests
from dotenv import load_dotenv
from datetime import datetime, date

# Load API key
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# Constants
DB_FILE = "task_manager.db"
MODEL = "openai/gpt-3.5-turbo"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# DB setup
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT,
    priority TEXT,
    due TEXT,
    category TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Save a task to DB
def save_task(task_data):
    cursor.execute("""
        INSERT INTO tasks (task, priority, due, category)
        VALUES (?, ?, ?, ?)
    """, (
        task_data.get("task", ""),
        task_data.get("priority", ""),
        task_data.get("due", ""),
        task_data.get("category", "Uncategorized")
    ))
    conn.commit()

# List tasks
def list_tasks():
    cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    rows = cursor.fetchall()
    if not rows:
        print("📭 No tasks found.")
        return
    print("\n📋 All Tasks:")
    for row in rows:
        print(f"[{row[0]}] {row[1]} | Priority: {row[2]} | Due: {row[3]} | Category: {row[4]} | Status: {row[5]}")

# Mark task as done
def mark_done(task_id):
    cursor.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))
    conn.commit()
    print(f"✅ Task {task_id} marked as done.")

# Delete task
def delete_task(task_id):
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    print(f"🗑️ Task {task_id} deleted.")

# Show daily summary
def daily_summary():
    print("\n📅 Daily Summary (Due today or marked high):")
    cursor.execute("""
        SELECT * FROM tasks WHERE 
        due LIKE ? OR 
        priority='High' AND status='pending'
    """, (f"%{date.today().strftime('%A')}%",))
    rows = cursor.fetchall()
    if not rows:
        print("No urgent tasks for today.")
        return
    for row in rows:
        print(f"[{row[0]}] {row[1]} | Due: {row[3]} | Priority: {row[2]}")

# Prompt builder
def create_prompt(user_input):
    return f"""
You are a smart task manager assistant.

From the user's input, extract:
- task (a short title)
- priority (Low, Medium, High)
- due (date or time if any)
- category (e.g., Work, Personal, Study)

Return valid JSON like:
{{
  "task": "...",
  "priority": "...",
  "due": "...",
  "category": "..."
}}

User Input: "{user_input}"
"""

# Main CLI loop
while True:
    print("\n🔹 Type a new task, or command [list / done <id> / delete <id> / summary / exit]:")
    user_input = sys.stdin.readline().strip()

    if user_input.lower() == "exit":
        print("👋 Goodbye!")
        break
    elif user_input.lower() == "list":
        list_tasks()
    elif user_input.lower().startswith("done "):
        try:
            task_id = int(user_input.split()[1])
            mark_done(task_id)
        except:
            print("⚠️ Invalid task ID.")
    elif user_input.lower().startswith("delete "):
        try:
            task_id = int(user_input.split()[1])
            delete_task(task_id)
        except:
            print("⚠️ Invalid task ID.")
    elif user_input.lower() == "summary":
        daily_summary()
    else:
        # Treat as a task input
        prompt = create_prompt(user_input)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://chat.openrouter.ai",
            "X-Title": "task-manager-cli"
        }
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            res = requests.post(API_URL, headers=headers, json=payload)
            res.raise_for_status()
            reply = res.json()["choices"][0]["message"]["content"]
            print("\n🧠 Assistant parsed:")
            print(reply)

            try:
                task_data = json.loads(reply)
                save_task(task_data)
                print("✅ Task saved to database!")
            except json.JSONDecodeError:
                print("⚠️ Could not parse assistant reply.")
        except Exception as e:
            print(f"❌ Error: {e}")
