# Belarus Tourism Review & Analysis System

A Flask + Vue 3 web application for Belarus tourism attractions with AI-powered sentiment analysis and personalized recommendations.

## Tech Stack

- **Backend**: Flask, Flask-SQLAlchemy, Flask-JWT-Extended, MySQL 8
- **Frontend**: Vue 3, Vue Router, vue-i18n, Axios, Pinia
- **AI**: DeepSeek API (sentiment analysis & recommendation)
- **UI**: Custom CSS with responsive design

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
python update_database.py
python app.py
```

The default local connection is `root:123456@localhost:3306/belarus_tourism`.
Set `SQLALCHEMY_DATABASE_URI` in the environment to use a different MySQL
account or host. `update_database.py` creates missing tables, adds the bundled
attraction data, and fills missing sample ratings without deleting existing
user data. It is safe to run again after an update. The API runs at
`http://localhost:5000`.

### Add Attraction Data

The Wikidata importer adds new English attraction records without changing
the existing records:

```bash
cd backend
python scrape_wikidata.py --limit 100 --new-only --output scraped_data.json
python enrich_attractions.py
```

The importer skips duplicate names and incomplete records, downloads available
Wikimedia Commons images, and stores local image paths in the database. The
enrichment step fills the remaining approved images and adds demo reviews to
new attractions that do not have a rating yet.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

On Windows PowerShell, use `npm.cmd run dev` if script execution policy blocks
`npm.ps1`. The development site runs at `http://localhost:3000` and proxies API
requests to Flask.

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

## Frontend Pages and Role Guide

The entire user interface is presented in English. This section explains the
purpose of every frontend page and the operations available to each role.

### Shared Interface

- The sidebar groups navigation under `Overview`, `Explore`, `Analytics`,
  `Community`, `My Trip`, and `Administration`.
- The header search opens the attraction list and searches by attraction name
  or city.
- The sun and moon button switches between light and dark themes.
- The sidebar can be collapsed on desktop and becomes a drawer on mobile.
- After login, the header displays the user's avatar, name, role, and logout
  button.
- `For You` and `My Profile` are available to signed-in users. `Admin Panel` is
  available only to moderators and administrators.

### Roles and Permissions

| Role | Available areas | Main operations |
|---|---|---|
| Guest | Dashboard, attractions, map, rankings, comparison, insights, word clouds, articles, questions, and itinerary | Browse and search data, read reviews and articles, create a local itinerary, register, or log in |
| User (`user`) | Guest pages plus recommendations, wishlist, and profile | Save attractions, create or delete personal reviews, like and comment on articles, manage personal articles, ask questions, edit the profile, and inspect login history |
| Moderator (`moderator`) | User pages plus the administration area | Manage user status, moderate reviews, feature attractions, inspect login events, and run algorithm tools |
| Administrator (`admin`) | All pages | All moderator operations plus role management and attraction image uploads from the attraction details page |

Users can modify or delete only their own reviews and articles. Protected
operations display a login prompt or return an authorization error for guests.

### Page Reference

#### 1. Dashboard

- Route: `/`
- Access: Everyone
- Displays headline metrics for attractions, reviews, average ratings, and
  views.
- Shows regional distribution, trending attractions, top-rated attractions,
  and recent reviews.
- Provides shortcuts to insights, attractions, regions, and rankings.

#### 2. Attractions

- Route: `/attractions`
- Access: Everyone
- Displays attraction images, locations, ratings, review counts, categories,
  and ticket prices in cards.
- Supports keyword search, category filters, and sorting by date, rating, or
  name.
- Shows nine attractions per page with `Prev` and `Next` controls.
- A card opens the attraction details page. Signed-in users can use the heart
  button to update their wishlist.

#### 3. Attraction Details

- Route: `/attractions/:id`
- Access: Everyone can view; signed-in users can interact
- Displays the main image, location, description, rating, sentiment summary,
  similar attractions, and useful reviews.
- Signed-in users can view a predicted rating, save the attraction, and submit
  a one-to-five-star English review.
- Users can delete their own reviews. The system warns about possible duplicate
  reviews before submission.
- Administrators and the attraction creator can upload a new image with
  `Change Image`.

#### 4. Map Explorer

- Route: `/map`
- Access: Everyone
- Maps attractions that have coordinates and summarizes mapped attractions,
  cities, and average rating.
- Supports name and category filters and `Markers` or `Heatmap` display modes.
- Selecting an attraction card focuses its location on the map.

#### 5. Rankings

- Route: `/rankings`
- Access: Everyone
- Lists the top 20 attractions by `Rating`, `Reviews`, `Views`, or `Saves`.
- Displays the top three in podium cards and the remaining attractions in a
  ranked list.
- The remaining list can be sorted by name. Selecting an attraction opens its
  details page.

#### 6. Compare Attractions

- Route: `/compare`
- Access: Everyone
- Compares two selected attractions side by side.
- Compares images, locations, categories, ratings, reviews, prices, saves,
  views, sentiment, seasons, opening hours, and verification status.
- Highlights the stronger value for ratings, reviews, price, saves, and views.
- The center button swaps the left and right attractions.

#### 7. Data Insights

- Route: `/insights`
- Access: Everyone
- Summarizes attractions, reviews, ratings, users, articles, views, and average
  ticket prices.
