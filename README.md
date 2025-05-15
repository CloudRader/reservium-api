# BUK Reservation System

## Overview

**BUK Reservation System** is a web-based application designed to automate and streamline room reservations for the **Buben Student Club**. It simplifies the booking process for both users and managers by integrating with the club's internal information system (**IS.BUK**) and Google Calendar. This allows automatic user data retrieval and real-time calendar synchronization.

* **Production API documentation**: [api.reservation.buk.cvut.cz/docs](https://api.reservation.buk.cvut.cz/docs)
* **Development API documentation**: [api.develop.reservation.buk.cvut.cz/docs](https://api.develop.reservation.buk.cvut.cz/docs)

---

## Running the Application Locally 🛫

### 1. Environment Configuration

First, create and configure a `.env.secret` file inside the `app/` directory. Below is an example with test credentials:

```ini
SECRET_KEY=ee8f822eeb5166d09ffc55b43c4a1d55c4a7725df56d540789b5fd0f2ffbdb07
DORMITORY_ACCESS_SYSTEM_API_KEY=E73C6B0794A6E69BD125CFAF98327BFBF6719A1E9BD87F2A4D1ACB41F9E45F30

CLIENT_ID=**YOUR_CLIENT_ID**
CLIENT_SECRET=**YOUR_CLIENT_SECRET**
REDIRECT_URI=https://**YOUR_PUBLIC_IP**:8000/users/callback

IS_SCOPES=http://is.buk.dev.buk.cvut.cz:3000/api/v1
IS_OAUTH_TOKEN=http://is.buk.dev.buk.cvut.cz:3000/oauth/token
IS_OAUTH=http://is.buk.dev.buk.cvut.cz:3000/oauth

GOOGLE_SCOPES=https://www.googleapis.com/auth/calendar
GOOGLE_CLIENT_ID=932482201036-gqfrbee9mk3rqd4ntb2v3sm11hnd2ii4.apps.googleusercontent.com
GOOGLE_PROJECT_ID=reservationsystemdevbuk
GOOGLE_CLIENT_SECRET=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

MAIL_USERNAME=develop@buk.cvut.cz
MAIL_PASSWORD=bxmeypdhtjocmweb
```

Next, create a `token.json` file inside `app/app/` with a test token:

```json
{
  "token": "...",
  "refresh_token": "...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "...",
  "client_secret": "...",
  "scopes": ["https://www.googleapis.com/auth/calendar"],
  "expiry": "2025-05-12T11:10:23.924400Z"
}
```

> This token will be automatically refreshed. It must be present initially to start the app.

---

### 2. Obtaining OAuth Credentials from IS.BUK

To retrieve your `CLIENT_ID`, `CLIENT_SECRET`, and `REDIRECT_URI`:

1. Go to [IS.BUK Dev](http://is.buk.dev.buk.cvut.cz:3000)
2. Log in with the test user:
   `Username`: `test.head`
   `Password`: `testheadbuk`
3. Navigate to: **System → OAuth API applications**
4. Create a new application:

   * **Name**: Any identifiable name
   * **Callback URL**: `https://<your-public-ip>:8000/users/callback`
   * **Manager**: Assign `test.head`
5. After creation, you will receive your `CLIENT_ID` and `CLIENT_SECRET`.

> ⚠️ **Make sure your IP is public and accessible**, as IS.BUK must be able to send callbacks to it.

---

### 3. Local SSL Configuration (for development only)

In `app/app/main.py`, enable SSL for local testing by:

```python
# Add to the top of the file
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Uncomment these lines at the bottom 
ssl_keyfile="certification/key.pem",
ssl_certfile="certification/cert.pem"
```

---

### 4. Running the Application with Docker

1. Start the containers:

```bash
docker compose up
```

2. Open a shell inside the backend container:

```bash
docker compose exec backend bash
```

3. Inside the container:

```bash
source /venv/bin/activate
cd app/
alembic upgrade head  # Run latest DB migrations
```

4. Optional scripts:

```bash
./scripts/run_tests.sh     # Run tests
./scripts/pylint.sh        # Run Pylint
./scripts/mypy.sh          # Run MyPy
```

> ⚠️ **These scripts may not run properly inside the container. It’s recommended to execute them locally.**
> 
> If you previously uncommented any code for container testing, consider commenting it back.

---

## API Testing

To test the API:

1. Visit: `https://<your-public-ip>:8000/docs`
2. Authenticate using the test endpoint:

```http
POST /users/login_dev
```

Use one of the following test accounts:

| Username       | Password         | Role Description                               |
| -------------- | ---------------- | ---------------------------------------------- |
| `test.user`    | `testuserbuk`    | Regular user                                   |
| `test.manager` | `testmanagerbuk` | User with manager-level permissions            |
| `test.active`  | `testactivebuk`  | Active member with extended privileges         |
| `test.head`    | `testheadbuk`    | Superuser with access to all IS.BUK operations |

After login, revisit the `/docs` page to use the API with proper authorization headers.

> 🚨 If SSL-related issues occur locally, try using `http://` instead of `https://`.

---

## Testing with Frontend UI

* Development frontend: [develop.reservation.buk.cvut.cz](https://develop.reservation.buk.cvut.cz)
* Development backend API: [api.develop.reservation.buk.cvut.cz/docs](https://api.develop.reservation.buk.cvut.cz/docs)

You can log in using test users listed above.

> ⚠️ Note: The local database is independent from the development server's database. Test data does not sync across environments.

* Production frontend: [reservation.buk.cvut.cz](https://reservation.buk.cvut.cz)
* Production backend API: [api.reservation.buk.cvut.cz/docs](https://api.reservation.buk.cvut.cz/docs)

> ⚠️ You must be a registered club member with a real IS.BUK account to use the production system.

---

## Code Quality Tools

### ✉️ Pylint

Run static code quality checks:

```bash
chmod -x ./scripts/pylint.sh  # Optional: remove executable bit
./scripts/pylint.sh
```

### 💡 MyPy

Run type checks:

```bash
chmod -x ./scripts/mypy.sh  # Optional
./scripts/mypy.sh
```

### ✅ Pytest

Run the test suite:

```bash
chmod -x ./scripts/run_tests.sh  # Optional
./scripts/run_tests.sh
```

---

## Notes

* The application uses **FastAPI** and **PostgreSQL**.
* Testcontainers are used for isolated database testing.
* All Docker services are defined in `docker-compose.yml`.
* SSL certificates are configured in `certification/`, used only for local development.

---

