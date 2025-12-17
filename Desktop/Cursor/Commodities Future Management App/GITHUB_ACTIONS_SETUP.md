# GitHub Actions Setup Guide

This guide explains how to set up GitHub Actions for daily automated scraping of CME futures data.

## Overview

GitHub Actions runs your scraper automatically every day at 6:00 PM UTC (configurable). The scraper:
- Fetches WTI and HH futures data from CME Group
- Saves the data to your Supabase database
- Skips data that already exists (no duplicates)

## Prerequisites

1. Your code is pushed to GitHub
2. You have a Supabase account and credentials
3. GitHub Actions is enabled on your repository (enabled by default)

## Step 1: Add Secrets to GitHub

1. Go to your GitHub repository
2. Click **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** > **Actions**
4. Click **New repository secret**

Add these two secrets:

### Secret 1: SUPABASE_URL
- **Name:** `SUPABASE_URL`
- **Value:** Your Supabase project URL (e.g., `https://xxxxx.supabase.co`)

### Secret 2: SUPABASE_KEY
- **Name:** `SUPABASE_KEY`
- **Value:** Your Supabase anon/public key (starts with `eyJ...`)

**Important:** 
- Keep these secrets secure - never commit them to your repository
- Only users with repository access can view secrets
- Secrets are encrypted and never shown in logs

## Step 2: Verify Workflow File

The workflow file is located at:
```
.github/workflows/daily-scraper.yml
```

It should already be in your repository. Verify it exists and has the correct schedule.

## Step 3: Test the Workflow

### Option A: Manual Trigger (Recommended for First Test)

1. Go to your GitHub repository
2. Click **Actions** tab (top menu)
3. In the left sidebar, click **Daily Scraper**
4. Click **Run workflow** button (top right)
5. Select branch: `master` (or your main branch)
6. Click **Run workflow**

The workflow will start running. You can watch it in real-time:
- Click on the running workflow
- Click on the `scrape` job
- Expand steps to see logs

### Option B: Wait for Scheduled Run

The workflow runs automatically at 6:00 PM UTC daily. You can verify it ran by:
1. Going to **Actions** tab
2. Looking for a workflow run with the name "Daily Scraper"
3. Green checkmark = success, red X = failure

## Step 4: Monitor Workflow Runs

### Viewing Logs

1. Go to **Actions** tab
2. Click on any workflow run
3. Click on the `scrape` job
4. Expand steps to see detailed logs

### Understanding Logs

- **Checkout repository**: Downloads your code ✅
- **Set up Python**: Sets up Python environment ✅
- **Install system dependencies**: Installs Chrome/Chromium ✅
- **Install Python dependencies**: Installs packages from requirements.txt ✅
- **Run daily scraper**: Executes your scraper ✅

Look for output like:
```
WTI: Scraped 45 contracts for 2025-01-15, Saved: 45
HH: Scraped 38 contracts for 2025-01-15, Saved: 38
```

## Customizing the Schedule

Edit `.github/workflows/daily-scraper.yml` and change the cron schedule:

```yaml
schedule:
  - cron: '0 18 * * *'  # Daily at 6:00 PM UTC
```

### Cron Syntax

Format: `minute hour day month weekday`

Examples:
- `'0 18 * * *'` - Daily at 6:00 PM UTC
- `'0 14 * * *'` - Daily at 2:00 PM UTC (10 AM EST)
- `'0 20 * * 1-5'` - Weekdays (Mon-Fri) at 8:00 PM UTC
- `'0 0 * * 1'` - Every Monday at midnight UTC

**Time Zone Note:** GitHub Actions uses UTC. Convert your desired time to UTC:
- EST is UTC-5 (winter)
- EDT is UTC-4 (summer)
- PST is UTC-8 (winter)
- PDT is UTC-7 (summer)

Example: 6 PM EST = 11 PM UTC (winter) or 10 PM UTC (summer)

## Troubleshooting

### Workflow Fails: "Chrome/Chromium not found"

**Solution:** The workflow already installs Chrome. If you see this error, check:
1. The "Install system dependencies" step completed successfully
2. All system packages installed without errors

### Workflow Fails: "SUPABASE_URL not found"

**Solution:**
1. Go to repository Settings > Secrets and variables > Actions
2. Verify `SUPABASE_URL` secret exists
3. Check spelling (case-sensitive)
4. Re-run the workflow

### Workflow Fails: "Authentication failed"

**Solution:**
1. Verify `SUPABASE_KEY` secret is correct
2. Check that the key is the anon/public key (not service_role key)
3. Ensure your Supabase project is active

### Workflow Succeeds But No Data Saved

**Possible causes:**
1. Data already exists (check logs for "skipped" messages - this is normal)
2. Scraper couldn't find data on CME website (check logs for "No data found")
3. Date selection issue (scraper uses "prior business day" by default)

**Debug:**
- Check workflow logs for detailed error messages
- Look for "Error scraping WTI" or "Error scraping HH" in logs
- Verify CME website is accessible

### Workflow Runs But Takes Too Long

**Normal:** The workflow can take 5-10 minutes:
- Installing dependencies: ~2-3 minutes
- Scraping WTI: ~1-2 minutes
- Scraping HH: ~1-2 minutes
- Saving to database: ~30 seconds

**If it times out (>30 minutes):**
- Check logs for hanging operations
- Verify CME website is responding
- Check Supabase connection

### Manual Scraping Still Works Locally

**This is expected!** The GitHub Actions workflow is for automated daily scraping. When you run the app locally, you can still scrape manually using the buttons in the Streamlit app.

## Email Notifications

GitHub will email you when:
- Workflow fails (if you have notifications enabled)
- Workflow succeeds (optional, can be enabled in Settings)

To enable email notifications:
1. Go to GitHub Settings (your account, not repository)
2. Notifications > Actions
3. Enable "Workflow runs" notifications

## Cost

**GitHub Actions is FREE for public repositories!**

For private repositories:
- **Free tier:** 2,000 minutes/month (plenty for daily scraping)
- **Each run:** ~5-10 minutes
- **Daily runs:** ~150-300 minutes/month
- **Remaining:** ~1,700+ minutes for other actions

You won't be charged unless you exceed 2,000 minutes/month on a private repository.

## Disabling the Workflow

To temporarily disable automated scraping:
1. Go to `.github/workflows/daily-scraper.yml`
2. Comment out the `schedule` section:
   ```yaml
   # schedule:
   #   - cron: '0 18 * * *'
   ```
3. Commit and push

To re-enable, uncomment the schedule section.

## Need Help?

- Check workflow logs in the Actions tab
- Verify secrets are set correctly
- Test the scraper locally first
- Check Supabase dashboard to see if data is being saved

