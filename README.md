# Joby (Frontend)

A React application for creating and managing personalized job notifications.
This frontend was scaffolded with Create React App and uses React Router for navigation. The app expects a backend API (by default at http://localhost:8001) for authentication, user profile, and notification persistence.

## Features
- Sign up / login
- Create, edit and delete job notification rules
- Profile editing (name, email) and password change
- Client-side forms with validation and backend error handling

## Prerequisites
- Node.js (>= 14)
- npm or yarn
- A backend server running (default expected at http://localhost:8001). See "API" section for expected endpoints.

## Quick start

1. Install dependencies

```bash
npm install
# or: yarn
```

2. Run development server

```bash
npm start
# or: yarn start
```

3. Build for production

```bash
npm run build
```

## Environment
- The frontend will use the `REACT_APP_API_URL` env variable if set. By default it calls `http://localhost:8001`.

Example (Windows PowerShell):

```powershell
$env:REACT_APP_API_URL = 'http://localhost:8001'; npm start
```

## Expected backend API 
The frontend expects these endpoints (adjust `src/utils/mockApi.js` if your API differs):

- POST /signup -> { token, user }
- POST /login -> { token, user }
- GET /user/me -> { user }
- PUT /user/me -> updated user
- POST /user/me/password -> { success }
- GET /notifications -> [ ...notifications ]
- POST /notifications -> created notification
- PUT /notifications/:id -> updated notification
- DELETE /notifications/:id -> 204 / { success }

All authenticated requests must include `Authorization: Bearer <token>` header.


## Styling
The app uses Tailwind-like utility classes. Colors/palette are set inline on components; if you want a global theme, extract class names to a central theme file.


