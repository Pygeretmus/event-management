# 🗓️ Event Management API

A Django RESTful API for managing events — including event creation, user registration, filtering, and email notifications.

---

## 🛠️ Tech Stack

- **Python 3.11.13**
- **Django 5.2.4**
- **Django REST Framework**
- **PostgreSQL 14**
- **Docker / Docker Compose**
- **JWT Authentication**
- **drf-spectacular** for Swagger Docs

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Pygeretmus/event-management.git
cd event-management
```

### 2. Run with Docker

```bash
docker-compose up --build
```

Visit the API at:  
http://localhost:8000

Swagger docs:  
http://localhost:8000/api/schema/swagger-ui/

---

## 🔐 Authentication

JWT-based authentication.

### Register

```
POST /api/users/create/
```

### Obtain Token

```
POST /api/token/
```

Include token in requests:

```
Authorization: Bearer <your_token>
```

---

## 📚 API Endpoints

| Method | Endpoint                         | Description                      |
|--------|----------------------------------|----------------------------------|
| GET    | `/api/events/`                  | List all events                  |
| POST   | `/api/events/`                  | Create a new event               |
| GET    | `/api/events/{id}/`             | Retrieve event details           |
| PUT    | `/api/events/{id}/`             | Update (fully) an event          |
| PATCH  | `/api/events/{id}/`             | Update (partially) an event      |
| DELETE | `/api/events/{id}/`             | Delete an event                  |
| POST   | `/api/events/{id}/register/`    | Register for an event            |

---

## 🔍 Filtering & Search

### Search

```http
GET /api/events/?search=expo
```

Searches by title, location, and organizer username (case-insensitive).

### Date Range Filtering

```http
GET /api/events/?start_date=2025-07-01T00:00:00Z&end_date=2025-07-31T23:59:59Z
```

Filters events between the given date range.

---

## 📧 Email Notifications

Users receive an email confirmation after successfully registering for an event.

> ⚠️ Requires configuring `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in `.env` or settings.

---
