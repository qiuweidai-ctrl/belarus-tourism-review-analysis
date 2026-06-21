# Belarus Tourism Review & Analysis System

A Flask + Vue 3 web application for Belarus tourism attractions with AI-powered sentiment analysis and personalized recommendations.

## Tech Stack

- **Backend**: Flask, Flask-SQLAlchemy, Flask-JWT-Extended, SQLite
- **Frontend**: Vue 3, Vue Router, vue-i18n, Axios, Pinia
- **AI**: DeepSeek API (sentiment analysis & recommendation)
- **UI**: Custom CSS with responsive design

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
python init_db.py   # Initialize database with sample data
python app.py       # Start server on http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
npm run dev        # Start dev server on http://localhost:3000
```

## Default Accounts

| Username | Password  | Role  |
|----------|-----------|-------|
| admin    | admin123  | admin |
| demo     | demo123   | user  |

## Features

- User registration and login (JWT auth)
- Attraction browsing, search, and filtering
- Write and view reviews
- AI sentiment analysis on reviews (DeepSeek API)
- AI-powered personalized recommendations
- Rating prediction based on user history
- English interface (i18n ready)
- Responsive design

## API Endpoints

- `POST /api/auth/register` - Register
- `POST /api/auth/login` - Login
- `GET /api/attractions` - List attractions
- `GET /api/attractions/:id` - Attraction detail
- `POST /api/attractions` - Create attraction (admin)
- `GET/POST /api/reviews` - List/create reviews
- `GET /api/recommendations` - Get personalized recommendations
- `POST /api/recommendations/predict-rating` - Predict rating
