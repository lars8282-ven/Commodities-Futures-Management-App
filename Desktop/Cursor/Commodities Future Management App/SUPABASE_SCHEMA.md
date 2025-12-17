# Supabase Schema Setup Guide

## Create the `futures_settlements` Table

1. Go to your Supabase project dashboard: https://app.supabase.com
2. Navigate to **SQL Editor**
3. Run the following SQL to create the table:

```sql
-- Create futures_settlements table
CREATE TABLE IF NOT EXISTS futures_settlements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    date DATE NOT NULL,
    commodity VARCHAR(10) NOT NULL CHECK (commodity IN ('WTI', 'HH')),
    month VARCHAR(50) NOT NULL,
    contract_expiry_date DATE,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    last NUMERIC,
    change NUMERIC,
    settle NUMERIC,
    est_volume NUMERIC,
    prior_day_oi NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint to prevent duplicates
    UNIQUE(date, commodity, month)
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_futures_settlements_date ON futures_settlements(date);
CREATE INDEX IF NOT EXISTS idx_futures_settlements_commodity ON futures_settlements(commodity);
CREATE INDEX IF NOT EXISTS idx_futures_settlements_date_commodity ON futures_settlements(date, commodity);
CREATE INDEX IF NOT EXISTS idx_futures_settlements_expiry_date ON futures_settlements(contract_expiry_date);
```

-- Add contract_expiry_date column to existing tables (run this if table already exists)
-- ALTER TABLE futures_settlements ADD COLUMN IF NOT EXISTS contract_expiry_date DATE;
```

## Enable Row Level Security (RLS)

If you want to enable RLS for additional security:

```sql
-- Enable RLS
ALTER TABLE futures_settlements ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust based on your security needs)
CREATE POLICY "Allow all operations" ON futures_settlements
    FOR ALL
    USING (true)
    WITH CHECK (true);
```

**Note:** For a simple scraper app, you may want to keep RLS disabled or use service role key for full access.

## Verify Table Creation

After running the SQL, verify the table was created:

1. Go to **Table Editor** in Supabase dashboard
2. You should see `futures_settlements` table
3. Check that all columns are present with correct types

## Get Your Supabase Credentials

1. Go to **Project Settings** > **API**
2. Copy:
   - **Project URL** → Use as `SUPABASE_URL` in `.env`
   - **anon public** key → Use as `SUPABASE_KEY` in `.env` (or use `service_role` key for admin access)

