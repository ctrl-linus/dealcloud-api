import requests
import os
from datetime import datetime, timedelta, timezone
import logging.handlers

# System variables
DEALCLOUD_SITE = os.getenv("DEALCLOUD_SITE")
API_CLIENT_ID = os.getenv("DEALCLOUD_CLIENT_ID")
API_CLIENT_SECRET = os.getenv("DEALCLOUD_CLIENT_SECRET")

API_ENDPOINT_TOKEN = "/api/rest/v1/oauth/token"
API_ENDPOINT_USER_ACTIVITY = "/api/rest/v1/management/user/activity"

LOG_OUTPUT_DIR = "./logs/"
SYSLOG_SERVER = "127.0.0.1"
SYSLOG_PORT = 1234

# Set up syslog output
syslog_handler = logging.handlers.SysLogHandler(address=(SYSLOG_SERVER, SYSLOG_PORT))
syslog_formatter = logging.Formatter('%(message)s')
syslog_handler.setFormatter(syslog_formatter)
syslogger = logging.getLogger(__name__)
syslogger = logging.getLogger('SysLogger')


# Set up HTTP request session
session = requests.Session()


def get_token():
    """Fetch a new Bearer token for API authentication.

    The token is required for API access and expires after 15 minutes.
    The scope must be `user_management` for User Activity log access.

    Returns:
        str: The API access token.
    Raises:
        requests.HTTPError: If the request fails.
        KeyError: If the response does not contain an access token.
    """
    session = requests.Session()
    url = f"https://{DEALCLOUD_SITE}{API_ENDPOINT_TOKEN}"

    response = session.post(
        url,
        data={"scope": "user_management", "grant_type": "client_credentials"},
        auth=(API_CLIENT_ID, API_CLIENT_SECRET),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    response.raise_for_status()

    try:
        return response.json()["access_token"]
    except KeyError as e:
        raise KeyError(f"Missing 'access_token' in response: {response.text}") from e


def get_user_activity(
    token: str, 
    user_ids: list[int] = None, 
    date_from: str = None,
    date_to: str = None,
    activity: int = None, 
    source: int = None,
    export_data_type: int = None,
    page_number: int = None,
    page_size: int = None
) -> dict:
    """Fetch user activity from the API.

    Args:
        token (str): Bearer token from `get_token()`.
        user_ids (list[int], optional): List of user IDs to filter by. Defaults to None.
        date_from (str, optional): Start date (max 90 days ago). Defaults to None.
        date_to (str, optional): End date (at least 1 day after `date_from`). Defaults to None.
        activity (int, optional): Activity type filter. Defaults to None.
        source (int, optional): Source type filter. Defaults to None.
        export_data_type (int, optional): Filter for export data (requires `activity=8`). Defaults to None.
        page_number (int, optional): Page number (default 1). Defaults to 1.
        page_size (int, optional): Number of records per page (default 10). Defaults to 10.

    Returns:
        dict: API response as a JSON dictionary.
    
    Raises:
        requests.HTTPError: If the API request fails.
    """
    
    # Construct payload and parameters
    data_json = build_data_json(user_ids, date_from, date_to, activity, source, export_data_type)
    params_json = build_param_json(page_number, page_size)

    response = requests.post(
        f"https://{DEALCLOUD_SITE}{API_ENDPOINT_USER_ACTIVITY}",
        json=data_json, 
        params=params_json,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    )

    response.raise_for_status()
    response_json = response.json()
    response_rows = response_json["rows"]
    return response_rows


def build_data_json(
    user_ids: list[int] = None,
    date_from: str = None,
    date_to: str = None,
    activity: int = None,
    source: int = None,
    export_data_type: int = None
) -> dict:
    """Builds JSON payload for API request.

    Returns:
        dict: JSON payload with only relevant parameters.
    """
    data = {}
    if user_ids: data["userIds"] = user_ids
    if date_from: data["dateFrom"] = date_from
    if date_to: data["dateTo"] = date_to
    if activity: data["activity"] = activity
    if source: data["source"] = source
    if activity == 8 and export_data_type: 
        data["exportDataType"] = export_data_type

    return data


def build_param_json(page_number: int, page_size: int) -> dict:
    """Builds query parameters for API request.

    Returns:
        dict: Query parameters.
    """
    params = {}
    if page_number: params["pageNumber"] = page_number
    if page_size: params["pageSize"] = page_size
    return params


def calculate_time_days_ago(days: int) -> str:
    """Calculates the timestamp for `days` ago in ISO format .

    Args:
        days (int): Number of days in the past.

    Returns:
        str: ISO 8601 timestamp with 'Z' suffix.
    """
    time_result = datetime.now() - timedelta(days=days)
    return time_result.isoformat()


def output_log_file(data):
    """Saves log data to a local file."""
    with open(f"{LOG_OUTPUT_DIR}/output.txt", "a") as log_file:
        for log in data:
            log_file.write(str(log) + "\n")


token = get_token()
user_activity = get_user_activity(token)
output_log_file(user_activity)
