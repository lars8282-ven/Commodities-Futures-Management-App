"""
Main Streamlit application for CME Futures Scraper.
Simple interface to scrape WTI and HH futures data for a given date.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from lib.auth import check_authentication
from lib.db import get_db, save_futures_data, get_futures_data, data_exists_for_date, get_latest_scrape_date
from lib.scraper import CMEScraper

# Page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="CME Futures Scraper",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication check - restrict access to @tepuiv.com emails via OIDC
if not check_authentication():
    st.stop()  # Stop execution if not authenticated (login UI is shown by check_authentication)

# Initialize session state
if "db" not in st.session_state:
    try:
        st.session_state.db = get_db()
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {e}")
        st.info("Please check your .env file and ensure SUPABASE_URL and SUPABASE_KEY are set correctly.")
        st.stop()

if "scraper" not in st.session_state:
    st.session_state.scraper = CMEScraper(headless=True)

if "available_dates_wti" not in st.session_state:
    st.session_state.available_dates_wti = None

if "available_dates_hh" not in st.session_state:
    st.session_state.available_dates_hh = None

# Title
st.title("📊 CME Futures Settlement Data Scraper")
st.markdown("Scrape WTI (Crude Oil) and HH (Natural Gas) futures settlement data from CME Group")

# Sidebar
st.sidebar.header("Scrape Settings")

# Fetch available dates
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_available_dates_cached(commodity: str):
    """Get available dates from CME (cached)."""
    try:
        scraper = CMEScraper(headless=True)
        dates = scraper.get_available_dates(commodity)
        scraper._close_driver()
        return dates
    except Exception as e:
        st.sidebar.error(f"Error fetching available dates: {e}")
        return []

# Buttons to refresh available dates
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🔄 Refresh WTI Dates", use_container_width=True):
        st.session_state.available_dates_wti = get_available_dates_cached("WTI")
        st.rerun()

with col2:
    if st.button("🔄 Refresh HH Dates", use_container_width=True):
        st.session_state.available_dates_hh = get_available_dates_cached("HH")
        st.rerun()

# Get available dates
if st.session_state.available_dates_wti is None:
    with st.spinner("Loading available dates..."):
        st.session_state.available_dates_wti = get_available_dates_cached("WTI")

if st.session_state.available_dates_hh is None:
    with st.spinner("Loading available dates..."):
        st.session_state.available_dates_hh = get_available_dates_cached("HH")

# Combine available dates (union of both)
all_available_dates = {}
if st.session_state.available_dates_wti:
    for date_info in st.session_state.available_dates_wti:
        all_available_dates[date_info["date"]] = date_info["display"]
if st.session_state.available_dates_hh:
    for date_info in st.session_state.available_dates_hh:
        if date_info["date"] not in all_available_dates:
            all_available_dates[date_info["date"]] = date_info["display"]

# Date selection
if all_available_dates:
    # Sort dates (most recent first)
    sorted_dates = sorted(all_available_dates.keys(), reverse=True)
    
    # Create date options for selectbox
    date_options = {display: date for date, display in all_available_dates.items()}
    sorted_displays = [all_available_dates[date] for date in sorted_dates]
    
    selected_display = st.sidebar.selectbox(
        "Select Date (Available from CME)",
        options=sorted_displays,
        index=0 if sorted_displays else None
    )
    
    selected_date = date_options.get(selected_display) if selected_display else None
    
    st.sidebar.info(f"📅 Available dates: {len(sorted_dates)} business days")
else:
    st.sidebar.warning("⚠️ Could not load available dates. Click refresh buttons above.")
    # Fallback to date picker
    selected_date = st.sidebar.date_input(
        "Select Date",
        value=datetime.now() - timedelta(days=1),
        max_value=datetime.now()
    ).strftime("%Y-%m-%d")

date_str = selected_date

# Check if data already exists
if date_str:
    st.sidebar.subheader("Data Status")
    wti_exists = data_exists_for_date(date_str, "WTI")
    hh_exists = data_exists_for_date(date_str, "HH")
    
    if wti_exists:
        st.sidebar.success("✓ WTI data exists")
    else:
        st.sidebar.info("○ WTI data not found")
    
    if hh_exists:
        st.sidebar.success("✓ HH data exists")
    else:
        st.sidebar.info("○ HH data not found")

# Scrape buttons
st.sidebar.subheader("Actions")
col1, col2 = st.sidebar.columns(2)

with col1:
    scrape_wti = st.button("Scrape WTI", type="primary", use_container_width=True)

with col2:
    scrape_hh = st.button("Scrape HH", type="primary", use_container_width=True)

scrape_both = st.sidebar.button("Scrape Both", type="secondary", use_container_width=True)

# Main content area
if scrape_wti or scrape_both:
    with st.spinner("Scraping WTI data (using prior business day)..."):
        try:
            scraper = CMEScraper(headless=True)
            records = scraper.scrape_wti()
            scraper._close_driver()
            
            if records:
                # Extract date from first record
                scrape_date = records[0].get("date", "unknown") if records else "unknown"
                
                # Save to database
                result = save_futures_data(records)
                
                # Show save results
                if result.get("saved", 0) > 0:
                    st.success(f"✅ Scraped {len(records)} WTI contracts for {scrape_date}. Saved: {result['saved']}, Skipped: {result['skipped']}")
                elif result.get("skipped", 0) == len(records):
                    st.info(f"ℹ️ All {len(records)} WTI contracts for {scrape_date} already exist in database (skipped).")
                else:
                    st.warning(f"⚠️ Scraped {len(records)} WTI contracts for {scrape_date}, but only {result.get('saved', 0)} were saved. Skipped: {result.get('skipped', 0)}")
                
                # Show errors if any
                if result.get("errors"):
                    with st.expander(f"⚠️ Database Errors ({result.get('error_count', 0)} errors)"):
                        for error in result["errors"]:
                            st.error(error)
                        if result.get("error_count", 0) > len(result["errors"]):
                            st.caption(f"... and {result.get('error_count', 0) - len(result['errors'])} more errors")
                
                st.rerun()
            else:
                st.warning("⚠️ No WTI data found. The table may be empty or the page may not have loaded correctly.")
                st.info("💡 Check the terminal output for Selenium errors or network issues.")
        except Exception as e:
            st.error(f"❌ Error scraping WTI: {e}")
            st.exception(e)
            st.info("💡 Check the terminal output for detailed error messages.")

if scrape_hh or scrape_both:
    with st.spinner("Scraping HH data (using prior business day)..."):
        try:
            scraper = CMEScraper(headless=True)
            records = scraper.scrape_henry_hub()
            scraper._close_driver()
            
            if records:
                # Extract date from first record
                scrape_date = records[0].get("date", "unknown") if records else "unknown"
                
                # Save to database
                result = save_futures_data(records)
                
                # Show save results
                if result.get("saved", 0) > 0:
                    st.success(f"✅ Scraped {len(records)} HH contracts for {scrape_date}. Saved: {result['saved']}, Skipped: {result['skipped']}")
                elif result.get("skipped", 0) == len(records):
                    st.info(f"ℹ️ All {len(records)} HH contracts for {scrape_date} already exist in database (skipped).")
                else:
                    st.warning(f"⚠️ Scraped {len(records)} HH contracts for {scrape_date}, but only {result.get('saved', 0)} were saved. Skipped: {result.get('skipped', 0)}")
                
                # Show errors if any
                if result.get("errors"):
                    with st.expander(f"⚠️ Database Errors ({result.get('error_count', 0)} errors)"):
                        for error in result["errors"]:
                            st.error(error)
                        if result.get("error_count", 0) > len(result["errors"]):
                            st.caption(f"... and {result.get('error_count', 0) - len(result['errors'])} more errors")
                
                st.rerun()
            else:
                st.warning("⚠️ No HH data found. The table may be empty or the page may not have loaded correctly.")
                st.info("💡 Check the terminal output for Selenium errors or network issues.")
        except Exception as e:
            st.error(f"❌ Error scraping HH: {e}")
            st.exception(e)
            st.info("💡 Check the terminal output for detailed error messages.")

# Display data tables
st.header("📋 Data Tables")

# Get latest dates from database
latest_wti_date = get_latest_scrape_date("WTI")
latest_hh_date = get_latest_scrape_date("HH")

# Filter options
col1, col2 = st.columns(2)
with col1:
    show_commodity = st.selectbox("Commodity", ["All", "WTI", "HH"], key="display_commodity")

with col2:
    # Show latest date selector
    latest_date = latest_wti_date or latest_hh_date
    if latest_date:
        st.info(f"📅 Showing data for: {latest_date}")

# Get and display data - show latest date by default
display_date = latest_wti_date or latest_hh_date
if display_date:
    commodity_filter = None if show_commodity == "All" else show_commodity
    data = get_futures_data(display_date, commodity_filter)
    
    if data:
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Reorder columns for better display
        column_order = ["date", "commodity", "month", "contract_expiry_date", "open", "high", "low", "last", "change", "settle", "est_volume", "prior_day_oi"]
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        # Format numeric columns
        numeric_cols = ["open", "high", "low", "last", "change", "settle", "est_volume", "prior_day_oi"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # Display table
        st.dataframe(df, use_container_width=True, height=400)
        
        # Summary stats
        st.subheader("Summary Statistics")
        if show_commodity == "All":
            summary = df.groupby("commodity").agg({
                "settle": ["count", "mean", "min", "max"],
                "est_volume": "sum",
                "prior_day_oi": "sum"
            }).round(2)
            st.dataframe(summary, use_container_width=True)
        else:
            if "settle" in df.columns:
                st.metric("Number of Contracts", len(df))
                st.metric("Average Settlement", f"${df['settle'].mean():.2f}" if not df['settle'].isna().all() else "N/A")
                if "est_volume" in df.columns and not df['est_volume'].isna().all():
                    st.metric("Total Volume", f"{df['est_volume'].sum():,.0f}")
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"futures_{display_date}_{show_commodity.lower()}.csv",
            mime="text/csv"
        )
    else:
        st.info(f"ℹ️ No data found for {display_date}. Use the sidebar to scrape data.")
else:
    st.info("ℹ️ No data in database yet. Use the sidebar to scrape data.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This app scrapes futures settlement data from CME Group websites:\n\n"
    "- WTI: Light Sweet Crude Oil\n"
    "- HH: Henry Hub Natural Gas\n\n"
    "**Auto-Scrape:** Uses the prior business day (default on CME page).\n\n"
    "**Best Time:** Run before 6 PM EST to get today's settlement data."
)
