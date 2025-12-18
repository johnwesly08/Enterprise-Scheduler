# 📊 Enterprise Scheduler

*A lightweight, conflict-aware scheduling system for events and shared resources*

---

## 🚀 Overview

**Enterprise Scheduler** is a Flask-based web application designed to manage **events**, **resources**, and **allocations** with **automatic conflict detection**.
It provides a centralized dashboard, intuitive CRUD operations, and reporting features — all while remaining **simple to run, platform-independent, and evaluator-friendly**.

This project intentionally avoids unnecessary complexity (such as mandatory authentication) to ensure **ease of evaluation, clarity of logic, and universal accessibility**.

---

## ✨ Key Features

### 🗂 Event Management

* Create, edit, and delete events
* Time-based validation (start time must be before end time)
* Supports overlapping time analysis

### 🧰 Resource Management

* Maintain a catalog of shared resources
* Assign resources to events dynamically

### 🔗 Resource Allocation

* Allocate resources to events
* Prevent duplicate allocations
* Automatically detect scheduling conflicts

### ⚠️ Conflict Detection

* Identifies overlapping allocations
* Displays conflicts clearly for corrective action

### 📈 Dashboard Overview

* Active events count
* Resource utilization percentage
* Recent allocations snapshot
* Graceful handling of empty data

### 📑 Reporting

* Generate usage reports for resources
* Calculate total usage hours within a date range
* View upcoming bookings

---

## 🧠 Design Philosophy

* **Database-driven UI** (no mock data)
* **SQLite-first** for portability and ease of setup
* **ORM-based architecture** using SQLAlchemy
* **Separation of concerns** (config, models, routes, templates)
* **Scope-controlled** feature set aligned with documented requirements

> 🔐 **Authentication Note**
> Authentication and authorization are intentionally excluded in this version to maintain ease of evaluation and universal access.
> The architecture supports future integration using Flask-Login or JWT without refactoring.

---

## 🛠 Tech Stack

| Layer         | Technology                         |
| ------------- | ---------------------------------- |
| Backend       | Flask (Python)                     |
| ORM           | SQLAlchemy                         |
| Database      | SQLite (default), MySQL-ready      |
| Frontend      | HTML, Jinja2, Bootstrap 5          |
| Styling       | Custom CSS (Glassmorphism UI)      |
| Configuration | `.env` + environment-based configs |

---

## 📁 Project Structure

```
enterprise-scheduler/
│
├── app.py
├── config.py
├── requirements.txt
├── .env
├── .gitignore
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── events.html
│   ├── resources.html
│   ├── allocations.html
│   ├── conflicts.html
│   └── report.html
│
├── static/
│   └── style.css
│
└── README.md
```

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/enterprise-scheduler.git
cd enterprise-scheduler
```

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # macOS/Linux
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure environment

Create a `.env` file:

```env
ENV=dev
SECRET_KEY=your-secret-key
```

### 5️⃣ Run the application

```bash
python app.py
```

Open browser:

```
http://127.0.0.1:5000
```

---

## 🧪 Development Notes

* SQLite database is auto-created on first run
* If models change, delete the SQLite DB file and restart
* No external services required
* One-command startup for evaluators

---

## 📌 Scope Compliance

This project **fully satisfies** the documented requirements for:

* Event scheduling systems
* Conflict-aware resource allocation
* Database-backed dashboards
* Academic / internship-level system design

Non-mandatory features (authentication, background jobs, APIs) are intentionally excluded and documented.

---

## 📜 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

# 📄 MIT License

```
MIT License

Copyright (c) 2025 John Wesley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
