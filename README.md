 #  ![KanMind Logo](assets/icons/logo_icon.svg)            Kanmind Backend API  



This is a RESTful API backend for the **Kanmind** Kanban board application, built with Django and Django REST Framework (DRF).  
It supports user registration, authentication, boards, tasks, comments, and permissions for collaborative task management.

---

## Features

- User registration and token-based authentication
- CRUD operations on Boards, Tasks, and Comments
- Permissions ensuring only board members or owners can access and modify data
- Task assignment and review workflows
- Commenting on tasks
- API schema and documentation support with **drf-spectacular** (OpenAPI/Swagger)

---

## Requirements

- Python 3.10+
- Django 5.2+
- Django REST Framework

---

## Setup & Installation

1. **Clone the repository**

    ```bash
    git clone https://github.com/your-username/kan_mind_backend.git
    cd kan_mind_backend
    ```

2. **Create and activate a virtual environment**

    ```bash
    python3 -m venv env
    source env/bin/activate  # macOS/Linux
    # .\env\Scripts\activate # Windows
    ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Apply migrations**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. **Create a superuser (optional, for admin access)**

    ```bash
    python manage.py createsuperuser
    ```

6. **Run the development server**

    ```bash
    python manage.py runserver
    ```

---

## Usage

- API base URL: `http://127.0.0.1:8000/api/`
  

### Authentication

- Token-based authentication is used.
- Obtain a token via the login endpoint.
- Include the token in the `Authorization` header as:  
  `Authorization: Token <your_token>`

---

## Notes

- All endpoints (except registration and login) require authentication.
- Boards are collaborative; only owners or members can access or modify them.
- Tasks support assignment and review.
- Comments belong to tasks and require membership to create/delete.

---

