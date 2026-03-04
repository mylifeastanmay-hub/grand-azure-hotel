# Grand Azure — Hotel Management System

A full-stack hotel management system built with **Flask (Python)**, **SQL Server**, and a polished dark-luxury frontend.

---

## Tech Stack

| Layer    | Technology                            |
|----------|---------------------------------------|
| Backend  | Python 3.10+, Flask, SQLAlchemy       |
| Database | SQL Server (via pyodbc)               |
| Frontend | HTML5, CSS3, Vanilla JavaScript       |
| PDF      | ReportLab                             |
| Auth     | Flask-Login + bcrypt                  |

---

## Folder Structure

```
hotel_management/
├── app.py                  # Flask app factory
├── config.py               # Configuration (DB, hotel info)
├── models.py               # SQLAlchemy models
├── extensions.py           # Shared Flask extensions
├── requirements.txt        # Python dependencies
├── database_schema.sql     # SQL Server schema + seed data
├── .env.example            # Environment variable template
│
├── routes/
│   ├── auth.py             # Login / logout
│   ├── dashboard.py        # Dashboard stats API
│   ├── guests.py           # Guest CRUD
│   ├── rooms.py            # Room CRUD + availability search
│   ├── reservations.py     # Reservations + check-in/out
│   ├── payments.py         # Payments API
│   ├── services.py         # Services + orders
│   ├── staff.py            # Staff management
│   ├── reports.py          # Analytics endpoints
│   └── invoices.py         # PDF invoice generation
│
├── templates/
│   ├── base.html           # Layout with sidebar
│   ├── login.html          # Login page
│   ├── dashboard.html      # Stats + charts
│   ├── guests.html         # Guest management
│   ├── rooms.html          # Room grid
│   ├── reservations.html   # Reservation table + check-in/out
│   ├── services.html       # Services catalog + orders
│   ├── staff.html          # Staff table
│   └── reports.html        # Revenue + occupancy charts
│
└── static/
    ├── css/main.css        # Complete stylesheet
    ├── js/
    │   ├── main.js         # Utilities, modal, toast
    │   ├── dashboard.js
    │   ├── guests.js
    │   ├── rooms.js
    │   ├── reservations.js
    │   ├── services.js
    │   ├── staff.js
    │   └── reports.js
    └── invoices/           # Generated PDF invoices (auto-created)
```

---

## Prerequisites

1. **Python 3.10+** — https://python.org
2. **SQL Server 2019+** or SQL Server Express (free) — https://www.microsoft.com/en-us/sql-server/sql-server-downloads
3. **ODBC Driver 17 for SQL Server** — https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
4. **SQL Server Management Studio (SSMS)** — to run the schema script

---

## Setup Instructions

### Step 1 — Clone / download the project

Place the `hotel_management/` folder wherever you like (e.g. `C:\projects\hotel_management`).

### Step 2 — Create and activate a virtual environment

```bash
cd hotel_management

# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Create the SQL Server database

1. Open **SQL Server Management Studio (SSMS)**.
2. Connect to your SQL Server instance.
3. Open `database_schema.sql` (File → Open → File…).
4. Press **F5** (Execute) to run the script.
   - This creates the `HotelManagement` database, all tables, indexes, and seed data.

### Step 5 — Configure environment variables

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and fill in your SQL Server connection details:

```env
SQL_SERVER=localhost          # or your server name / IP
SQL_DATABASE=HotelManagement
SQL_USERNAME=sa               # your SQL login
SQL_PASSWORD=YourPassword123! # your SQL password
SQL_DRIVER=ODBC Driver 17 for SQL Server
SECRET_KEY=change-me-randomly
```

> **Tip:** If you're using Windows Authentication instead of SQL login, change the `SQLALCHEMY_DATABASE_URI` in `config.py` to use `trusted_connection=yes` and remove username/password.

### Step 6 — Create the admin user

Start the app once, then visit the setup URL:

```bash
python app.py
```

Open your browser: **http://localhost:5000/auth/setup-admin**

This creates the default admin account:
- **Username:** `admin`
- **Password:** `admin123`

> ⚠️ Change this password immediately in production!

### Step 7 — Open the application

Navigate to: **http://localhost:5000**

Login with `admin` / `admin123`

---

## Features

### Dashboard
- Live occupancy rate, revenue, reservation counts
- Revenue bar chart (last 7 days)
- Room-type doughnut chart
- Recent reservations table

### Guest Management
- Add / edit / delete guests
- Search by name, email, phone
- Store ID proof details

### Room Management
- Visual room card grid
- Filter by status and type
- Add / edit / delete rooms
- Room availability check by date range

### Reservations
- Create reservations with availability validation
- One-click **Check In** / **Check Out**
- Cancel reservations
- Status workflow: Confirmed → Checked In → Checked Out

### Services & Orders
- Service catalog by category (food, spa, transport, laundry)
- Place room service orders
- Track order delivery status

### Billing & Invoices
- Auto-calculate totals (room nights + services + tax)
- Generate professional **PDF invoices** (download or view in browser)
- Payment recording with method tracking

### Staff Management
- Add / edit staff with roles (admin, manager, staff)
- Shift management (morning, afternoon, night)
- Activate / deactivate accounts

### Reports & Analytics
- Monthly and daily revenue charts
- 30-day occupancy rate trend
- Summary KPIs (annual revenue, avg stay, total bookings)

---

## API Endpoints (RESTful)

| Method | Endpoint                           | Description               |
|--------|------------------------------------|---------------------------|
| POST   | /auth/login                        | Login                     |
| GET    | /api/dashboard/stats               | Dashboard metrics         |
| GET    | /guests/api                        | List guests               |
| POST   | /guests/api                        | Create guest              |
| PUT    | /guests/api/{id}                   | Update guest              |
| DELETE | /guests/api/{id}                   | Delete guest              |
| GET    | /rooms/api                         | List rooms                |
| GET    | /rooms/api/available               | Available rooms by dates  |
| POST   | /rooms/api                         | Create room               |
| GET    | /reservations/api                  | List reservations         |
| POST   | /reservations/api                  | Create reservation        |
| POST   | /reservations/api/{id}/checkin     | Check in guest            |
| POST   | /reservations/api/{id}/checkout    | Check out guest           |
| POST   | /reservations/api/{id}/cancel      | Cancel reservation        |
| GET    | /services/api                      | List services             |
| POST   | /services/api/orders               | Place service order       |
| GET    | /invoices/view/{reservation_id}    | View PDF invoice          |
| GET    | /invoices/generate/{reservation_id}| Download PDF invoice      |
| GET    | /reports/api/revenue               | Revenue data              |
| GET    | /reports/api/occupancy             | Occupancy data            |

---

## Production Deployment

1. Set `FLASK_ENV=production` and `FLASK_DEBUG=0` in `.env`
2. Use a production WSGI server: `pip install gunicorn && gunicorn app:create_app()`
3. Put Nginx or Apache in front as a reverse proxy
4. Use a strong, random `SECRET_KEY`
5. Store `.env` securely — never commit it to version control

---

## Troubleshooting

**pyodbc connection error:**
- Verify ODBC Driver 17 is installed: run `odbcad32.exe` on Windows
- Test the connection string in SSMS first
- Check Windows Firewall allows SQL Server port 1433

**Flask import errors:**
- Make sure virtual environment is active
- Run `pip install -r requirements.txt` again

**"Table not found" errors:**
- Run `database_schema.sql` in SSMS first
- Or alternatively use SQLite for dev: uncomment the SQLite URI in `config.py`

---

## License

MIT — free to use and modify for commercial and personal projects.
