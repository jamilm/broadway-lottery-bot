"""
Broadway Lottery Bot - Main entry point for the application.
"""
import os
import sys
import time
import yaml
import random
import schedule
from datetime import datetime, timedelta
from dotenv import load_dotenv
from loguru import logger

from browser import BrowserHandler
from lottery_bot import LotteryBot


def setup_logging(config):
    """Set up logging configuration."""
    log_level = config['logging']['level']
    log_file = config['logging']['file']
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logger
    logger.remove()  # Remove default handler
    logger.add(sys.stderr, level=log_level)
    logger.add(log_file, rotation="1 day", retention="7 days", level=log_level)
    
    logger.info(f"Logging initialized at level {log_level}")


def load_config():
    """Load configuration from YAML file and environment variables."""
    # Load config file
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        sys.exit(1)
    
    # Load environment variables
    load_dotenv()
    
    # Override config with environment variables
    config['credentials']['username'] = os.environ.get('TELECHARGE_USERNAME', config['credentials']['username'])
    config['credentials']['password'] = os.environ.get('TELECHARGE_PASSWORD', config['credentials']['password'])
    
    # Validate required configuration
    if not config['credentials']['username'] or not config['credentials']['password']:
        logger.error("Missing required credentials. Set TELECHARGE_USERNAME and TELECHARGE_PASSWORD environment variables.")
        sys.exit(1)
    
    return config


def run_lottery_entries(config):
    """Run the lottery entry process."""
    try:
        # Set up browser handler
        browser_handler = BrowserHandler(config)
        
        # Create lottery bot
        lottery_bot = LotteryBot(browser_handler, config)
        
        # Run the lottery entries
        success = lottery_bot.run_lottery_entries()
        
        if success:
            logger.info("Lottery entries completed successfully")
        else:
            logger.error("Failed to complete lottery entries")
            
    except Exception as e:
        logger.error(f"Error during lottery entry process: {e}")


def schedule_lottery_entries(config):
    """Schedule the lottery entries to run at the configured time."""
    scheduled_time = config['schedule']['time']
    random_window = config['schedule']['random_window_minutes']
    
    logger.info(f"Scheduling lottery entries for {scheduled_time} with {random_window} minute random window")
    
    def job():
        # Add random delay within the configured window to appear more human-like
        if random_window > 0:
            delay_minutes = random.randint(0, random_window)
            logger.info(f"Adding random delay of {delay_minutes} minutes")
            time.sleep(delay_minutes * 60)
        
        run_lottery_entries(config)
    
    # Schedule the job
    schedule.every().day.at(scheduled_time).do(job)
    
    # Also run once immediately if this is the first run
    first_run_file = "data/first_run_completed"
    if not os.path.exists(first_run_file):
        logger.info("First run detected, running lottery entries immediately")
        job()
        
        # Create the first run file
        os.makedirs(os.path.dirname(first_run_file), exist_ok=True)
        with open(first_run_file, 'w') as f:
            f.write(datetime.now().isoformat())


def main():
    """Main entry point for the application."""
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Load configuration
    config = load_config()
    
    # Set up logging
    setup_logging(config)
    
    logger.info("Broadway Lottery Bot starting up")
    
    # Schedule lottery entries
    schedule_lottery_entries(config)
    
    # Keep the script running
    logger.info("Entering main loop")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    main()
