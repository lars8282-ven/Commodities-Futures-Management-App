# CME Futures Settlement Data Scraper

A simple Streamlit application for scraping and viewing WTI (Crude Oil) and HH (Natural Gas) futures settlement data from CME Group websites.

## Features

- **Date-based Scraping**: Scrape futures data for any specific date
- **Dual Commodity Support**: Scrape both WTI and Henry Hub futures
- **Data Fields**: Extracts Month, Open, High, Low, Last, Change, Settle, Est. Volume, and Prior day OI
- **Supabase Storage**: Stores scraped data in Supabase with automatic deduplication
- **Table View**: Display scraped data in an interactive table
- **Automated Daily Scraping**: Cloud function for scheduled daily data collection

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Supabase

1. Create a Supabase project at https://app.supabase.com
2. Run the SQL script in `SUPABASE_SCHEMA.md` to create the `futures_settlements` table
3. Get your Supabase credentials from Project Settings > API:
   - Project URL
   - anon public key (or service_role key for admin access)

### 4. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_anon_key_here
   ```

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. **Select a Date**: Use the date picker in the sidebar to choose the date you want to scrape
2. **Scrape Data**: Click "Scrape WTI", "Scrape HH", or "Scrape Both" buttons
3. **View Data**: The scraped data will appear in the main table below
4. **Filter**: Use the commodity filter to show All, WTI only, or HH only
5. **Download**: Click "Download as CSV" to export the data

## Automated Daily Scraping

The app includes a cloud function (`functions/daily_scraper.py`) that can be deployed to run automatically every day.

### Deploy to Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Deploy: `vercel`
3. Set environment variables in Vercel dashboard
4. The function will run daily at 6 PM ET (configured in `vercel.json`)

### Deploy to AWS Lambda

1. Package the function with dependencies
2. Create a Lambda function
3. Set up EventBridge rule for daily schedule
4. Configure environment variables

### Manual Testing

You can test the daily scraper locally:

```bash
python functions/daily_scraper.py
```

## Data Fields

The scraper extracts the following fields from CME settlement pages:

- **Month**: Contract month (e.g., "Jan 2025")
- **Open**: Opening price
- **High**: High price
- **Low**: Low price
- **Last**: Last traded price
- **Change**: Price change
- **Settle**: Settlement price
- **Est. Volume**: Estimated trading volume
- **Prior day OI**: Prior day open interest

## Project Structure

```
.
├── app.py                      # Main Streamlit application
├── lib/
│   ├── db.py                   # Supabase database client
│   └── scraper.py              # CME web scraper
├── functions/
│   └── daily_scraper.py        # Automated daily scraper function
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── SUPABASE_SCHEMA.md          # Database schema setup guide
└── vercel.json                 # Vercel deployment configuration
```

## Data Sources

- **WTI Futures**: https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.settlements.html
- **HH Futures**: https://www.cmegroup.com/markets/energy/natural-gas/natural-gas.settlements.html

## Troubleshooting

### Connection Errors

- Verify your Supabase URL and key are correct in `.env`
- Check that the `futures_settlements` table exists in your Supabase project
- Ensure your Supabase project is active

### Scraping Errors

- CME website structure may change - the scraper may need updates
- Check your internet connection
- Verify the date you're scraping has data available (markets are closed on weekends)

### No Data Found

- The date may not have data available yet (try yesterday's date)
- Markets may be closed (weekends, holidays)
- CME website structure may have changed

## License

Private project for Tepui Ventures
