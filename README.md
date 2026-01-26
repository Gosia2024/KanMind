

# KanMind – Backend API 🧠

````bash

KanMind is a **RESTful backend API** built with **Django** and **Django REST Framework**.  
It provides authentication, board management, task handling, and commenting features
for a Kanban-style application.

> ⚠️ This repository contains **backend only** (no frontend).

---

## 🚀 Quickstart

Follow these steps to run the project locally.

### 1. Clone repository
```bash
git clone https://github.com/Gosia2024/KanMind.git
cd KanMind
````

## 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Run development server

```bash
python manage.py runserver
```

API will be available at:
👉 **[http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)**

---

## 📚 Table of Contents

- [KanMind – Backend API 🧠](#kanmind--backend-api-)
  - [2. Create virtual environment](#2-create-virtual-environment)
    - [3. Install dependencies](#3-install-dependencies)
    - [4. Apply migrations](#4-apply-migrations)
    - [5. Run development server](#5-run-development-server)
  - [📚 Table of Contents](#-table-of-contents)
  - [🧱 Tech Stack](#-tech-stack)
  - [🗂 Project Structure](#-project-structure)
  - [🔐 Authentication](#-authentication)
    - [Register](#register)
    - [Login](#login)
  - [✨ Main Features](#-main-features)
    - [Boards](#boards)
    - [Tasks](#tasks)
    - [Comments](#comments)
  - [🛡 Permissions Overview](#-permissions-overview)
  - [📡 HTTP Status Codes](#-http-status-codes)

---

## 🧱 Tech Stack

* **Python** 3.10+

- **Django**
- **Django REST Framework**
- **Token Authentication (DRF)**
- **SQLite** (development & tests)

---

## 🗂 Project Structure

```text
KanMind/
├── core/            # Django project (settings, urls, wsgi)
├── auth_app/        # Authentication & user logic
├── boards_app/      # Boards domain
├── tasks_app/       # Tasks & comments domain
├── requirements.txt
├── manage.py
└── README.md
```

Each app contains an `api/` directory with:

- `serializers.py`
- `views.py`
- `urls.py`
- `permissions.py`

---

## 🔐 Authentication

Authentication is handled via **Token Authentication**.

### Register

```bash
POST /api/registration/
```

### Login

```bash
POST /api/login/
```

The response contains an authentication token.

All authenticated requests must include the header:

```bash
Authorization: Token <your_token>
```

---

## ✨ Main Features

### Boards

* Create, list, update, and delete boards

- Board owner and member permissions

* Board details include members and tasks

### Tasks

* Create tasks inside boards

* Assign **assignee** and **reviewer**

* Filter tasks:

  * Assigned to me

  * Reviewing

* Update and delete tasks with permission checks

### Comments

* Add comments to tasks
* List task comments
* Only comment authors can delete their comments

---

## 🛡 Permissions Overview

* Only authenticated users can access the API
* Board access: **owner or board member**
* Task creation & update: **board member**
* Task deletion: **task creator or board owner**
* Comment deletion: **comment author only**

---

## 📡 HTTP Status Codes

* `200 OK` – successful request
* `201 CREATED` – resource created
* `204 NO CONTENT` – resource deleted
* `400 BAD REQUEST` – validation error
* `401 UNAUTHORIZED` – authentication required
* `403 FORBIDDEN` – permission denied
* `404 NOT FOUND` – resource does not exist

