# NASA APOD ETL Pipeline

An automated ETL (Extract, Transform, Load) pipeline that fetches NASA's Astronomy Picture of the Day (APOD) data and stores it in a Supabase database.

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
│   ├── transform.py      # Trcdansforms JSON to CSV
│   └── load.py           # Loads data into Supabase
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

- Python 3.11+
- NASA API Key (get one at https://api.nasa.gov/)
- Supabase account and project

## Installation

1. Clone this repository or navigate to the project directory

2. Install required packages:
```bash
pip install requests pandas supabase python-dotenv
```

3. Create a `.env` file in the project root with your credentials:
```
supabase_url=your_supabase_url
supabase_key=your_supabase_key
```

4. Update the NASA API key in `scripts/extract.py` (or use environment variables)

## Usage

### Run the Complete ETL Pipeline

Execute the scripts in order:

```bash
cd scripts

# Step 1: Extract data from NASA API
python extract.py

# Step 2: Transform JSON to CSV
python transform.py

# Step 3: Load data into Supabase
python load.py
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

## Error Handling

- File existence checks before processing
- API request error handling with `raise_for_status()`
- SQL injection protection with quote escaping
- Batch processing with delays to avoid rate limiting

## Future Enhancements

- Schedule automated daily runs using cron or task scheduler
- Add data validation and quality checks
- Implement incremental loading (avoid duplicates)
- Add logging for better monitoring
- Create a combined pipeline script
- Add unit tests

## License

This project uses NASA's public API. Please review NASA's API terms of use.

## Author

Created as a demonstration of ETL pipeline development with Python and Supabase.
