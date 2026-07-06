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

The complete REST surface (10 blueprints, 40+ endpoints) is documented in the project report (`Report_BelarusTourism.docx`, Appendix B).

## Capturing Report Screenshots

The internship report expects screenshots of every page. Use the bundled Playwright script to capture them all in one go:

```bash
pip install playwright
playwright install chromium
# In one terminal: cd backend && python app.py
# In another:       python take_screenshots.py
```

The script writes 12 PNGs into `screenshots/` covering the home page, attractions list (with category dropdown), attraction detail, login, the logged-in navigation bar showing the username and avatar, recommendations, articles list/detail/write, Q&A, profile, and the admin dashboard.

## Screenshot Checklist (manual)

If you prefer to capture screenshots by hand, this is the minimum list required for the report:

1. Home page (hero + featured attractions + recent reviews).
2. Attractions listing with the **Category** dropdown open.
3. Attraction detail page with the AI sentiment badge and the predicted-rating widget.
4. Login page.
5. Home page **after** a successful login, showing the username and avatar in the navigation bar.
6. Recommendations page with personalised results.
7. Articles list.
8. Article detail.
9. Article-write form.
10. Q&A list and a single Q&A thread.
11. Profile page (avatar, my reviews, my ratings tabs).
12. Admin dashboard with platform statistics and moderation controls.

Always capture in English locale (set the browser language to English).
