# CME Scraper Testing Guide

## What We've Verified

### ✅ Scraper Integration
- **lib/scraper.py** - No InstantDB imports (clean Supabase integration)
- Uses Selenium for web scraping
- Properly structured with methods: `scrape_wti()`, `scrape_henry_hub()`, `get_available_dates()`

### ✅ Data Format Compatibility
- Scraper output fields match Supabase schema:
  - `date`, `commodity`, `month`, `open`, `high`, `low`, `last`, `change`, `settle`, `est_volume`, `prior_day_oi`, `created_at`
- Database expects the same fields - perfect match!

### ✅ Database Query Fix
- Fixed `lib/db.py` to use PostgREST `.eq()` method instead of `.match()`
- Query now correctly checks for existing records using:
  ```python
  .eq("date", record["date"]).eq("commodity", record["commodity"]).eq("month", record["month"])
  ```

## Test Script Created

Created `test_scraper.py` with comprehensive tests:
1. **Test Available Dates** - Fetches available dates from CME
2. **Test Scrape WTI** - Scrapes WTI data for a date
3. **Test Scrape HH** - Scrapes Henry Hub data for a date
4. **Test Database Connection** - Verifies Supabase connection
5. **Test Save Data** - Tests saving scraped data to database
6. **Test Retrieve Data** - Tests retrieving data from database
7. **Test Data Exists** - Checks if data exists for a date

## How to Run Tests

### Option 1: Debug Mode (Best for Troubleshooting)
```powershell
# Run in visible mode - opens browser so you can see what's happening
.\run_debug.ps1
```
This opens a browser window and shows detailed debug output. Best for debugging date detection issues.

### Option 2: Run Test Script (Recommended)
```powershell
# Use the helper script (uses Anaconda Python)
.\run_test.ps1
```

### Option 3: Run Test Script Directly
```powershell
# Use Anaconda Python directly
C:\Users\LuisRodriguez\anaconda3\python.exe test_scraper.py
```

### Option 4: If Python is in PATH
```powershell
python test_scraper.py
```

### Option 2: Test via Streamlit App
1. Start Streamlit app:
   ```powershell
   streamlit run app.py
   ```
2. Use the UI to:
   - Select a date from the dropdown
   - Click "Scrape WTI" or "Scrape HH"
   - Verify data appears in the table
   - Check Supabase dashboard to confirm data was saved

## Prerequisites

1. **Environment Variables** - Ensure `.env` file has:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

2. **Supabase Table** - Ensure `futures_settlements` table exists (see `SUPABASE_SCHEMA.md`)

3. **Dependencies** - All required packages in `requirements.txt`:
   - streamlit
   - pandas
   - selenium
   - webdriver-manager
   - supabase
   - postgrest
   - python-dotenv

## Expected Test Results

### Successful Test Output:
```
============================================================
TEST 1: Get Available Dates
============================================================
Found 5 available WTI dates
Sample dates:
  - Monday, 16 Dec 2024 (2024-12-16)
  - Friday, 15 Dec 2024 (2024-12-15)
  ...

============================================================
TEST 2: Scrape WTI Data for 2024-12-16
============================================================
Scraped 36 WTI contracts
Sample records (first 3):
  Month: Jan 2025
  Settle: $75.50
  ...

============================================================
TEST 4: Database Connection
============================================================
✓ Database connection successful
✓ Database query successful

============================================================
TEST 5: Save WTI Data to Database
============================================================
Results:
  Saved: 36
  Skipped: 0
```

## Troubleshooting

### If scraper fails:
- Check internet connection
- Verify CME website is accessible
- Ensure Chrome/Chromium is installed (for Selenium)
- Check that the date is available (only last 5 business days)

### If database save fails:
- Verify `.env` file has correct Supabase credentials
- Check Supabase table exists and has correct schema
- Verify RLS (Row Level Security) policies allow inserts

### If test script won't run:
- **"Could not find platform independent libraries"** - This means Python 3.14 installation is incomplete
  - **Solution**: Use Anaconda Python instead: `C:\Users\LuisRodriguez\anaconda3\python.exe test_scraper.py`
  - Or use the helper script: `.\run_test.ps1`
- Check Python is in PATH or use full path
- Install dependencies: `C:\Users\LuisRodriguez\anaconda3\python.exe -m pip install -r requirements.txt`

## Next Steps

1. Run the test script to verify scraper works
2. Test through Streamlit UI for full integration
3. Verify data in Supabase dashboard
4. Test deduplication by scraping the same date twice
5. Test with different dates to ensure reliability

## Files Modified

- ✅ `lib/db.py` - Fixed PostgREST query method
- ✅ `lib/scraper.py` - Added debug logging support
- ✅ `test_scraper.py` - Created comprehensive test script with debug mode
- ✅ `debug_scraper.py` - Created debug script (runs in visible mode)
- ✅ `run_debug.ps1` - Helper script for debug mode

## Files to Review

- `lib/scraper.py` - Main scraper implementation
- `lib/db.py` - Database operations
- `app.py` - Streamlit UI (already working)
- `SUPABASE_SCHEMA.md` - Database schema setup

