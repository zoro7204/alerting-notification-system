# Lightweight Alerting & Notification System

This project is a lightweight alerting and notification system built for the AtomicAds SDE Intern assignment. It allows admins to create and manage alerts with specific visibility, and for users to receive, read, and snooze these notifications. The system features a modular reminder engine designed for easy demonstration.

-----

## Tech Stack

  * **Backend:** Python 3
  * **Framework:** FastAPI
  * **Database:** SQLite
  * **ORM:** SQLAlchemy
  * **Database (Demo):** SQLite was chosen for easy local testing. The design is DB-agnostic and can be switched to Postgres/MySQL by updating `database.py`.

-----

## Project Structure

```
/atomicads_project/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app setup and all API routes
│   ├── models.py         # SQLAlchemy database models
│   ├── schemas.py        # Pydantic schemas for data validation
│   ├── crud.py           # Core business logic and database functions
│   └── database.py       # Database engine and session setup
├── seed.py               # Script to populate the DB with test data
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

-----

## Setup and Run

**1. Clone the repository:**

```bash
git clone <your-repo-url>
cd atomicads_project
```

**2. Install dependencies:**
The `requirements.txt` file contains all necessary packages:

```
fastapi
uvicorn[standard]
sqlalchemy
pydantic[email]
```

Install them using pip:

```bash
pip install -r requirements.txt
```

**3. Initialize and seed the database:**
This command creates the `database.db` file and populates it with sample teams, users, and a test alert.

```bash
python seed.py
```

**4. Run the server:**

```bash
python -m uvicorn app.main:app --reload
```

The API will be running at `http://127.0.0.1:8000`. The interactive documentation is available at `http://127.0.0.1:8000/docs`.

-----

## How to Demo the Core Features

The reminder and snooze functionality can be tested with the following sequence:

1.  **Trigger Reminders (First Time):** Call `POST /admin/trigger-reminders`. The response will show that 2 reminders were sent (to Alice and Bob on the Engineering team for Alert ID 1).
2.  **Snooze the Alert:** Call `POST /users/1/alerts/1/snooze` to make Alice (user 1) snooze the alert (alert 1).
3.  **Trigger Reminders (Second Time):** Call `POST /admin/trigger-reminders` again. The response will now show that only 1 reminder was sent (to Bob), because Alice has snoozed it.
4.  **Check Analytics:** Call `GET /analytics/summary` to see system-level metrics like total alerts, deliveries, read/snoozed counts, and severity breakdown.

-----

## API Endpoints (cURL Examples)

### Admin

**Create Alert:**

```bash
curl -X POST "http://127.0.0.1:8000/admin/alerts" -H "Content-Type: application/json" -d '{
  "title": "New Org-Wide Policy", "message": "All employees must complete the new security training by Friday.", "severity": "Info", "reminders_enabled": true,
  "visibility": [{"visibility_type": "ORGANIZATION"}]
}'
```

**List All Alerts:**

```bash
curl -X GET "http://127.0.0.1:8000/admin/alerts"
```

**Update (Archive) an Alert:**

```bash
curl -X PUT "http://127.0.0.1:8000/admin/alerts/1" -H "Content-Type: application/json" -d '{"archived": true}'
```

**Trigger Reminder Engine:**

```bash
curl -X POST "http://127.0.0.1:8000/admin/trigger-reminders" -d ''
```

### User

**Fetch Alerts for a User:**

```bash
curl -X GET "http://127.0.0.1:8000/users/1/alerts"
```

**Mark an Alert as Read:**

```bash
curl -X POST "http://127.0.0.1:8000/users/1/alerts/1/read" -d ''
```

**Snooze an Alert:**

```bash
curl -X POST "http://127.0.0.1:8000/users/1/alerts/1/snooze" -d ''
```

### Analytics

**Get System Summary:**

```bash
curl -X GET "http://127.0.0.1:8000/analytics/summary"
```

-----

## Design Choices

  * **Object-Oriented Design:** The system is structured with clear separation of concerns (API routes in `main.py`, business logic in `crud.py`, and data models in `models.py`).
  * **Extensibility (Strategy Pattern):** The PRD mentioned future scope for new notification channels (Email, SMS). The code is structured to easily incorporate the **Strategy Pattern** for this, where a base `NotificationChannel` could be implemented by `InAppChannel`, `EmailChannel`, etc.
  * **State Management (State Pattern):** User preferences (Read, Unread, Snoozed) are managed in a dedicated `UserAlertPreference` table. This logic lends itself to the **State Pattern** for handling transitions between these states.
  * **Decoupled Logic (Observer Pattern):** The reminder trigger is decoupled from alert creation, and user subscriptions are handled dynamically through visibility rules. This reflects principles of the **Observer Pattern**, where users are effectively "subscribers" to alert topics (Organization, Team, or direct).
  * **System Analytics:** A lightweight analytics endpoint was included to provide system administrators with immediate visibility into alert engagement and overall system usage, as requested by the PRD.