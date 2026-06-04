# ScanX Voice Calling Service

## Overview

ScanX Voice Calling Service is a FastAPI-based application that enables clinic staff to initiate patient phone calls directly from Google Chat appointment notifications.

The application integrates:

* Google Chat Cards
* Twilio Programmable Voice
* Twilio Voice JavaScript SDK
* Cloud SQL PostgreSQL
* Google Cloud Run

The goal is to provide a one-click calling experience for clinic staff while maintaining a consistent ScanX caller identity for patients.

---

# Architecture

```text
Google Chat Card
       │
       ▼
Call Patient Button
       │
       ▼
FastAPI Backend
       │
       ▼
Twilio Voice SDK
       │
       ▼
Browser / Clinic Tablet
       │
       ▼
Patient Phone
```

---

# Features

* One-click patient calling from Google Chat
* Direct calling from clinic tablets
* No staff personal phone numbers exposed
* Centralized ScanX caller ID
* Cloud SQL appointment lookup
* Call logging
* Cloud Run deployment
* Secure token validation
* Browser-based calling interface
* Automatic call initiation
* Automatic window close after call completion

---

# Technology Stack

## Backend

* FastAPI
* SQLAlchemy
* PostgreSQL
* Twilio SDK
* Python

## Frontend

* Twilio Voice JavaScript SDK
* HTML
* JavaScript

## Cloud

* Google Cloud Run
* Cloud SQL PostgreSQL
* Cloud Build
* Artifact Registry
* Secret Manager

---

# Project Structure

```text
Twilio_Gchat_calling_backend/

├── app.py
├── config.py
├── database.py
├── models.py
├── requirements.txt
├── Procfile
├── .env
├── .env.example
├── .gcloudignore
├── .gitignore
│
├── routes/
│   └── voice.py
│
└── static/
```

---

# Environment Variables

Create a `.env` file locally.

Example:

```env
# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Voice SDK
TWILIO_API_KEY_SID=SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_TWIML_APP_SID=APxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Caller ID
TWILIO_PHONE_NUMBER=+1XXXXXXXXXX

# Application
BASE_URL=https://your-cloud-run-url.run.app
CALL_BUTTON_SECRET=ScanX50

# Database
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=scanx_app
DB_HOST=127.0.0.1
DB_PORT=5432

# Cloud Run Only
INSTANCE_CONNECTION_NAME=project:region:instance
```

---

# Environment Variables Explained

| Variable                 | Purpose                                    |
| ------------------------ | ------------------------------------------ |
| TWILIO_ACCOUNT_SID       | Twilio Account Identifier                  |
| TWILIO_AUTH_TOKEN        | Twilio Authentication Token                |
| TWILIO_API_KEY_SID       | Twilio Voice SDK API Key                   |
| TWILIO_API_KEY_SECRET    | Twilio Voice SDK API Secret                |
| TWILIO_TWIML_APP_SID     | Twilio TwiML Application                   |
| TWILIO_PHONE_NUMBER      | Caller ID shown to patients                |
| BASE_URL                 | Public application URL                     |
| CALL_BUTTON_SECRET       | Security token used by Google Chat buttons |
| DB_USER                  | PostgreSQL username                        |
| DB_PASSWORD              | PostgreSQL password                        |
| DB_NAME                  | Database name                              |
| DB_HOST                  | Database host                              |
| DB_PORT                  | Database port                              |
| INSTANCE_CONNECTION_NAME | Cloud SQL instance connection              |

---

# Local Development

## Create Virtual Environment

```bash
python -m venv env
```

Activate:

### Windows

```bash
env\Scripts\activate
```

### Linux/Mac

```bash
source env/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Application

```bash
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

Application:

```text
http://localhost:5000
```

Health Check:

```text
http://localhost:5000/health
```

---

# Cloud SQL Connection

Local development uses:

```text
Cloud SQL Auth Proxy
```

Start Proxy:

```bash
cloud-sql-proxy PROJECT:REGION:INSTANCE --port 5432
```

Example:

