#!/usr/bin/env python3
"""
Test script for the Broadway Lottery Bot.
This script runs the bot once without scheduling.
"""
import os
import sys
import yaml
from dotenv import load_dotenv
from loguru import logger

from src.browser import BrowserHandler
from src.lottery_bot import LotteryBot


def setup_logging():
    """Set up basic logging for the test script."""
    logger.remove()  # Remove default handler
    logger.add(sys.stderr, level="INFO")
    logger.add("data/test_bot.log", rotation="1 day", level="DEBUG")
    
    # Create screenshots directory
    os.makedirs("data/screenshots", exist_ok=True)


def load_config():
    """Load configuration from YAML file."""
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        sys.exit(1)


def main():
    """Main entry point for the test script."""
    # Set up logging
    setup_logging()
    
    # Load environment variables (if any)
    load_dotenv()
    
    # Load configuration
    config = load_config()
    
    # Override config with environment variables if set
    if os.environ.get('TELECHARGE_USERNAME'):
        config['credentials']['username'] = os.environ.get('TELECHARGE_USERNAME')
    if os.environ.get('TELECHARGE_PASSWORD'):
        config['credentials']['password'] = os.environ.get('TELECHARGE_PASSWORD')
    
    # Personal info
    if os.environ.get('TELECHARGE_FIRST_NAME'):
        config['personal_info']['first_name'] = os.environ.get('TELECHARGE_FIRST_NAME')
    if os.environ.get('TELECHARGE_LAST_NAME'):
        config['personal_info']['last_name'] = os.environ.get('TELECHARGE_LAST_NAME')
    if os.environ.get('TELECHARGE_EMAIL'):
        config['personal_info']['email'] = os.environ.get('TELECHARGE_EMAIL')
    if os.environ.get('TELECHARGE_ZIP_CODE'):
        config['personal_info']['zip_code'] = os.environ.get('TELECHARGE_ZIP_CODE')
    if os.environ.get('TELECHARGE_PHONE'):
        config['personal_info']['phone'] = os.environ.get('TELECHARGE_PHONE')
    
    logger.info("Starting Broadway Lottery Bot test")
    
    try:
        # Set up browser handler
        browser_handler = BrowserHandler(config)
        
        # Create lottery bot
        lottery_bot = LotteryBot(browser_handler, config)
        
        # Run the lottery entries
        success = lottery_bot.run_lottery_entries()
        
        if success:
            logger.info("Test completed successfully!")
        else:
            logger.error("Test failed to complete lottery entries")
            
    except Exception as e:
        logger.error(f"Error during test: {e}")
    
    logger.info("Test finished")


if __name__ == "__main__":
    main()
