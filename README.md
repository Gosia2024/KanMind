# KanMind – Backend API

KanMind is a RESTful backend API built with **Django** and **Django Rest Framework**.
It provides authentication, board management, task handling, and commenting features
for a Kanban-style application.

This repository contains **backend only** (no frontend).

---

## Quickstart

Follow these steps to run the project locally.

```bash
# 1. Clone repository
git clone <repository-url>
cd KanMind

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / Mac
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Run development server
python manage.py runserver

API will be available at:
http://127.0.0.1:8000/api/

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Authentication](#authentication)
- [Main Features](#main-features)
  - [Boards](#boards)
  - [Tasks](#tasks)
  - [Comments](#comments)
- [Permissions Overview](#permissions-overview)
- [HTTP Status Codes](#http-status-codes)

## Tech Stack

- Python 3.10+
- Django
- Django Rest Framework
- Token Authentication (DRF)
- SQLite (development & tests)

## Project Structure

- core/ # Django project (settings, urls, wsgi)
- auth_app/ # Authentication & user logic
- boards_app/ # Boards domain
- tasks_app/ # Tasks & comments domain
- requirements.txt
- manage.py
- README.md

Each app contains an `api/` directory with:

- `serializers.py`
- `views.py`
- `urls.py`
- `permissions.py`
## Authentication

Authentication is handled via **Token Authentication**.

### Register

`POST /api/registration/`
### Login

`POST /api/login/`

The response contains an authentication token.

All authenticated requests must include the following header:

Authorization: Token <your_token>
## Main Features

### Boards

- Create, list, update and delete boards
- Board owner and member permissions
- Board details include members and tasks

### Tasks

- Create tasks inside boards
- Assign assignee and reviewer
- Filter tasks:
  - Assigned to me
  - Reviewing
- Update and delete tasks with permission checks

### Comments

- Add comments to tasks
- List task comments
- Only comment authors can delete their comments

## Permissions Overview

- Only authenticated users can access the API
- Board access: owner or board member
- Task creation and update: board member
- Task deletion: task creator or board owner
- Comment deletion: comment author only
## HTTP Status Codes

- `200 OK` – successful request
- `201 CREATED` – resource created
- `204 NO CONTENT` – resource deleted
- `400 BAD REQUEST` – validation error
- `401 UNAUTHORIZED` – authentication required
- `403 FORBIDDEN` – permission denied
- `404 NOT FOUND` – resource does not exist