```bash
cloud-sql-proxy vernal-maker-473121-k4:us-central1:scanx-postgres-db --port 5432
```

---

# Cloud Run Deployment

## Enable Required APIs

```bash
gcloud services enable \
run.googleapis.com \
cloudbuild.googleapis.com \
artifactregistry.googleapis.com \
sqladmin.googleapis.com
```

---

## Deploy

```bash
gcloud run deploy scanx-voice-calling \
--source . \
--region us-central1 \
--allow-unauthenticated \
--add-cloudsql-instances vernal-maker-473121-k4:us-central1:scanx-postgres-db
```

Windows CMD:

```cmd
gcloud run deploy scanx-voice-calling --source . --region us-central1 --allow-unauthenticated --add-cloudsql-instances vernal-maker-473121-k4:us-central1:scanx-postgres-db
```

---

# Required IAM Permissions

## Deployment User

### roles/run.sourceDeveloper

Required to deploy source code directly to Cloud Run.

### roles/serviceusage.serviceUsageConsumer

Allows use of Google Cloud APIs required during deployment.

### roles/iam.serviceAccountUser

Allows deploying Cloud Run services using a runtime service account.

---

## Runtime Service Account

### roles/cloudsql.client

Allows Cloud Run to connect securely to Cloud SQL PostgreSQL.

### roles/secretmanager.secretAccessor

Allows application access to secrets stored in Secret Manager.

---

## Cloud Build

### roles/run.builder

Allows Cloud Build to build and deploy Cloud Run revisions.

---

# Database

## Appointment Table

The application reads appointment data from:

```sql
appointment
```

Expected fields:

```sql
appointment_id
first_name
last_name
phone
email
appointment_type
date
time
calendar
status_label
```

---

# Twilio Setup

## Create API Key

Twilio Console

```text
Account
 └── API Keys & Tokens
```

Create:

```text
Standard API Key
```

---

## Create TwiML App

Twilio Console

```text
Voice
 └── TwiML Apps
```

Voice Request URL:

```text
https://YOUR_CLOUD_RUN_URL/voice/outgoing
```

Method:

```text
POST
```

---

# Google Chat Integration

Example button:

```json
{
  "buttonList": {
    "buttons": [
      {
        "text": "📞 Call Patient",
        "onClick": {
          "openLink": {
            "url": "https://YOUR_CLOUD_RUN_URL/call-page?appointmentId={{APPOINTMENT_ID}}&token=ScanX50"
          }
        }
      }
    ]
  }
}
```

---

# Call Flow

```text
Staff clicks button
        │
        ▼
Google Chat
        │
        ▼
/call-page
        │
        ▼
Twilio Voice SDK
        │
        ▼
Browser microphone
        │
        ▼
/voice/outgoing
        │
        ▼
Patient phone
```

---

# Security

* Patient phone numbers never exposed to browser
* Appointment lookup performed server-side
* Secure token validation
* Environment variables not committed to source control
* Optional Secret Manager integration

---

# Troubleshooting

## Invalid Token

Verify:

```env
CALL_BUTTON_SECRET=ScanX50
```

Matches Google Chat URL token.

---

## Database Connection Timeout

Verify:

```text
Cloud SQL Auth Proxy running
```

or

```text
Cloud Run has Cloud SQL connection configured
```

---

## Twilio Application Error

Verify:

```text
Twilio TwiML App URL
```

Points to:

```text
https://YOUR_CLOUD_RUN_URL/voice/outgoing
```

---

## Cloud Run Deployment Failure

Verify APIs enabled:

```text
run.googleapis.com
cloudbuild.googleapis.com
artifactregistry.googleapis.com
sqladmin.googleapis.com
```

---

# Future Enhancements

* Multi-clinic routing
* Call recording management
* Call analytics dashboard
* Audit logging
* Role-based access control
* Browser notifications
* WebRTC call queues
* Automatic call dispositioning

---

# Author

ScanX Health LLC

Voice Calling Platform powered by:

* FastAPI
* Twilio Programmable Voice
* Google Cloud Platform
