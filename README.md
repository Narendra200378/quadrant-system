# Quadrant Visitor Management System

A role-based visitor management application built for Quadrant Technologies. This repository combines a static multi-page frontend with an AWS serverless backend to manage visitor registration, Aadhaar upload, approval workflows, and gate access.

This project demonstrates:
- Multi-role UI design for `employee`, `admin`, and `security` users
- Serverless backend logic with AWS Lambda, API Gateway, DynamoDB, and S3
- Visitor lifecycle management from registration to entry and exit
- Secure Aadhaar document upload and retrieval with presigned S3 URLs
- Role-based dashboards and status management

## Table Of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [File Guide](#file-guide)
- [Architecture](#architecture)
- [Application Flow](#application-flow)
- [API Routes](#api-routes)
- [AWS Setup Guide](#aws-setup-guide)
- [Local Run Guide](#local-run-guide)
- [Deployment Notes](#deployment-notes)
- [Portfolio Highlights](#portfolio-highlights)
- [Current Limitations](#current-limitations)

## Overview

This system manages visitor access across three internal roles:

- `Employee`: registers visitors, uploads Aadhaar documents, and tracks visits
- `Admin`: reviews visitor requests, approves/rejects/reschedules, exports data, and manages users
- `Security`: validates arrivals, approves or rejects entry, and records exits

The frontend uses static HTML, CSS, and JavaScript. The backend uses a Python AWS Lambda function that interacts with DynamoDB and S3.

## Key Features

- Public landing page with role selection
- Employee registration form and Aadhaar upload
- Admin dashboard with visitor approvals, status controls, and user management
- Security dashboard for gate validation and exit tracking
- Presigned S3 upload and download flows for Aadhaar files
- Visitor statuses: `pending`, `approved`, `rejected`, `rescheduled`
- EmailJS notification support in dashboards

## Tech Stack

### Frontend

- HTML5
- CSS3
- JavaScript
- Google Fonts
- EmailJS browser SDK
- Tailwind CSS via CDN on dashboard pages

### Backend

- Python
- AWS Lambda
- Amazon API Gateway
- Amazon DynamoDB
- Amazon S3

## Project Structure

```text
QT project/
|-- Main.html
|-- Main Admin.html
|-- Main employee.html
|-- Main security.html
|-- lambda functions.py
|-- README.md
```

## File Guide

- `Main.html`: public landing page with role selection and company branding
- `Main Admin.html`: admin dashboard for visitor approvals and user management
- `Main employee.html`: employee portal for visitor registration, Aadhaar upload, and visit tracking
- `Main security.html`: security dashboard for arrival validation and exit management
- `lambda functions.py`: AWS Lambda backend with DynamoDB and S3 integrations

## Architecture

```text
Frontend Pages
  |-- Main.html
  |-- Main Admin.html
  |-- Main employee.html
  |-- Main security.html
          |
          v
AWS API Gateway
          |
          v
AWS Lambda (lambda functions.py)
          |
    -------------------------
    |                       |
    v                       v
DynamoDB                Amazon S3
Employees table         Aadhaar document storage
Visitors table
```

### Core AWS Resources Used

- DynamoDB table: `Employees`
- DynamoDB table: `Visitors`
- S3 bucket: `visitor-images-narendra`
- Lambda CORS origin: `https://visitor-management-frontend.s3.ap-south-1.amazonaws.com`

## Application Flow

### Employee Flow

1. Employee logs in with name and employee ID.
2. Employee registers a visitor with visit details.
3. Aadhaar document is uploaded to S3 using a presigned URL.
4. Visitor data is saved to DynamoDB.
5. Employee can view and reschedule visitor records.

### Admin Flow

1. Admin logs in with a registered admin account.
2. Admin reviews visitor requests and user records.
3. Admin approves, rejects, or reschedules visitors.
4. Admin can register internal users for employee and security roles.

### Security Flow

1. Security user logs in with valid credentials.
2. Security views visitor schedules and gate requests.
3. Security approves or rejects entry.
4. Security records exit time.
5. Security can view uploaded Aadhaar documents via presigned links.

## API Routes

The Lambda backend supports these routes:

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/user` | List registered users |
| `POST` | `/user` | Register a new internal user |
| `DELETE` | `/user` | Delete a user by `emp_id` |
| `GET` | `/visitors` | List visitor records |
| `GET` | `/admin` | List visitor records (alternate route) |
| `POST` | `/register` | Register a new visitor |
| `PUT` | `/register` | Reschedule an existing visit |
| `POST` | `/approve` | Update visitor status and in/out times |
| `GET` | `/upload-url` | Create presigned S3 upload URL |
| `GET` | `/aadhaar` | Create presigned S3 download URL |
| `GET` | `/presigned` | Alternate presigned download route |
| `POST` | `/aadhaar-key` | Save uploaded Aadhaar S3 key |

## AWS Setup Guide

### 1. Create DynamoDB Tables

#### `Employees`
- Partition key: `emp_id` (`String`)

Fields:
- `emp_id`
- `name`
- `role`

#### `Visitors`
- Partition key: `visitor_id` (`String`)

Fields used by the frontend:
- `visitor_id`
- `name`
- `aadhaar`
- `email`
- `date`
- `time`
- `purpose`
- `emp_name`
- `emp_id`
- `status`
- `rescheduled_date`
- `rescheduled_time`
- `aadhaar_key`
- `reg_time`
- `in_time`
- `out_time`

### 2. Create the S3 Bucket

The backend expects:

```text
visitor-images-narendra
```

If you use another bucket name, update `S3_BUCKET` in `lambda functions.py`.

Uploaded object key pattern:

```text
aadhaar/<visitor_id>.<ext>
```

### 3. Deploy the Lambda Function

- Runtime: Python 3.x
- Upload `lambda functions.py`
- Grant IAM permissions for DynamoDB and S3 operations

### 4. Configure API Gateway

Expose the following routes:
- `/user`
- `/visitors`
- `/admin`
- `/register`
- `/approve`
- `/upload-url`
- `/aadhaar`
- `/presigned`
- `/aadhaar-key`

Enable the required methods and `OPTIONS`.

### 5. Configure CORS

Current allowed origin:

```python
'Access-Control-Allow-Origin': 'https://visitor-management-frontend.s3.ap-south-1.amazonaws.com'
```

If your frontend is hosted elsewhere, update this origin in `lambda functions.py`.

### 6. Update Frontend API URL

Update the hardcoded API base URL in:
- `Main employee.html`
- `Main Admin.html`
- `Main security.html`

### 7. Configure EmailJS

The dashboards use EmailJS for notifications. To enable it:
1. Create an EmailJS account
2. Create a service/template
3. Replace keys/template IDs in the frontend
4. Test email notifications

## Local Run Guide

### Option 1: Open Directly

Open these files in a browser:
- `Main.html`
- `Main Admin.html`
- `Main employee.html`
- `Main security.html`

### Option 2: Serve Locally

```powershell
python -m http.server 8080
```

Then visit:
- `http://localhost:8080/Main.html`
- `http://localhost:8080/Main Admin.html`
- `http://localhost:8080/Main employee.html`
- `http://localhost:8080/Main security.html`

## Deployment Notes

### Frontend
- Deploy the HTML files to static hosting such as S3, Netlify, or GitHub Pages
- Update API base URLs to your live API gateway
- Match the frontend domain with Lambda CORS settings

### Backend
- Deploy Lambda behind API Gateway
- Ensure DynamoDB tables and S3 bucket exist
- Ensure Lambda has permissions to access DynamoDB and S3
- Keep the region consistent across resources

## Portfolio Highlights

Project strengths:
- Multi-role visitor management system for employee, admin, and security users
- Serverless backend using AWS Lambda, API Gateway, DynamoDB, and S3
- Presigned S3 upload/download for secure Aadhaar handling
- Dashboard interfaces with filters, analytics, and status controls
- End-to-end visitor lifecycle from registration to exit

Suggested resume bullet:

```text
Built a role-based visitor management system using HTML, JavaScript, AWS Lambda, API Gateway, DynamoDB, and S3, enabling secure visitor registration, approval workflows, Aadhaar document uploads, and operational dashboards for employee, admin, and security teams.
```

## Current Limitations

- Configuration is hardcoded in the frontend and Lambda scripts
- Authentication is client-side only and not production-grade
- CSS and JavaScript are embedded inline instead of separate assets
- No automated tests or CI/CD setup included
- Repository does not include screenshots or infrastructure-as-code
