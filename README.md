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
│       └── nasa_etl_dags.py  # Airflow DAG: extract → transform → load
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
- NASA API Key (get one at https://api.nasa.gov/)
- Supabase account and project

## Setup

1) Configure `.env` in the project root:

```
api_key=YOUR_NASA_API_KEY
supabase_url=YOUR_SUPABASE_URL
supabase_key=YOUR_SUPABASE_KEY
AIRFLOW_IMAGE_NAME=apache/airflow:2.4.2
AIRFLOW_UID=50000
AIRFLOW_PROJ_DIR=./airflow
_PIP_ADDITIONAL_REQUIREMENTS=supabase python-dotenv pandas requests
```

2) Start Docker Desktop, then bring up Airflow:

```powershell
docker compose up -d
```

3) Open Airflow UI at http://localhost:8080 (username: `airflow`, password: `airflow`).

4) Populate Airflow Variables from `.env` (one-time setup):

```powershell
docker compose exec airflow-scheduler python /opt/airflow/dags/init_variables.py
```

This reads `.env` and auto-creates Variables: `api_key`, `supabase_url`, `supabase_key`.

Alternatively, create Variables manually (Admin → Variables):
- `api_key`: YOUR_NASA_API_KEY
- `supabase_url`: YOUR_SUPABASE_URL
- `supabase_key`: YOUR_SUPABASE_KEY

## Usage

### Run via Airflow (Recommended)

1) In Airflow UI, ensure `nasa_etl_pipeline` is toggled ON.
2) Trigger a manual run if desired (▶ button).
3) Monitor task logs for `extract_nasa_data`, `transform_nasa_data`, and `load_to_supabase`.

The DAG is scheduled `@daily` and will run automatically when the stack is up.

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

## Troubleshooting

- Docker not starting: ensure Docker Desktop is running, then `docker compose up -d`.
- DAG not visible: confirm `AIRFLOW_PROJ_DIR=./airflow` in `.env` and that `airflow/dags/nasa_etl_dags.py` exists.
- Missing variables: set `api_key`, `supabase_url`, `supabase_key` in Airflow Variables.
- Supabase RPC missing: create the `execute_sql` function as above.
- Permissions/paths: scripts and data are mounted at `/opt/airflow/scripts` and `/opt/airflow/data` in containers.

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

## License

This project uses NASA's public API. Please review NASA's API terms of use.

## Author

Created as a demonstration of ETL pipeline development with Python and Supabase.
