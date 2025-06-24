# 🧠 AI Task Manager Assistant (CLI-Based)

A natural-language-powered task manager built with Python, SQLite, and OpenRouter (GPT-3.5). Create and manage tasks using simple sentences like:
Remind me to submit my report by Friday, it's urgent, category work.

## 🚀 Features

✅ Natural language task input  
✅ Auto-parses priority, due date, category  
✅ Stores tasks in SQLite database  
✅ CLI commands: `list`, `done <id>`, `delete <id>`, `summary`  
✅ OpenRouter API (Free GPT-3.5)  
✅ Simple and extensible structure

---

## 📦 Requirements

- Python 3.8+
- `openrouter.ai` API key (free, no card required)
- `requests`, `python-dotenv`

---

## 🛠️ Setup Guide

#1. Clone Repository

```bash
git clone https://github.com/joe2130/task-manager-assistant.git
cd task-manager-assistant

2. Install Dependencies

pip install -r requirements.txt

3. Add API Key
Create a .env file:

OPENROUTER_API_KEY=your_openrouter_key_here
(Use .env.example as a reference)

4. Run the CLI

python main.py