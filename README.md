# Irish Civil War Location-Based Services (LBS)

![Status](https://img.shields.io/badge/status-complete-success) ![License](https://img.shields.io/badge/license-MIT-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![Django](https://img.shields.io/badge/django-4.0+-green)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Deployment](#deployment)
- [Screenshots](#screenshots)
- [Known Issues & Limitations](#known-issues--limitations)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**Irish Civil War LBS** is a Django-based Location-Based Services web application that provides interactive mapping and historical analysis of significant sites from the Irish Civil War period (1916-1923). The application combines geospatial technologies with historical documentation to create an educational resource for exploring this pivotal period in Irish history.

### Key Objectives
- Visualize historical sites on an interactive map
- Enable proximity-based searching for nearby locations
- Provide temporal filtering by historical period
- Maintain comprehensive historical records with geospatial coordinates
- Support WCAG AA accessibility standards

---

## Features

### Core Functionality
- **Interactive Mapping**: Leaflet.js-powered map with OpenStreetMap tiles
- **Historical Site Management**: 22 documented sites from Irish Civil War era
- **Multi-Period Timeline**: 5 distinct historical periods (Easter Rising, War of Independence, Treaty Period, Civil War, Aftermath)
- **Advanced Filtering**:
  - Date range filtering (temporal)
  - Category-based filtering (historical periods)
  - Proximity-based search (geographic)
- **REST API**: Django REST Framework for programmatic access
- **Responsive Design**: Mobile-first Bootstrap 5 UI
- **Accessibility**: Full WCAG AA compliance with keyboard navigation and screen reader support

### Technical Features
- PostGIS spatial database integration
- Complex geospatial queries (proximity searches)
- JSONB data support for flexible historical metadata
- Static file optimization and caching
- CORS-enabled API endpoints

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend** | Django | 4.0+ |
| **Database** | PostgreSQL | 12+ |
| **Spatial DB** | PostGIS | 3.0+ |
| **Frontend** | Bootstrap | 5.3 |
| **Mapping** | Leaflet.js | 1.9.4 |
| **REST API** | Django REST Framework | 3.14+ |
| **ORM** | Django ORM | Built-in |
| **Python** | Python | 3.9+ |
| **Server** | Gunicorn | 20.1+ |
| **Reverse Proxy** | Nginx | 1.18+ |

---

## Project Structure

```
irish-civil-war-lbs/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore configuration
├── irish_civil_war_project/           # Main Django project settings
│   ├── __init__.py
│   ├── settings.py                    # Project configuration
│   ├── urls.py                        # Main URL routing
│   ├── wsgi.py                        # WSGI configuration
│   └── asgi.py                        # ASGI configuration
├── api/                               # REST API app
│   ├── migrations/                    # Database migrations
│   ├── models.py                      # Historical site model
│   ├── serializers.py                 # DRF serializers
│   ├── views.py                       # API viewsets
│   ├── urls.py                        # API URL routing
│   └── admin.py                       # Django admin config
├── historical_sites/                  # Historical sites app
│   ├── migrations/
│   ├── models.py
│   ├── views.py                       # Frontend views
│   ├── urls.py
│   └── templates/
│       └── historical_sites/
├── templates/                         # Global templates
│   ├── base.html                      # Base template
│   └── historical_sites/
│       ├── index.html
│       └── detail.html
├── static/                            # Static files
│   ├── css/
│   │   └── style.css                  # Main stylesheet
│   ├── js/
│   │   ├── map.js                     # Map initialization and logic
│   │   └── main.js                    # Global JavaScript
│   └── images/
├── staticfiles/                       # Collected static files (production)
├── logs/                              # Application logs
├── irish_civil_war_sites.json         # Historical data (import fixture)
├── docker-compose.yml                 # Docker Compose configuration
├── Dockerfile                         # Docker image definition
├── nginx.conf                         # Nginx configuration
└── venv/                              # Virtual environment (excluded from git)
```

---

## Setup Instructions

### Local Development Setup

#### Prerequisites
- Python 3.9 or higher
- PostgreSQL 12 or higher with PostGIS extension
- Git
- Virtual environment manager (venv or conda)

#### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/irish-civil-war-lbs.git
cd irish-civil-war-lbs
```

#### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your local configuration
```

**Key environment variables to set:**
```env
DEBUG=True
SECRET_KEY=your-django-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@localhost:5432/irish_civil_war_db
POSTGIS_URL=postgresql://user:password@localhost:5432/irish_civil_war_db
```

#### Step 5: Database Setup

```bash
# Create PostgreSQL database
createdb irish_civil_war_db
psql irish_civil_war_db -c "CREATE EXTENSION postgis;"

# Run migrations
python manage.py migrate

# Load historical data
python manage.py loaddata irish_civil_war_sites.json

# Create superuser
python manage.py createsuperuser
```

#### Step 6: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

#### Step 7: Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

---

## Configuration

### Environment Variables (.env)

Create a `.env` file in the project root (see `.env.example` for template):

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/database_name

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# CORS (for API)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Django Settings

Key settings in `irish_civil_war_project/settings.py`:
- **INSTALLED_APPS**: Includes `api`, `historical_sites`, `rest_framework`, `corsheaders`
- **DATABASES**: Configured for PostgreSQL with PostGIS support
- **MIDDLEWARE**: CORS, CSRF, and authentication middleware
- **REST_FRAMEWORK**: Pagination, authentication, and filtering configuration

---

## Running the Application

### Development Server

```bash
python manage.py runserver
```

### Production with Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 irish_civil_war_project.wsgi
```

### Using Docker Compose

```bash
docker-compose up -d
```

Access the application at `http://localhost:8000`

---

## API Documentation

### Base URL
```
/api/sites/
```

### Endpoints

#### 1. List All Historical Sites
```http
GET /api/sites/
```

**Query Parameters:**
- `period`: Filter by historical period (EASTER_RISING, WAR_INDEPENDENCE, TREATY, CIVIL_WAR, AFTERMATH)
- `search`: Full-text search on name/description
- `nearby`: Proximity search (requires `latitude`, `longitude`, `radius_km`)

**Example:**
```bash
curl "http://localhost:8000/api/sites/?period=CIVIL_WAR&search=Dublin"
```

**Response:**
```json
{
  "count": 22,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "General Post Office",
      "location": {
        "type": "Point",
        "coordinates": [-6.2655, 53.3432]
      },
      "period": "EASTER_RISING",
      "latitude": 53.3432,
      "longitude": -6.2655,
      "description": "Site of Easter Rising proclamation",
      "significance": "HIGH",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

#### 2. Retrieve Single Site
```http
GET /api/sites/{id}/
```

**Example:**
```bash
curl "http://localhost:8000/api/sites/1/"
```

#### 3. Proximity Search
```http
GET /api/sites/?nearby=true&latitude=53.3498&longitude=-6.2603&radius_km=5
```

**Parameters:**
- `latitude`: Latitude of search center
- `longitude`: Longitude of search center
- `radius_km`: Search radius in kilometers

#### 4. Date Range Filtering
```http
GET /api/sites/?date_from=1916-01-01&date_to=1923-12-31
```

### Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 404 | Site not found |
| 400 | Invalid query parameters |
| 500 | Server error |

---

## Database Schema

### Historical Site Model

```sql
CREATE TABLE api_historicalsite (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  location GEOMETRY(Point, 4326) NOT NULL,
  period VARCHAR(50) NOT NULL,
  latitude DECIMAL(9, 6),
  longitude DECIMAL(9, 6),
  significance VARCHAR(50),
  historical_context JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_location ON api_historicalsite USING GIST(location);
CREATE INDEX idx_period ON api_historicalsite(period);
```

### Period Choices
- `EASTER_RISING`: Easter Rising (1916)
- `WAR_INDEPENDENCE`: War of Independence (1919-1921)
- `TREATY`: Treaty Period (1921-1922)
- `CIVIL_WAR`: Civil War (1922-1923)
- `AFTERMATH`: Aftermath (1923+)

### Significance Levels
- `CRITICAL`: Major historical significance
- `HIGH`: Important site
- `MEDIUM`: Notable site
- `LOW`: Minor historical interest

---

## Deployment

### Cloud Deployment (Heroku Example)

```bash
# Create Procfile
echo "web: gunicorn irish_civil_war_project.wsgi" > Procfile

# Add Heroku remote
heroku create your-app-name

# Configure environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=your-heroku-postgres-url

# Deploy
git push heroku main
```

### Docker Deployment

```bash
# Build image
docker build -t irish-civil-war-lbs .

# Run container
docker run -p 8000:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=your-secret \
  -e DATABASE_URL=postgresql://... \
  irish-civil-war-lbs
```

### Using Docker Compose

```bash
docker-compose up -d
```

See `docker-compose.yml` and `Dockerfile` for configuration details.

---

## Screenshots

### Home Page
The hero section features the application title with call-to-action buttons for exploring the interactive map and learning about Irish Civil War history.

### Interactive Map
- Leaflet-based interactive map displaying 22 historical sites
- Color-coded markers by historical period
- Real-time site list with filtering controls
- Modal popups with detailed site information

### Filters and Controls
- **Timeline Filter**: Date range picker (1916-1923)
- **Category Filter**: Multi-select historical periods
- **Proximity Search**: Search nearby sites within custom radius
- **Statistics**: Display total and visible sites

### Accessibility Features
- WCAG AA compliant (0 accessibility issues)
- Keyboard navigation throughout
- High contrast color schemes
- Screen reader optimized

---

## Known Issues & Limitations

### Current Limitations

1. **Historical Data Completeness**: Database contains 22 documented sites. Additional historical sites may be added in future releases.

2. **Real-time Updates**: Site data requires manual updates. Real-time event integration not yet implemented.

3. **Authentication**: Currently read-only API with no user authentication. Future version will include user accounts and contributions.

4. **Mobile Offline Support**: Application requires active internet connection. Offline mode not yet implemented.

5. **Media Files**: Historical photographs not yet integrated. Currently displays placeholder images.

### Performance Notes

- Large proximity searches (100+ km radius) may experience slight delay
- PostGIS queries optimized with spatial indexes
- Static files cached with 1-year expiration

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- Historical data sourced from academic records and historical societies
- Leaflet.js for mapping capabilities
- Django REST Framework for API development
- PostGIS for spatial database functionality
- Bootstrap for responsive UI framework

---

**Last Updated**: November 2025  
**Version**: 1.0.0
