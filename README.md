# NASA APOD ETL Pipeline (Docker + Airflow)

An automated ETL (Extract, Transform, Load) pipeline that fetches NASA's Astronomy Picture of the Day (APOD) data and stores it in a Supabase database. This repo includes an Apache Airflow stack via Docker Compose to schedule and run the pipeline daily.

## Project Overview

This project demonstrates a complete data pipeline that:
- **Extracts** data from NASA's APOD API
- **Transforms** the JSON data into a structured CSV format
- **Loads** the processed data into a Supabase PostgreSQL database

## Project Structure

```
nasa_etl_project/
├── data/
│   ├── raw/              # Raw JSON data from NASA API
│   └── staged/           # Transformed CSV data
├── scripts/
│   ├── extract.py        # Fetches data from NASA APOD API
│   ├── transform.py      # Transforms JSON to CSV
│   └── load.py           # Loads data into Supabase
├── airflow/
│   └── dags/
│       ├── nasa_etl_dags.py  # Airflow DAG: extract → transform → load
│       └── init_variables.py # Bootstrap Airflow Variables from .env
├── ui/
│   ├── streamlit_app.py      # Streamlit frontend (gallery, search, stats)
│   ├── requirements.txt       # Python dependencies for UI
│   └── .streamlit/config.toml # Streamlit configuration
├── docker-compose.yaml        # Airflow stack (webserver, scheduler, worker, db)
└── README.md
```

## Database Schema

```sql
CREATE TABLE nasa_apod (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    title VARCHAR(255) NOT NULL,
    explanation TEXT NOT NULL,
    media_type VARCHAR(50),
    image_url TEXT,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Prerequisites

- Docker Desktop (Windows/macOS/Linux)
- Python 3.9+
- NASA API Key (get one at https://api.nasa.gov/)
- Supabase account and project

## Quickstart

1) Create `.env` from template and fill keys:

```
copy .env.example .env
# Edit .env and set: api_key, supabase_url, supabase_key
```

2) Start Docker and Airflow stack:

```powershell
docker compose up -d
```

3) Initialize Airflow Variables from `.env`:

```powershell
docker compose exec airflow-scheduler python /opt/airflow/dags/init_variables.py
```

4) Ensure Supabase has the table and unique constraint on `date` (run in Supabase SQL editor):

```sql
CREATE TABLE IF NOT EXISTS public.nasa_apod (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    title VARCHAR(255) NOT NULL,
    explanation TEXT NOT NULL,
    media_type VARCHAR(50),
    image_url TEXT,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE public.nasa_apod
  ADD CONSTRAINT IF NOT EXISTS nasa_apod_date_key UNIQUE (date);
```

5) Test the DAG for today's run:

```powershell
docker compose exec airflow-scheduler airflow dags test nasa_etl_pipeline 2025-12-14
```

6) Launch the Streamlit UI:

```powershell
cd ui
python -m pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8501
```

Open http://localhost:8501

## Usage

### Run via Airflow (Recommended)

1) In Airflow UI, ensure `nasa_etl_pipeline` is toggled ON.
2) Trigger a manual run if desired (▶ button).
3) Monitor task logs for `extract_nasa_data`, `transform_nasa_data`, and `load_to_supabase`.

The DAG is scheduled `@daily` and will run automatically when the stack is up.

### Run Streamlit UI Locally

View and interact with APOD data in a web browser:

```bash
cd ui
streamlit run streamlit_app.py
```

Open http://localhost:8501 to browse the APOD gallery, search records, and view stats. Videos play inline when `media_type=video`, otherwise images render responsively.

**Features:**
- 🖼️ Gallery view with images and descriptions
- 🔍 Search by keyword, date range, or media type
- 📊 Dashboard with stats (total records, last update)
- ⚙️ Pipeline status indicator
- 📱 Responsive design

### Run locally (optional)

You can also run scripts outside Airflow for debugging:

```bash
python scripts/extract.py
python scripts/transform.py
python scripts/load.py
```

### Individual Script Details

#### Extract (`extract.py`)
- Fetches the latest APOD data from NASA's API
- Saves raw JSON to `data/raw/nasa_data.json`
- Returns the data dictionary

#### Transform (`transform.py`)
- Reads the raw JSON file
- Extracts relevant fields: date, title, explanation, media_type, image_url
- Saves processed data to `data/staged/nasa_data_staged.csv`

#### Load (`load.py`)
- Reads the staged CSV file
- Connects to Supabase database
- Inserts data using RPC (Remote Procedure Call)
- Includes error handling and batch processing

## Data Fields

| Field | Type | Description |
|-------|------|-------------|
| date | DATE | Publication date of the APOD |
| title | VARCHAR(255) | Title of the astronomy picture |
| explanation | TEXT | Detailed explanation of the image |
| media_type | VARCHAR(50) | Type of media (image/video) |
| image_url | TEXT | URL to the image |

## Supabase Setup

You'll need to create a stored procedure in Supabase to execute SQL queries:

```sql
CREATE OR REPLACE FUNCTION execute_sql(query text)
RETURNS void AS $$
BEGIN
  EXECUTE query;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

Also ensure a `nasa_apod` table exists (see schema above). The loader uses RPC to insert batches.

For idempotent loads without duplicates, ensure `UNIQUE(date)` on `nasa_apod`. The loader performs an upsert via SQL RPC using `ON CONFLICT (date) DO UPDATE`.

## Troubleshooting

- Docker not starting: ensure Docker Desktop is running, then `docker compose up -d`.
- DAG not visible: confirm `AIRFLOW_PROJ_DIR=./airflow` in `.env` and that `airflow/dags/nasa_etl_dags.py` exists.
- Missing variables: set `api_key`, `supabase_url`, `supabase_key` in Airflow Variables.
- Supabase RPC missing: create the `execute_sql` function as above.
- Permissions/paths: scripts and data are mounted at `/opt/airflow/scripts` and `/opt/airflow/data` in containers.
- Streamlit won't load data: verify `.env` is in project root with valid Supabase credentials.
 - Windows path issues: if `streamlit_app.py` isn't found, run via absolute path or `cd ui` first.

## Deployment

### Deploy Streamlit Frontend (Free)

1) Push the repo to GitHub (already done ✓).
2) Go to [Streamlit Cloud](https://streamlit.io/cloud).
3) Click "New app" → connect GitHub repo.
4) Select `ui/streamlit_app.py` as the main file.
5) Add Secrets (in Streamlit Cloud settings):
   ```
   supabase_url = "your_url"
   supabase_key = "your_key"
   ```
6) Click "Deploy" — app is live at `https://<your-username>-nasa-etl-project.streamlit.app`

### Deploy Airflow (Optional - Self-Hosted)

For production, deploy Airflow to:
- AWS EC2 + Docker
- Google Cloud Run
- DigitalOcean
- Railway

Currently running locally; ideal for portfolio demo.

- File existence checks before processing
- API request error handling with `raise_for_status()`
- SQL injection protection with quote escaping
- Batch processing with delays to avoid rate limiting

## Future Enhancements

- Automated bootstrap of Airflow Variables from `.env`
- Add data validation and quality checks
- Implement incremental loading (avoid duplicates)
- Add logging for better monitoring
- Create a combined pipeline script
- Add unit tests
- Advanced Streamlit features: user ratings, favorites, sharing
- Multi-user authentication for Streamlit Cloud

## License

This project uses NASA's public API. Please review NASA's API terms of use.

## Author

Created as a demonstration of ETL pipeline development with Python and Supabase.
