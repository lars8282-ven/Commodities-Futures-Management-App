# InstantDB Setup Instructions

## Important Note

The current implementation uses a REST API approach for InstantDB. However, InstantDB primarily provides JavaScript/TypeScript SDKs. You have two options:

### Option 1: Use InstantDB JavaScript SDK (Recommended)

If InstantDB doesn't have a Python SDK, you may need to:
1. Create a Node.js/TypeScript API server that uses `@instantdb/react` or `@instantdb/node`
2. Have your Streamlit app call this API server
3. Or use InstantDB's GraphQL API directly if available

### Option 2: Use Alternative Database

Consider using:
- **PostgreSQL** with `psycopg2` or `sqlalchemy`
- **SQLite** for simpler setup
- **Supabase** (PostgreSQL with REST API)
- **Firebase** (has Python SDK)

### Option 3: Check for Python SDK

Check if InstantDB has released a Python SDK:
- Visit https://instantdb.com/docs
- Check their GitHub for Python packages
- Contact InstantDB support

## Current Implementation

The `lib/instant_client.py` file implements a REST API client. You'll need to:

1. Verify InstantDB's actual API endpoints
2. Update the base URL and authentication method
3. Adjust the query/insert/update/delete methods to match InstantDB's API

## Schema Entities

The app expects these entities in InstantDB:

1. **futuresContracts**
   - commodity (string)
   - contractMonth (string)
   - contractSymbol (string)
   - settlementPrice (number)
   - settlementDate (string)
   - volume (number, optional)
   - openInterest (number, optional)
   - source (string)
   - createdAt (string)
   - updatedAt (string)

2. **spotPrices**
   - commodity (string)
   - price (number)
   - date (string)
   - source (string)
   - createdAt (string)

3. **errorCalculations**
   - futuresContractId (string)
   - spotPriceId (string)
   - contractMonth (string)
   - commodity (string)
   - futuresPrice (number)
   - spotPrice (number)
   - absoluteError (number)
   - percentageError (number)
   - date (string)
   - daysToExpiry (number, optional)
   - createdAt (string)

4. **scrapeLogs**
   - source (string)
   - commodity (string)
   - status (string)
   - recordsScraped (number)
   - errorMessage (string, optional)
   - scrapeDate (string)
   - createdAt (string)

## Environment Variables

Set these in your `.env` file:

```
INSTANT_APP_ID=your_app_id_here
INSTANT_API_KEY=your_api_key_here
```

