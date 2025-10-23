# 🧠 Joby – Personalized Job Notification Platform

## 🌍 Overview

Joby is a full-stack job notification platform that allows users to create, manage, and receive personalized job alerts based on their preferences.
It consists of three coordinated components:

Frontend (React) – The user-facing interface for registration, login, and notification management.

Backend (FastAPI) – The main API that handles authentication, user data, and automated email notifications.

Jobs Engine (FastAPI) – A microservice that scrapes and aggregates job listings from Indeed and LinkedIn.

The platform enables users to:

Register and log in securely using JWT-based authentication.

Define job search rules (e.g., job title, location, frequency).

Automatically receive job listings by email daily, weekly, or monthly.

View and update personal information and notification preferences via an intuitive React interface.


Main Ports:

Frontend: 3000

Backend: 8001

Jobs Engine: 8002

# 🖥️ Joby Frontend

A React-based web application that serves as the user interface for the Joby platform.
It enables users to sign up, log in, manage their profiles, and create job notification rules.
The app interacts with the backend API for authentication, data persistence, and notification management.

✨ Features

🔐 Authentication: Sign up and login via JWT tokens.

⚙️ Profile Management: Edit name, email, and password.

📬 Job Notifications: Create, edit, and delete job notification rules.

🧭 Routing: Implemented using React Router for seamless navigation.

✅ Validation: Client-side form validation with backend error handling.

🎨 Styling: Tailwind-style utility classes for consistent UI design.

🌐 Configurable API URL: Uses environment variable REACT_APP_API_URL for backend connection.

### ⚙️ Prerequisites

Node.js (>= 14)

npm or yarn

Backend server running at http://localhost:8001 (by default)

##  Quick Start

1️⃣ Install dependencies:
```bash
npm install
```
### or
```bash
yarn
```

 2️⃣ Run development server:

```bash  
npm start
```
### or
```bash
yarn start
```

3️⃣ Build for production:
```bash
npm run build
```

4️⃣ Set environment variable (optional):

Windows PowerShell
```bash
$env:REACT_APP_API_URL = 'http://localhost:8001'; npm start
```

### 🌐 Environment Variables
Variable	Description	Default
REACT_APP_API_URL	Backend API URL	http://localhost:8001
🔗 Expected Backend Endpoints
Method	Endpoint	Description
POST	/signup	Register new user
POST	/login	Authenticate user
GET	/user/me	Retrieve user details
PUT	/user/me	Update user profile
POST	/user/me/password	Change password
GET	/notifications	Fetch all job notifications
POST	/notifications	Create a new notification rule
PUT	/notifications/:id	Update a notification rule
DELETE	/notifications/:id	Delete a notification rule

All authenticated requests must include:

Authorization: Bearer <token>

🎨 Styling and Design

The app uses Tailwind-like utility classes (without a full Tailwind dependency).
Colors and layout styles are defined inline or within reusable components.
For a consistent global theme, you can extract class names into a shared theme file.


🧪 Testing the Frontend

You can test the frontend locally after running the backend:

### Run backend on port 8001
```bash
uvicorn main:app --reload --port 8001
```
### Run frontend on port 3000
```bash
npm start
```

Once both are running, open http://localhost:3000
 in your browser.


📄 License

This project is open-source and available under the MIT License
.
