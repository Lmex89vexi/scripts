import requests
import time
from loguru import logger

# Configure loguru with local timezone and custom format
logger.remove()  # Remove default handler
logger.add(
    lambda msg: print(msg, end=""),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    colorize=True,
)

# Configuration
#url = "https://jju1k48fvd.execute-api.us-east-2.amazonaws.com/QA/v1/solicitud/catalogo-visitor-keys"
url = "https://solbackend-qa.intravexi.mx/v1/solicitud/emails/luismexcache@vexi.mx/brandings"
total_requests = 1000
duration_minutes = 10

# Calculate the delay (in seconds) to evenly space the requests
duration_seconds = duration_minutes * 60
delay = duration_seconds / total_requests

logger.info(f"Target: {url}")
logger.info(f"Sending {total_requests} requests over {duration_minutes} minutes.")
logger.info(f"Interval: {delay} seconds between requests.")

for i in range(total_requests):
    try:
        # Send the GET request
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "x-api-key": "Ox679bkqkq7J5Iub9fc3L8SWDSNvqj6e8CIuQEdA",
            },
            verify=False
        )

        # Log the progress and status code
        logger.success(
            f"Request {i + 1}/{total_requests}: Status {response.status_code}"
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Request {i + 1}/{total_requests}: Error - {e}")

    # Wait for the calculated delay, but do not sleep after the very last request
    if i < total_requests - 1:
        time.sleep(delay)

logger.info("Completed.")
