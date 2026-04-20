# Quadrant Visitor Management System

A role-based visitor management application built for Quadrant Technologies. The project combines a static multi-page frontend with an AWS serverless backend to handle visitor registration, employee/admin/security workflows, status tracking, and Aadhaar document upload and retrieval.

This repository is a strong portfolio-style full-stack project because it demonstrates:
- Multi-role UI design for `employee`, `admin`, and `security` users
- CRUD-style backend flows with AWS Lambda, API Gateway, DynamoDB, and S3
- Real-world visitor lifecycle management from registration to entry and exit
- Document upload using presigned S3 URLs
- Dashboard-style analytics, filtering, export, and operational workflows

## Table Of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Architecture](#architecture)
- [Application Flow](#application-flow)
- [API Routes](#api-routes)
- [AWS Setup Guide](#aws-setup-guide)
- [Local Run Guide](#local-run-guide)
- [Deployment Notes](#deployment-notes)
- [Portfolio Highlights](#portfolio-highlights)
- [Current Limitations](#current-limitations)
- [Future Improvements](#future-improvements)
- [License](#license)

## Overview

The system is designed to manage office visitor entries in a structured way across three internal roles:

- `Employee` users register visitors, upload Aadhaar documents, and reschedule visits
- `Admin` users monitor all visitor records, approve or reject requests, export data, and manage registered users
- `Security` users validate arrivals, allow or reject visitors at the gate, and mark exits

The frontend is built as static HTML pages with embedded CSS and JavaScript, while the backend logic is implemented in an AWS Lambda function that reads and writes data to DynamoDB and stores uploaded files in S3.

## Key Features

- Public landing page with role-based access entry
- Employee-side visitor registration form
- Aadhaar upload using S3 presigned URLs
- Visitor ID generation and tracking
- Admin dashboard with search, filtering, analytics, and CSV export
- Security dashboard for entry approval and exit management
- Reschedule workflow for existing visits
- Role-based login checks against the users table
- Visitor status flow including `pending`, `approved`, `rejected`, and `rescheduled`
- Presigned document viewing for uploaded Aadhaar files
- Email notification integration via EmailJS in the frontend

## Tech Stack

### Frontend

- HTML5
- CSS3
- JavaScript
- Tailwind CSS via CDN
- Google Fonts
- EmailJS browser SDK

### Backend

- Python
- AWS Lambda
- Amazon API Gateway
- Amazon DynamoDB
- Amazon S3
- `boto3`

## Project Structure

```text
QT project/
|-- index.html
|-- Main.html
|-- employee.html
|-- admin.html
|-- security.html
|-- test1.html
|-- lambda functions.py
|-- README.md
```

### File Guide

- `index.html`: public landing page with company branding and sign-in modal
- `Main.html`: alternate role-selection style landing page
- `employee.html`: employee portal to register visitors and manage recent entries
- `admin.html`: admin operations dashboard with filters, approvals, exports, and user registration
- `security.html`: security gate dashboard for live visitor validation
- `test1.html`: older experimental dashboard connected to a different API base URL
- `lambda functions.py`: AWS Lambda backend for all main API routes

## Screenshots

You asked to include this section, so the README is ready for it. If you add images to a `screenshots/` folder, these links will work immediately.

Suggested screenshot files:
- `screenshots/landing-page.png`
- `screenshots/employee-portal.png`
- `screenshots/admin-dashboard.png`
- `screenshots/security-dashboard.png`

Example markdown you can keep or replace later:

```md
![Landing Page](screenshots/landing-page.png)
![Employee Portal](screenshots/employee-portal.png)
![Admin Dashboard](screenshots/admin-dashboard.png)
![Security Dashboard](screenshots/security-dashboard.png)
```

Recommended screenshots to capture:
- Landing page hero section
- Employee visitor registration form
- Admin visitor table with filters and analytics cards
- Security dashboard showing approvals and exit flow

## Architecture

```text
Frontend Pages
  |-- index.html / Main.html
  |-- employee.html
  |-- admin.html
  |-- security.html
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
- API base URL used in the main dashboards:
  `https://4ropzko5m1.execute-api.ap-south-1.amazonaws.com`

## Application Flow

### Employee Flow

1. Employee logs in with name and employee ID.
2. Employee registers a visitor with personal and visit details.
3. Optional Aadhaar file is uploaded to S3 using a presigned upload URL.
4. Visitor record is saved in DynamoDB through the Lambda API.
5. Employee can view registered visitors and reschedule visits.

### Admin Flow

1. Admin logs in using a registered admin account.
2. Admin reviews all visitors from the database.
3. Admin approves, rejects, reschedules, or exports visitor data.
4. Admin can also register internal users for `employee` and `security` roles.

### Security Flow

1. Security user logs in with valid credentials.
2. Security views visitors scheduled for the day or selected period.
3. Security allows or rejects arrivals.
4. Security marks exit time after visit completion.
5. Security can inspect uploaded Aadhaar documents using presigned access URLs.

## API Routes

The backend Lambda currently supports the following routes:

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/user` | List registered users |
| `POST` | `/user` | Register a new internal user |
| `DELETE` | `/user` | Delete a user by `emp_id` |
| `GET` | `/visitors` | List all visitor records |
| `GET` | `/admin` | Alternate route returning visitor records |
| `POST` | `/register` | Register a new visitor |
| `PUT` | `/register` | Reschedule an existing visit |
| `POST` | `/approve` | Update visitor status and save in/out times |
| `GET` | `/upload-url` | Generate presigned S3 upload URL |
| `GET` | `/aadhaar` | Generate presigned S3 download URL |
| `GET` | `/presigned` | Alternate Aadhaar download route |
| `POST` | `/aadhaar-key` | Save uploaded S3 object key to DynamoDB |

## AWS Setup Guide

This section gives you a practical path to recreate the backend environment.

### 1. Create DynamoDB Tables

Create these two tables:

#### `Employees`

- Partition key: `emp_id` as `String`

Suggested attributes stored by the app:
- `emp_id`
- `name`
- `role`

Example items:

```json
{
  "emp_id": "EMP001",
  "name": "Narendra",
  "role": "employee"
}
```

```json
{
  "emp_id": "ADM001",
  "name": "Admin User",
  "role": "admin"
}
```

```json
{
  "emp_id": "SEC001",
  "name": "Security User",
  "role": "security"
}
```

#### `Visitors`

- Partition key: `visitor_id` as `String`

Common fields used by the frontend:
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

### 2. Create S3 Bucket

Create an S3 bucket for Aadhaar uploads. The code currently expects:

```text
visitor-images-narendra
```

If you use a different bucket name, update the `S3_BUCKET` constant in `lambda functions.py`.

Stored object key pattern:

```text
aadhaar/<visitor_id>.<ext>
```

### 3. Create The Lambda Function

- Runtime: Python 3.x
- Upload the code from `lambda functions.py`
- Attach an IAM role with permissions for:
  - `dynamodb:GetItem`
  - `dynamodb:PutItem`
  - `dynamodb:UpdateItem`
  - `dynamodb:DeleteItem`
  - `dynamodb:Scan`
  - `s3:GetObject`
  - `s3:PutObject`

### 4. Configure API Gateway

Expose the Lambda function through API Gateway routes that match the frontend:

- `/user`
- `/visitors`
- `/admin`
- `/register`
- `/approve`
- `/upload-url`
- `/aadhaar`
- `/presigned`
- `/aadhaar-key`

Enable `GET`, `POST`, `PUT`, `DELETE`, and `OPTIONS` as needed.

### 5. Configure CORS

The Lambda currently uses a fixed allowed origin:

```python
'Access-Control-Allow-Origin': 'https://visitor-management-frontend.s3.ap-south-1.amazonaws.com'
```

If your frontend is hosted somewhere else, update the CORS origin in the Lambda code.

### 6. Update Frontend API Base URL

The HTML dashboards contain hardcoded API endpoints. If your deployed API changes, update the `API_BASE` or `BASE_URL` constants in:

- `employee.html`
- `admin.html`
- `security.html`
- `test1.html`

### 7. Configure EmailJS

The employee and admin flows reference EmailJS for notifications. To make email work:

1. Create an EmailJS account
2. Create the service and templates you need
3. Replace the hardcoded EmailJS keys or template IDs in the frontend files
4. Test new registration and reschedule email flows

## Local Run Guide

This project has no build step and no package installation step.

### Option 1: Open Directly

You can open the static pages directly in a browser:

```powershell
start index.html
```

### Option 2: Serve With A Simple Static Server

```powershell
python -m http.server 8080
```

Then open:

- `http://localhost:8080/index.html`
- `http://localhost:8080/Main.html`
- `http://localhost:8080/employee.html`
- `http://localhost:8080/admin.html`
- `http://localhost:8080/security.html`

## Deployment Notes

### Frontend Deployment

- Deploy the HTML files to Amazon S3 static hosting, Netlify, GitHub Pages, or another static host
- Make sure the API base URL constants point to your live API Gateway endpoint
- Match the frontend domain with the Lambda CORS configuration

### Backend Deployment

- Deploy the Lambda behind API Gateway
- Ensure the DynamoDB tables exist with the expected partition keys
- Ensure the S3 bucket exists and the Lambda IAM role can access it
- Keep the region consistent with your deployed bucket and API Gateway

## Portfolio Highlights

If you are using this project in a resume, LinkedIn, or portfolio, these are the strongest talking points:

- Built a multi-role visitor management system supporting employee, admin, and security workflows
- Designed and integrated a serverless backend using AWS Lambda, API Gateway, DynamoDB, and S3
- Implemented presigned S3 upload and download flows for secure visitor document handling
- Developed dashboard interfaces with filtering, analytics cards, CSV export, and status management
- Created an end-to-end visit lifecycle covering registration, approval, rejection, rescheduling, entry, and exit
- Integrated email notifications for visitor communication workflows

Suggested resume bullet:

```text
Built a role-based visitor management system using HTML, JavaScript, AWS Lambda, API Gateway, DynamoDB, and S3, enabling visitor registration, approval workflows, Aadhaar document uploads, and operational dashboards for employee, admin, and security teams.
```

## Current Limitations

- Configuration is hardcoded across multiple HTML files and the Lambda script
- Authentication is client-side and should not be considered production-grade security
- `test1.html` uses a different API endpoint than the main dashboards
- CSS and JavaScript are embedded inline rather than split into reusable assets
- There is no automated testing or CI setup in the repository
- The repository currently does not include screenshots or infrastructure-as-code

## Future Improvements

- Move shared constants into a central configuration file
- Replace client-side login checks with secure authentication and authorization
- Split inline CSS and JavaScript into separate files
- Add Terraform, AWS SAM, or CloudFormation for infrastructure setup
- Add a `.gitignore`, deployment scripts, and environment-based config management
- Add screenshot assets for a stronger GitHub presentation
- Add audit logging and better role-based permission controls
- Add pagination and server-side filtering at the API layer

## License

No license file is currently included in this repository.
