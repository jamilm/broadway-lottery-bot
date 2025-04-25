# Broadway Lottery Bot

An automated script to enter Broadway play lotteries on the Rush Telecharge website (https://rush.telecharge.com/).

## Overview

This bot automatically logs into the Rush Telecharge website and enters all available play lotteries. It can be scheduled to run daily at a specified time.

## Features

- Automated login to Rush Telecharge
- Finds and enters all available play lotteries
- Configurable schedule for daily entries
- Randomized timing to appear more human-like
- Docker support for easy deployment
- Detailed logging for monitoring and debugging

## Requirements

- Docker (for containerized deployment)
- Python 3.9+ (for local development)
- A Rush Telecharge account

## Configuration

The bot is configured using a combination of the `config.yaml` file and environment variables.

### Environment Variables

Set the following environment variables for authentication and personal information:

```
TELECHARGE_USERNAME=your_username
TELECHARGE_PASSWORD=your_password
TELECHARGE_FIRST_NAME=your_first_name
TELECHARGE_LAST_NAME=your_last_name
TELECHARGE_EMAIL=your_email
TELECHARGE_ZIP_CODE=your_zip_code
TELECHARGE_PHONE=your_phone_number
```

### Config File

The `config.yaml` file contains additional configuration options:

- `schedule.time`: Time to run the lottery entries (24-hour format)
- `schedule.random_window_minutes`: Random window in minutes to vary the entry time
- `browser.headless`: Whether to run the browser in headless mode
- `browser.timeout`: Timeout in seconds for page loads
- `logging.level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Docker Deployment

1. Build the Docker image:
   ```
   docker build -t broadway-lottery-bot .
   ```

2. Run the container with environment variables:
   ```
   docker run -d \
     --name broadway-lottery \
     -e TELECHARGE_USERNAME=your_username \
     -e TELECHARGE_PASSWORD=your_password \
     -e TELECHARGE_FIRST_NAME=your_first_name \
     -e TELECHARGE_LAST_NAME=your_last_name \
     -e TELECHARGE_EMAIL=your_email \
     -e TELECHARGE_ZIP_CODE=your_zip_code \
     -e TELECHARGE_PHONE=your_phone_number \
     -v lottery-data:/app/data \
     broadway-lottery-bot
   ```

3. Check the logs:
   ```
   docker logs -f broadway-lottery
   ```

## Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your credentials (same variables as listed above)

3. Run the bot:
   ```
   python src/main.py
   ```

## Customization

The bot is designed to work with the current structure of the Rush Telecharge website. If the website changes, you may need to update the selectors in the `lottery_bot.py` file.

## Disclaimer

This bot is for educational purposes only. Please use responsibly and in accordance with the terms of service of the Rush Telecharge website.

## License

MIT
