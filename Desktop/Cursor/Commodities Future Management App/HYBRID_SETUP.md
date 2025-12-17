# Hybrid Setup: Streamlit + Next.js API Routes

## Architecture

This setup uses a hybrid approach:
- **Next.js App**: Provides API routes that interact with InstantDB
- **Streamlit App**: Python application that calls the Next.js API routes

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Streamlit │  HTTP   │  Next.js API │  SDK    │  InstantDB   │
│   (Python) │ ──────> │   Routes     │ ──────> │  Database   │
└────────────┘         └──────────────┘         └─────────────┘
```

## Setup Instructions

### 1. Start the Next.js API Server

```bash
cd commodities-futures-management-app
npm run dev
```

This will start the Next.js server on `http://localhost:3000` with API routes at:
- `http://localhost:3000/api/futures`
- `http://localhost:3000/api/spot`
- `http://localhost:3000/api/errors`

### 2. Configure Environment Variables

Create `.env` in the root directory:

```env
# InstantDB Configuration
NEXT_PUBLIC_INSTANT_APP_ID=a72f835b-06f6-4031-a6c2-9668bb3832bf
INSTANT_APP_ID=a72f835b-06f6-4031-a6c2-9668bb3832bf

# Next.js API URL (for Python client)
NEXTJS_API_URL=http://localhost:3000/api
```

### 3. Run the Streamlit App

```bash
# In the root directory
streamlit run app.py
```

The Streamlit app will automatically connect to the Next.js API routes.

## API Routes

### GET /api/futures
Query futures contracts.

**Query Parameters:**
- `commodity`: Filter by "WTI" or "HH"
- `contractMonth`: Filter by contract month (YYYY-MM)
- `startDate`: Start date filter
- `endDate`: End date filter

**Example:**
```bash
curl "http://localhost:3000/api/futures?commodity=WTI&startDate=2024-01-01"
```

### POST /api/futures
Create a new futures contract.

**Body:**
```json
{
  "commodity": "WTI",
  "contractMonth": "2024-12",
  "contractSymbol": "CLZ2024",
  "settlementPrice": 75.50,
  "settlementDate": "2024-12-15",
  "volume": 1000,
  "openInterest": 500,
  "source": "CME"
}
```

### GET /api/spot
Query spot prices.

**Query Parameters:**
- `commodity`: Filter by "WTI" or "HH"
- `startDate`: Start date filter
- `endDate`: End date filter

### POST /api/spot
Create a new spot price record.

**Body:**
```json
{
  "commodity": "WTI",
  "price": 75.00,
  "date": "2024-12-15",
  "source": "EIA"
}
```

### GET /api/errors
Query error calculations.

**Query Parameters:**
- `commodity`: Filter by "WTI" or "HH"
- `contractMonth`: Filter by contract month

### POST /api/errors
Create a new error calculation.

**Body:**
```json
{
  "futuresContractId": "abc123",
  "spotPriceId": "def456",
  "contractMonth": "2024-12",
  "commodity": "WTI",
  "futuresPrice": 75.50,
  "spotPrice": 75.00,
  "absoluteError": 0.50,
  "percentageError": 0.67,
  "date": "2024-12-15",
  "daysToExpiry": 10
}
```

## Python Client Usage

The Python client (`lib/instant_client.py`) automatically uses the Next.js API:

```python
from lib.instant_client import get_db

db = get_db()

# Query futures contracts
futures = db.query("futuresContracts", filters={"commodity": "WTI"})

# Insert a new futures contract
record = {
    "commodity": "WTI",
    "contractMonth": "2024-12",
    "settlementPrice": 75.50,
    "settlementDate": "2024-12-15",
    "source": "CME"
}
result = db.insert("futuresContracts", record)
```

## Deployment

### Option 1: Deploy Both Separately

1. **Deploy Next.js to Vercel:**
   ```bash
   cd commodities-futures-management-app
   vercel deploy
   ```

2. **Update Streamlit `.env`:**
   ```env
   NEXTJS_API_URL=https://your-app.vercel.app/api
   ```

3. **Deploy Streamlit to Streamlit Cloud or your server**

### Option 2: Deploy Next.js Only

Convert the Streamlit app to use Next.js React components instead.

## Troubleshooting

### Connection Issues

1. **Check Next.js is running:**
   ```bash
   curl http://localhost:3000/api/futures
   ```

2. **Check environment variables:**
   - Ensure `NEXT_PUBLIC_INSTANT_APP_ID` is set in Next.js
   - Ensure `NEXTJS_API_URL` is set in Streamlit `.env`

3. **Check CORS (if deploying):**
   - Next.js API routes should allow requests from your Streamlit domain

### API Errors

- Check Next.js console for errors
- Check InstantDB dashboard for connection issues
- Verify schema matches in `instant.schema.ts`

## Benefits of This Approach

1. **Best of Both Worlds**: Use Streamlit for data science UI, Next.js for InstantDB integration
2. **Separation of Concerns**: API layer separate from UI
3. **Easy to Scale**: Can add more API consumers later
4. **Type Safety**: TypeScript in Next.js, Python in Streamlit
5. **Real-time**: InstantDB's real-time features work through the API

