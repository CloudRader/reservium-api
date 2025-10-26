# 🌀 Reservium API

**Reservium** — a ready-to-go reservation system.

Backend service powering the **Reservium platform**, providing event, calendar, and reservation management with integrated authentication, mail notifications, and Google Calendar synchronization.

---

## 🌐 Overview

Reservium is a **FastAPI-based backend** designed to automate and simplify reservation management.  
It integrates seamlessly with **Keycloak** for authentication, **Google Calendar** for scheduling, and **Dormitory Access APIs** for internal facility management.

**Part of the Reservium Suite:**
- 🧩 **[Reservium API](https://github.com/CloudRader/reservium-api)** — core backend (this project)
- 💻 **[Reservium UI](https://github.com/CloudRader/reservium-ui)** — web frontend

---

## 📘 API Reference

- **Production API:** [api.reservation.buk.cvut.cz/docs](https://api.reservation.buk.cvut.cz/docs)  
- **Development API:** [api.develop.reservation.buk.cvut.cz/docs](https://api.develop.reservation.buk.cvut.cz/docs)

---

## ⚙️ Quick Start with Docker Compose

Reservium can be deployed quickly with Docker.  
You only need a `.env` file and a `token.json` file.

### 📁 Example Directory Layout

/your-project

├── .env

├── docker-compose.yml

└── token.json

---

### 🧩 docker-compose.yml

```yaml
---
services:
  db:
    container_name: db
    image: postgres:latest
    restart: on-failure
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql
    networks:
      - internal

  reservium-api:
    container_name: reservium-api
    image: darkrader/reservium-api:latest
    environment:
      ORGANIZATION_NAME: "Your organization name"

      DB__POSTGRES_USER: ${POSTGRES_USER}
      DB__POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      DB__POSTGRES_DB: ${POSTGRES_DB}
      DB__POSTGRES_SERVER: db

      MAIL__USERNAME: ${MAIL__USERNAME}
      MAIL__PASSWORD: ${MAIL__PASSWORD}
      MAIL__FROM_NAME: ${MAIL__FROM_NAME}
      MAIL__SENT_DORMITORY_HEAD: true  # defalt false
      MAIL__DORMITORY_HEAD_EMAIL: develop@buk.cvut.cz

      KEYCLOAK__SERVER_URL: ${KEYCLOAK__SERVER_URL}
      KEYCLOAK__REALM: ${KEYCLOAK__REALM}
      KEYCLOAK__CLIENT_ID: ${KEYCLOAK__CLIENT_ID}
      KEYCLOAK__CLIENT_SECRET: ${KEYCLOAK__CLIENT_SECRET}

      SPICEDB__CLIENT_SECRET: ${SPICEDB__CLIENT_SECRET}

      GOOGLE__CLIENT_ID: ${GOOGLE__CLIENT_ID}
      GOOGLE__CLIENT_SECRET: ${GOOGLE__CLIENT_SECRET}

      DORMITORY_ACCESS_SYSTEM__API_KEY: ${DORMITORY_ACCESS_SYSTEM__API_KEY}
    volumes:
      - ./token.json:/usr/src/app/src/token.json
    depends_on:
      - db
    restart: on-failure
    ports:
      - "8000:8000"
    networks:
      - internal

  reservium-ui:
    container_name: reservium-ui
    image: darkrader/reservium-ui:latest
    ports:
      - "3000:3000"
    networks:
      - internal

networks:
  internal:

volumes:
  postgres_data:
```

### 🧾 .env Example

```env
# Database
POSTGRES_DB=reservium
POSTGRES_USER=reservium
POSTGRES_PASSWORD=secretpassword

# Mail
MAIL__USERNAME=reservium@buk.cvut.cz
MAIL__PASSWORD=exampleapp123
MAIL__FROM_NAME=Reservium System

# Keycloak
KEYCLOAK__SERVER_URL=https://auth.buk.cvut.cz
KEYCLOAK__REALM=reservium
KEYCLOAK__CLIENT_ID=reservium-api
KEYCLOAK__CLIENT_SECRET=supersecret

# SpiceDB
SPICEDB__CLIENT_SECRET=myspicedbsecret

# Google
GOOGLE__CLIENT_ID=example.apps.googleusercontent.com
GOOGLE__CLIENT_SECRET=example-secret

# Dormitory Access System
DORMITORY_ACCESS_SYSTEM__API_KEY=ABCDEFG1234567890
```

### 🔐 token.json Example

```token
{
  "token": "...",
  "refresh_token": "...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "...",
  "client_secret": "...",
  "scopes": ["https://www.googleapis.com/auth/calendar"],
  "expiry": "2025-12-31T23:59:59Z"
}
```

> This token enables Google Calendar integration and is refreshed automatically.

### ▶️ Running Reservium

**🚀 The system will automatically:**
- Start PostgreSQL
- Run database migrations
- Launch the backend API on port 8000
- Launch the frontend (if included) on port 3000

**You can access:**
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000