- Includes rating, visitor, category, region, price, review trend, and category
  sentiment charts.
- The `Leaderboard` switches between rating, review, view, and save metrics.
- Attraction and review data can be exported as CSV files. User exports require
  a moderator or administrator account.

#### 8. Word Clouds

- Route: `/wordcloud`
- Access: Everyone
- Calculates frequent English words from reviews and attraction descriptions.
- Supports `All content`, `Reviews`, and `Attractions` scopes.
- Word size represents frequency, while multiple colors improve readability.
- The `Top 15` list uses the same color palette for ranks and progress bars.

#### 9. Travel Guides and Articles

- Route: `/articles`
- Access: Everyone can browse; signed-in users can publish
- Lists published travel guides with search, featured filters, and pagination.
- Selecting a card opens the article details page.
- Signed-in users can open the editor with `Write Article`.

#### 10. Article Details

- Route: `/articles/:id`
- Access: Everyone can read; signed-in users can interact
- Displays the cover, author, content, tags, views, likes, and comments.
- Signed-in users can like or unlike the article and submit comments.

#### 11. Write or Edit Article

- Route: `/articles/write`
- Access: Signed-in users
- Provides fields for the title, summary, body, cover URL, related attraction,
  and tags.
- `Publish` creates an article. Users can open their own articles from the
  profile page for editing.
- `Cancel` returns to the article list.

#### 12. Questions and Answers

- Route: `/qa`
- Access: Everyone can browse; signed-in users can ask questions
- Displays questions, answer and vote counts, authors, dates, and related
  attractions.
- Supports attraction filters and pagination.
- `Ask Question` lets a signed-in user select an attraction and submit a title
  and description.

#### 13. Trip Itinerary

- Route: `/itinerary`
- Access: Everyone
- Creates a named trip with multiple days, attraction stops, and notes.
- Supports day and stop reordering, drag-and-drop sorting, deletion, and totals
  for stops, estimated price, and average rating.
- The itinerary is stored in the current browser's `localStorage` and is not
  synchronized with another account or device.
- It can be downloaded as text or printed with `Print / Save PDF`.

#### 14. My Wishlist

- Route: `/wishlist`
- Access: Signed-in users
- Summarizes saved attractions, estimated price, average rating, and visited
  attractions.
- Supports sorting by recently added, rating, or price.
- Users can set priority, mark an attraction as visited, open its details, or
  remove it.
- Guests see a login prompt.

#### 15. Smart Recommendations

- Route: `/recommendations`
- Access: Everyone can view trends and category suggestions; personalized
  results require login
- `Trending Now` uses ratings, reviews, sentiment, and time decay to rank
  attractions.
- Signed-in users can view their user cluster, preference profile, and
  behavior-based similar attractions.
- `Refresh` updates personalized results, while category controls switch the
  recommendation group.

#### 16. My Profile

- Route: `/profile`
- Access: Signed-in users
- Displays the username, email, nickname, role, biography, avatar, and
  registration date.
- `Edit Profile` updates the nickname, biography, avatar, and password.
- `My Reviews` lists and deletes the user's attraction reviews.
- `Wishlist` lists and removes saved attractions.
- `Articles` creates, edits, or deletes the user's articles.
- `Security` displays login, logout, registration, password, device, and IP
  events.

#### 17. Login

- Route: `/login`
- Access: Guests
- Authenticates with a username and password, stores the JWT session, and
  returns to the dashboard.
- The `demo` and `admin` accounts in this README can be used for testing.

#### 18. Register

- Route: `/register`
- Access: Guests
- Creates an account from a username, email address, and password. New accounts
  receive the `user` role.
- Successful registration redirects to the login page.

#### 19. Admin Dashboard

- Route: `/admin`
- Access: `admin` and `moderator`
- Summarizes users, attractions, published reviews, and pending reviews.
- `Users` blocks or unblocks accounts. Only administrators can change roles.
- `Reviews` filters by status, hides published reviews, and approves hidden or
  pending reviews.
- `Attractions` displays rating, review, and view data and controls featured
  status.
- `Login Events` filters security and account activity by event type.
- `AI Algorithms` retrains user clusters, inspects cluster membership, detects
  duplicate reviews, rebuilds the duplicate index, and recalculates trends.

### Recommended Workflows

#### Guest

1. Review headline data and popular attractions on the dashboard.
2. Search or filter destinations on `Attractions`.
3. Narrow the selection with `Map Explorer`, `Rankings`, and `Compare`.
4. Create a trip in `Trip Itinerary`, then download or print it.
5. Register when wishlist, review, or personalized features are needed.

#### User

1. Log in and use the heart button on an attraction card or details page.
2. Submit ratings and reviews to provide preference data for recommendations.
3. Open `For You` to inspect personalized suggestions and the user cluster.
4. Manage priority and visit status in `Wishlist`.
5. Manage reviews, saved attractions, articles, profile data, password, and
   login history in `My Profile`.

#### Moderator or Administrator

1. Log in with the appropriate role to display the `Administration` section.
2. Check pending reviews and unusual login events on the admin overview.
3. Complete routine moderation in the `Users`, `Reviews`, and `Attractions`
   tabs.
4. Retrain clusters or recalculate trending scores from `AI Algorithms` when
   recommendation data needs an update.
5. Administrators can replace an attraction image with `Change Image` on its
   details page.
