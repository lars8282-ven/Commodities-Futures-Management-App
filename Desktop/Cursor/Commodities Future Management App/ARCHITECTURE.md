# Architecture Overview

## Application Structure

```
Commodities Future Management App/
├── app.py                    # Main Streamlit application entry point
├── lib/                      # Core libraries
│   ├── instant_client.py     # InstantDB client wrapper
│   ├── cme_scraper.py        # CME futures scraper
│   ├── eia_scraper.py        # EIA spot price scraper
│   ├── excel_importer.py     # Excel file importer
│   ├── error_calculator.py   # Error calculation engine
│   ├── scheduler.py          # Daily automation scheduler
│   └── data_processor.py     # Data processing utilities
├── components/               # Reusable UI components
│   ├── charts/               # Visualization components
│   │   ├── error_over_time.py
│   │   ├── percentile_distribution.py
│   │   ├── futures_vs_spot.py
│   │   └── contract_analysis.py
│   └── tables/               # Table components
│       ├── error_summary_table.py
│       └── futures_data_table.py
├── pages/                    # Streamlit pages (if using multi-page)
├── data/                     # Data storage
│   ├── backfill/             # Excel files for backfilling
│   └── cache/                # Cached scraped data
└── requirements.txt          # Python dependencies
```

## Data Flow

```
┌─────────────┐
│   CME Site  │──┐
└─────────────┘  │
                 ├──► [CME Scraper] ──► [InstantDB: futuresContracts]
┌─────────────┐  │
│   EIA Site  │──┘
└─────────────┘

┌─────────────┐
│ Excel Files │──► [Excel Importer] ──► [InstantDB: futuresContracts/spotPrices]
└─────────────┘

[InstantDB: futuresContracts] ──┐
                                 ├──► [Error Calculator] ──► [InstantDB: errorCalculations]
[InstantDB: spotPrices] ─────────┘

[InstantDB: errorCalculations] ──► [Visualizations] ──► [Streamlit UI]
```

## Key Components

### 1. Data Scraping

**CME Scraper** (`lib/cme_scraper.py`):
- Scrapes WTI and Henry Hub futures settlement prices
- Handles all available contract months
- Parses contract symbols and dates
- Stores data with deduplication

**EIA Scraper** (`lib/eia_scraper.py`):
- Scrapes WTI and Henry Hub spot prices
- Handles monthly and daily data formats
- Matches dates with futures contracts
- Stores data with deduplication

### 2. Data Import

**Excel Importer** (`lib/excel_importer.py`):
- Flexible column mapping for various Excel formats
- Validates and cleans data
- Handles missing values
- Bulk import with progress tracking

### 3. Error Calculation

**Error Calculator** (`lib/error_calculator.py`):
- Matches futures contracts with spot prices by date
- Calculates absolute error: `|futuresPrice - spotPrice|`
- Calculates percentage error: `((futuresPrice - spotPrice) / spotPrice) * 100`
- Computes days to expiry
- Provides statistical summaries

### 4. Visualizations

**Error Over Time** (`components/charts/error_over_time.py`):
- Line charts showing error trends
- Dual-axis for absolute and percentage errors
- Filterable by commodity and contract month

**Percentile Distribution** (`components/charts/percentile_distribution.py`):
- Histograms with percentile markers
- Separate views for absolute and percentage errors
- Statistical analysis

**Futures vs Spot** (`components/charts/futures_vs_spot.py`):
- Dual-axis comparison chart
- Error bars visualization
- Time series overlay

**Contract Analysis** (`components/charts/contract_analysis.py`):
- Heatmap by contract month and date
- Error by days to expiry scatter plot
- Trend analysis

### 5. Automation

**Scheduler** (`lib/scheduler.py`):
- APScheduler-based daily automation
- Configurable scrape time
- Error logging
- Can be extended for notifications

## Database Schema

### futuresContracts
- `commodity`: "WTI" | "HH"
- `contractMonth`: "YYYY-MM"
- `contractSymbol`: string
- `settlementPrice`: number
- `settlementDate`: "YYYY-MM-DD"
- `volume`: number (optional)
- `openInterest`: number (optional)
- `source`: "CME" | "EXCEL"
- `createdAt`: ISO timestamp
- `updatedAt`: ISO timestamp

### spotPrices
- `commodity`: "WTI" | "HH"
- `price`: number
- `date`: "YYYY-MM-DD"
- `source`: "EIA" | "EXCEL"
- `createdAt`: ISO timestamp

### errorCalculations
- `futuresContractId`: string (reference)
- `spotPriceId`: string (reference)
- `contractMonth`: "YYYY-MM"
- `commodity`: "WTI" | "HH"
- `futuresPrice`: number
- `spotPrice`: number
- `absoluteError`: number
- `percentageError`: number
- `date`: "YYYY-MM-DD"
- `daysToExpiry`: number (optional)
- `createdAt`: ISO timestamp

### scrapeLogs
- `source`: "CME" | "EIA" | "SCHEDULER"
- `commodity`: "WTI" | "HH" | "BOTH"
- `status`: "success" | "failed"
- `recordsScraped`: number
- `errorMessage`: string (optional)
- `scrapeDate`: ISO timestamp
- `createdAt`: ISO timestamp

## Error Handling

- Scrapers include retry logic and error logging
- Excel import validates data before insertion
- Error calculations handle missing data gracefully
- All database operations include error handling
- Scrape logs track failures for debugging

## Future Enhancements

1. **Time Series Predictions**
   - ML models for price forecasting
   - Compare predictions vs actuals
   - Model performance metrics

2. **Alert System**
   - Notifications when errors exceed thresholds
   - Email/SMS alerts
   - Dashboard warnings

3. **API Endpoints**
   - REST API for external integrations
   - Webhook support
   - Data export endpoints

4. **Advanced Analytics**
   - Volatility analysis
   - Correlation analysis
   - Contract roll analysis
   - Seasonal patterns

5. **Data Quality**
   - Data validation rules
   - Anomaly detection
   - Data quality scores

