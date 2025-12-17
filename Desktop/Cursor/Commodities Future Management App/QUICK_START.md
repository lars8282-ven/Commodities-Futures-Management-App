# Quick Start Guide

## Prerequisites
- Node.js and npm installed
- Python 3.8+ with virtual environment set up
- InstantDB account with App ID: `a72f835b-06f6-4031-a6c2-9668bb3832bf`

## Step 1: Create Environment Files

### For Next.js (create this file):
**File:** `commodities-futures-management-app/.env.local`

```env
NEXT_PUBLIC_INSTANT_APP_ID=a72f835b-06f6-4031-a6c2-9668bb3832bf
INSTANT_ADMIN_TOKEN=your_admin_token_here
```

**Note:** You need to get the admin token from your InstantDB dashboard. Go to your InstantDB project settings to find the admin token.

### For Streamlit (create this file):
**File:** `.env` (in root directory)

```env
INSTANT_APP_ID=a72f835b-06f6-4031-a6c2-9668bb3832bf
NEXTJS_API_URL=http://localhost:3000/api
SCRAPE_RATE_LIMIT_SECONDS=2
DAILY_SCRAPE_TIME=18:00
TIMEZONE=America/New_York
```

## Step 2: Start the Servers

### Option A: Use the Startup Script
```powershell
.\start-app.ps1
```

### Option B: Manual Start

**Terminal 1 - Next.js API:**
```powershell
cd "commodities-futures-management-app"
npm run dev
```

**Terminal 2 - Streamlit App:**
```powershell
# In the root directory
.\venv\Scripts\streamlit.exe run app.py
```

## Step 3: Access the Apps

- **Streamlit Dashboard:** http://localhost:8501
- **Next.js API:** http://localhost:3000/api/futures

## Troubleshooting

### API Returns 500 Error
1. Check that `.env.local` exists in `commodities-futures-management-app/` directory
2. Verify `NEXT_PUBLIC_INSTANT_APP_ID` is set correctly
3. Restart the Next.js server after creating/updating `.env.local`
4. Check the Next.js console for detailed error messages

### Streamlit Can't Connect to API
1. Ensure Next.js is running on port 3000
2. Check that `NEXTJS_API_URL` is set in `.env` file
3. Test the API directly: `curl http://localhost:3000/api/futures`

### InstantDB Connection Issues
1. Verify your InstantDB App ID is correct
2. Check that your InstantDB schema matches `instant.schema.ts`
3. Ensure your InstantDB account is active

## Notes

- The Next.js server must be running before starting Streamlit
- Environment variables in `.env.local` are loaded automatically by Next.js
- The Streamlit app connects to the Next.js API, which then connects to InstantDB

