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
├── docker-compose.yml                 # Docker Compose configuration
├── Dockerfile                         # Docker image definition
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore configuration
│
├── irish_civil_war_project/           # Main Django project settings
│   ├── __init__.py
│   ├── settings.py                    # Project configuration
│   ├── urls.py                        # Main URL routing
│   ├── wsgi.py                        # WSGI configuration
│   └── asgi.py                        # ASGI configuration
│
├── api/                               # REST API (API Logic remains in app as no external API used)
│
├── historical_sites/                  # Historical sites REST API App
│   ├── migrations/                    # Database migrations
│   ├── models.py                      # Historical site model
│   ├── serializers.py                 # DRF serializers
│   ├── views.py                       # API viewsets
│   ├── urls.py                        # API URL routing
│   ├── admin.py                       # Django admin config
│   └── management/
│       ├─── commands/
│       ├────── load_historical_sites.py
│       ├────── load_county_boundaries_from_geojson.py
│       └────── update_sites_with_images.py
│
├── templates/                         # Global templates
│   ├── base.html                      # Base template
│   └── map.html
│
├── static/                            # Static files
│   ├── css/
│   │   └── style.css                  # Main stylesheet
│   ├── js/
│   │   ├── map.js                     # Map initialization and logic
│   │   ├── scripts.js                 # Script for smooth web page
│   │   └── main.js                    # Global JavaScript
│   └── images/
│
├── staticfiles/                       # Collected static files (production)
│
├── documentation/                     # Project Technology Diagram and Database Schema Docs.
│
└── venv/                              # Virtual environment (excluded from git)
```

---

## Setup Instructions

### Docker Deployment Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/irish-civil-war-lbs.git
cd irish-civil-war-lbs
```

```bash
2. Create environment file
cp .env.example .env
```

#### Django Settings
```env
DEBUG=False
SECRET_KEY=change-me-in-production-very-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,django,nginx
```

#### Database Configuration
```env
DB_USER=irish_admin
DB_PASSWORD=secure_password_change_me
DB_NAME=irish_civil_war_db
DB_HOST=db
DB_PORT=5432
```

##### PgAdmin (Database Management UI)
```env
PGADMIN_EMAIL=admin@irish-war.local
PGADMIN_PASSWORD=admin_password_change_me
```

##### Security 
```env
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
```

#### Nginx Configuration
```env
NGINX_HOST=localhost
NGINX_PORT=80
```

#### CORS (API Access)
```env
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000
```

3. Build and start all services
```bash
docker-compose build --no-cache
docker-compose up -d
```
**Note:**Wait for all containers to be healthy before Step 4.

4. Load historical data
```bash
docker-compose exec django python manage.py migrate
docker-compose exec django sh -c "python manage.py load_county_boundaries_from_geojson irish_counties.geojson && python manage.py update_sites_with_images sites_images_descriptions.json"
docker-compose exec django python manage.py collectstatic --noinput
```

5. Access the application
  - Open `http://127.0.0.1` in your browser
  - Access PGAdmin at `http://localhost:5050`
    - Login with credentials from `.env` file (PGADMIN_EMAIL and PGADMIN_PASSWORD)
    - Add new server:
      - Name: irish_civil_war_db
      - Host: db
      - Port: 5432
      - Username: irish_admin
      - Password: [DB_PASSWORD from .env]


---

## Configuration

### Django Settings

Key settings in `irish_civil_war_project/settings.py`:
- **INSTALLED_APPS**: Includes `api`, `historical_sites`, `rest_framework`, `corsheaders`
- **DATABASES**: Configured for PostgreSQL with PostGIS support
- **MIDDLEWARE**: CORS, CSRF, and authentication middleware
- **REST_FRAMEWORK**: Pagination, authentication, and filtering configuration

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
CREATE TABLE historical_sites_historicalsite (
  id SERIAL PRIMARY KEY,
  
  -- Basic Information
  name VARCHAR(255) NOT NULL UNIQUE,
  event_date DATE NOT NULL,
  location_name VARCHAR(500) NOT NULL,
  
  -- Spatial Data (PostGIS)
  location GEOMETRY(Point, 4326) NOT NULL,
  
  -- Historical Context
  significance TEXT NOT NULL,
  category VARCHAR(50) NOT NULL,
  event_type VARCHAR(100) NOT NULL,
  
  -- Additional Details
  description TEXT,
  casualties INTEGER,
  commanders JSONB DEFAULT '[]',
  
  -- Media and Resources
  images JSONB DEFAULT '[]',
  audio_url VARCHAR(200),
  sources JSONB DEFAULT '[]',
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Spatial index for location-based queries
CREATE INDEX idx_historicalsite_location 
  ON historical_sites_historicalsite 
  USING GIST(location);

-- B-tree indexes for filtering
CREATE INDEX idx_historicalsite_event_date 
  ON historical_sites_historicalsite(event_date);

CREATE INDEX idx_historicalsite_category 
  ON historical_sites_historicalsite(category);

-- Unique constraint on site name
CREATE UNIQUE INDEX idx_historicalsite_name 
  ON historical_sites_historicalsite(name);

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

## Screenshots

### Home Page
The hero section features the application title with call-to-action buttons for exploring the interactive map and learning about Irish Civil War history.

<img width="1470" height="877" alt="Screenshot 2025-11-04 at 17 08 47" src="https://github.com/user-attachments/assets/a5c0676a-dfb0-49a5-8389-86d7c70f8874" />
<img width="1470" height="878" alt="Screenshot 2025-11-04 at 17 09 18" src="https://github.com/user-attachments/assets/504e38d1-5109-4c9c-a622-f73ea92f5a22" />

### Interactive Map
- Leaflet-based interactive map displaying 22 historical sites
- Color-coded markers by historical period
- Real-time site list with filtering controls
- Modal popups with detailed site information

<img width="1470" height="877" alt="Screenshot 2025-11-04 at 17 09 42" src="https://github.com/user-attachments/assets/c3cc9696-b9a2-45b1-9bae-aa2d8e0ef0b9" />

### Filters and Controls and Alternate Views
- **Timeline Filter**: Date range picker (1916-1923)
- **Category Filter**: Multi-select historical periods
- **Proximity Search**: Search nearby sites within custom radius
- **Statistics**: Display total and visible sites

<img width="1470" height="874" alt="Screenshot 2025-11-04 at 18 12 28" src="https://github.com/user-attachments/assets/b55cad6b-c7ad-4b8f-9b3e-9ca20be5e733" />
<img width="1470" height="874" alt="Screenshot 2025-11-04 at 18 12 50" src="https://github.com/user-attachments/assets/2b85d26d-9e72-4a40-bc3c-5b5694823254" />

### Accessibility Features
- WCAG AA compliant (0 accessibility issues)
- Keyboard navigation throughout
- High contrast color schemes
- Screen reader optimized

<img width="1470" height="874" alt="Screenshot 2025-11-04 at 18 14 41" src="https://github.com/user-attachments/assets/56148b2e-11ac-4af1-aa41-31e1bef18cef" />

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
