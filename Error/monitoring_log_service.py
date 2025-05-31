import requests
import logging

def setup_logging(log_file: str = "logs.txt"):
    """Sets up logging to a file."""
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def log_error(message: str):
    """Logs an error message to the log file."""
    logging.error(message)


def notify_ntfy(message: str, topic: str = "netDev"):
    """Sends a notification to the ntfy topic."""
    url = f"https://ntfy.sh/{topic}"
    headers = {"Title": "NetGuardian Notification"}
    response = requests.post(url, data=message.encode("utf-8"), headers=headers)
    response.raise_for_status()


setup_logging()