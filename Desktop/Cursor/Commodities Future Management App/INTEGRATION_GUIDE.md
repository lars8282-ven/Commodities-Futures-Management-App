# InstantDB Integration Guide

## Overview

The `create-instant-app` command created a Next.js app structure with InstantDB integration. Since we're using Streamlit (Python), we need to integrate InstantDB differently.

## Current Setup

1. **Next.js App** (in `commodities-futures-management-app/`):
   - Contains InstantDB schema definition (`instant.schema.ts`)
   - Contains InstantDB permissions (`instant.perms.ts`)
   - Contains database initialization (`lib/db.ts`)
   - App ID: `a72f835b-06f6-4031-a6c2-9668bb3832bf`

2. **Streamlit App** (root directory):
   - Python-based application
   - Uses custom InstantDB client (`lib/instant_client.py`)

## Integration Options

### Option 1: Use InstantDB REST API (Current Implementation)

The current Python client (`lib/instant_client.py`) uses REST API calls. You'll need to:

1. **Verify InstantDB API endpoints**: Check InstantDB documentation for the actual REST API endpoints
2. **Update the client**: Modify `lib/instant_client.py` to match InstantDB's actual API structure
3. **Use the schema**: The schema in `instant.schema.ts` defines the entities you need to create

### Option 2: Use InstantDB JavaScript SDK via API Server

Create a Node.js API server that uses InstantDB's JavaScript SDK:

1. Create an API server (Express/Fastify) that:
   - Uses `@instantdb/react` or `@instantdb/node`
   - Exposes REST endpoints for your Python app
   - Handles all InstantDB operations

2. Update Python client to call this API server instead of InstantDB directly

### Option 3: Convert to Next.js (Future Option)

If you want to use the Next.js structure:
1. Move Streamlit logic to Next.js API routes
2. Use React components instead of Streamlit
3. Keep the existing InstantDB integration

## Schema Entities

The schema defines these entities (see `instant.schema.ts`):

1. **futuresContracts**: Futures settlement prices
2. **spotPrices**: Spot prices from EIA
3. **errorCalculations**: Calculated errors between futures and spot
4. **scrapeLogs**: Logs of scraping operations

## Environment Variables

Set these in your `.env` file:

```
NEXT_PUBLIC_INSTANT_APP_ID=a72f835b-06f6-4031-a6c2-9668bb3832bf
INSTANT_APP_ID=a72f835b-06f6-4031-a6c2-9668bb3832bf
INSTANT_API_KEY=your_api_key_here
```

## Next Steps

1. **Verify InstantDB API**: Check if InstantDB has a Python SDK or REST API documentation
2. **Update Python Client**: Modify `lib/instant_client.py` to work with InstantDB's actual API
3. **Test Connection**: Test the connection with a simple query
4. **Deploy Schema**: Ensure the schema entities are created in your InstantDB instance

## Resources

- InstantDB Docs: https://www.instantdb.com/docs
- InstantDB Dashboard: Check your InstantDB dashboard for API keys and endpoints
- Schema Definition: `commodities-futures-management-app/src/instant.schema.ts`

