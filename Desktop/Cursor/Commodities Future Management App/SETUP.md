# Setup Guide for Commodities Futures Management App

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- InstantDB account and credentials

## Installation Steps

### 1. Create Virtual Environment

```bash
# Navigate to the project directory
cd "Commodities Future Management App"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env  # Windows
   # or
   cp .env.example .env   # macOS/Linux
   ```

2. Edit `.env` and add your InstantDB credentials:
   ```
   INSTANT_APP_ID=your_instant_app_id_here
   INSTANT_API_KEY=your_instant_api_key_here
   ```

### 4. Set Up InstantDB

**Important**: See `INSTANTDB_SETUP.md` for detailed instructions on setting up InstantDB.

The app expects these entities to be created in your InstantDB instance:
- `futuresContracts`
- `spotPrices`
- `errorCalculations`
- `scrapeLogs`

You may need to:
1. Create these entities in the InstantDB dashboard
2. Or use InstantDB's auto-creation feature if available
3. Or modify the code to use a different database (see `INSTANTDB_SETUP.md`)

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

### Initial Data Import

1. Go to the **Data Import** page
2. Upload Excel files with historical futures and spot price data
3. The app will parse and import the data into InstantDB

### Manual Scraping

1. Go to the **Dashboard** page
2. Click "Run Manual Scrape" in the sidebar
3. The app will scrape current data from CME and EIA

### Error Calculation

1. After importing/scraping data, click "Calculate Errors" in the sidebar
2. The app will match futures contracts with spot prices and calculate errors

### Viewing Analysis

- **Dashboard**: Overview with key metrics and charts
- **Error Analysis**: Detailed error analysis with distributions and heatmaps
- **Data Import**: Import historical data from Excel files
- **Settings**: Configuration information

## Troubleshooting

### InstantDB Connection Issues

- Verify your `INSTANT_APP_ID` and `INSTANT_API_KEY` are correct
- Check `INSTANTDB_SETUP.md` for alternative database options
- Ensure InstantDB entities are created

### Scraping Issues

- Check your internet connection
- Verify the CME and EIA websites are accessible
- Some websites may require specific headers or have rate limits
- Check the console for error messages

### Import Issues

- Ensure Excel files have the correct column headers
- Check that dates and prices are in valid formats
- Review error messages in the Streamlit interface

## Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Go to https://streamlit.io/cloud
3. Connect your repository
4. Set environment variables in the Streamlit Cloud dashboard
5. Deploy

### Vercel (Alternative)

If you prefer Vercel, you may need to:
1. Convert the app to a Next.js application
2. Or use Vercel's Python runtime with Streamlit
3. Set up Vercel Cron jobs for daily scraping

## Daily Automation

To enable daily automated scraping:

1. **Local/Server**: Use the APScheduler (already implemented in `lib/scheduler.py`)
   - Start the scheduler in your deployment environment
   - Configure the scrape time in `.env`

2. **Cloud**: Use platform-specific cron jobs
   - Streamlit Cloud: May require external scheduler
   - Vercel: Use Vercel Cron
   - Other platforms: Use their scheduled job features

## Additional Features

Future enhancements can include:
- Time series predictions using ML models
- Alert system for high errors
- API endpoints for external integrations
- Advanced filtering and analysis options

