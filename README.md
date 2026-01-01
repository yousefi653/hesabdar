# HesabDar

A **web-based accounting application** for managing income, expenses, and financial reports, built with Django.

## Features

* Add, edit, and manage **income and expense records**
* Categorize financial transactions
* Support for **Jalali (Persian) dates**
* Financial dashboard with **charts and reports**
* User authentication (registration and login)
* Web-based user interface with dynamic forms and pages

---

## Tech Stack

* **Python**
* **Django**
* **SQLite** (easily replaceable with PostgreSQL)
* **jdatetime** (Jalali date handling)
* **matplotlib** (financial charts and statistics)
* HTML / CSS (Django Templates)

---

## Project Architecture

The project follows a modular Django architecture and includes the following layers:

* **Models**: Financial data structures and relationships
* **Views**: Business logic and request handling
* **Forms**: Input validation and user data processing
* **Templates**: Web UI and presentation layer
* **Static files**: Styles and frontend assets

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yousefi653/hesabdar.git
cd hesabdar
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\\Scripts\\activate     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Run the development server

```bash
python manage.py runserver
```

Then open the application in your browser:

```
http://127.0.0.1:8000/
```

---

## Reports & Charts

The dashboard provides visual financial reports using charts, giving users a clear overview of their income and expenses.

---

## Project Goals

* Practice and apply **real backend development with Django**
* Work with financial data and accounting logic
* Build a practical system close to real-world use cases

---

## License

This project was developed for educational and portfolio purposes.

---

## Author

**Yousef Ghasemi**
GitHub: [https://github.com/yousefi653](https://github.com/yousefi653)

---

⭐ If you find this project useful, feel free to give it a star!

