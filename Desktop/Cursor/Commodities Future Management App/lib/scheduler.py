"""
Daily automated scraping scheduler.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import os
from datetime import datetime
from lib.scraper import CMEScraper
from lib.eia_scraper import EIAScraper
from lib.error_calculator import ErrorCalculator

class ScrapingScheduler:
    """Scheduler for daily automated scraping and error calculation."""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.cme_scraper = CMEScraper(headless=True)
        self.eia_scraper = EIAScraper()
        self.error_calculator = ErrorCalculator()
    
    def daily_scrape_job(self):
        """Job to run daily scraping and error calculation."""
        print(f"Starting daily scrape job at {datetime.now()}")
        
        try:
            # Scrape CME futures
            print("Scraping CME futures...")
            cme_results = self.cme_scraper.scrape_and_save()
            print(f"CME scrape complete: {cme_results}")
            
            # Scrape EIA spot prices
            print("Scraping EIA spot prices...")
            eia_results = self.eia_scraper.scrape_and_save()
            print(f"EIA scrape complete: {eia_results}")
            
            # Calculate errors
            print("Calculating errors...")
            error_results = self.error_calculator.calculate_errors()
            print(f"Error calculation complete: {error_results}")
            
            print(f"Daily scrape job completed at {datetime.now()}")
            
        except Exception as e:
            print(f"Error in daily scrape job: {e}")
            # Log error to database
            from lib.instant_client import get_db
            db = get_db()
            db.insert("scrapeLogs", {
                "source": "SCHEDULER",
                "commodity": "BOTH",
                "status": "failed",
                "recordsScraped": 0,
                "errorMessage": str(e),
                "scrapeDate": datetime.now().isoformat(),
                "createdAt": datetime.now().isoformat(),
            })
    
    def start(self):
        """Start the scheduler."""
        # Get scrape time from environment
        scrape_time = os.getenv("DAILY_SCRAPE_TIME", "18:00")
        timezone = os.getenv("TIMEZONE", "America/New_York")
        
        hour, minute = map(int, scrape_time.split(":"))
        
        # Schedule daily job
        self.scheduler.add_job(
            self.daily_scrape_job,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=timezone),
            id="daily_scrape",
            name="Daily Futures and Spot Price Scraping",
            replace_existing=True,
        )
        
        self.scheduler.start()
        print(f"Scheduler started. Daily scrape scheduled for {scrape_time} {timezone}")
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        print("Scheduler stopped")

# Global scheduler instance
_scheduler: ScrapingScheduler = None

def get_scheduler() -> ScrapingScheduler:
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = ScrapingScheduler()
    return _scheduler

