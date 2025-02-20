import requests
import os
from datetime import datetime, timedelta, timezone

# System variables
DEALCLOUD_SITE = os.getenv("DEALCLOUD_SITE")
API_CLIENT_ID = os.getenv("DEALCLOUD_CLIENT_ID")
API_CLIENT_SECRET = os.getenv("DEALCLOUD_CLIENT_SECRET")

# API Endpoints
API_ENDPOINT_TOKEN = "/api/rest/v1/oauth/token"
API_ENDPOINT_USER_ACTIVITY = "/api/rest/v1/management/user/activity"

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
    _token: str, 
    _user_ids: list[int] = None, 
    _date_from: str = None,
    _date_to: str = None,
    _activity: int = None, 
    _source: int = None,
    _export_data_type: int = None,
    _page_number: int = None,
    _page_size: int = None
) -> dict:
    """Fetch user activity from the API.

    Args:
        _token (str): Bearer token from `get_token()`.
        _user_ids (list[int], optional): List of user IDs to filter by. Defaults to None.
        _date_from (str, optional): Start date (max 90 days ago). Defaults to None.
        _date_to (str, optional): End date (at least 1 day after `_date_from`). Defaults to None.
        _activity (int, optional): Activity type filter. Defaults to None.
        _source (int, optional): Source type filter. Defaults to None.
        _export_data_type (int, optional): Filter for export data (requires `_activity=8`). Defaults to None.
        _page_number (int, optional): Page number (default 1). Defaults to 1.
        _page_size (int, optional): Number of records per page (default 10). Defaults to 10.

    Returns:
        dict: API response as a JSON dictionary.
    
    Raises:
        requests.HTTPError: If the API request fails.
    """
    
    # Construct payload and parameters
    _data_json = build_data_json(_user_ids, _date_from, _date_to, _activity, _source, _export_data_type)
    _params_json = build_param_json(_page_number, _page_size)

    response = requests.post(
        f"https://{DEALCLOUD_SITE}{API_ENDPOINT_USER_ACTIVITY}",
        json=_data_json, 
        params=_params_json,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_token}"
        }
    )

    response.raise_for_status()
    response_json = response.json()
    response_rows = response_json["rows"]
    return response_rows


def build_data_json(
    _user_ids: list[int] = None,
    _date_from: str = None,
    _date_to: str = None,
    _activity: int = None,
    _source: int = None,
    _export_data_type: int = None
) -> dict:
    """Builds JSON payload for API request.

    Returns:
        dict: JSON payload with only relevant parameters.
    """
    _data = {}
    if _user_ids: _data["userIds"] = _user_ids
    if _date_from: _data["dateFrom"] = _date_from
    if _date_to: _data["dateTo"] = _date_to
    if _activity: _data["activity"] = _activity
    if _source: _data["source"] = _source
    if _activity == 8 and _export_data_type: 
        _data["exportDataType"] = _export_data_type

    return _data


def build_param_json(_page_number: int, _page_size: int) -> dict:
    """Builds query parameters for API request.

    Returns:
        dict: Query parameters.
    """
    _params = {}
    if _page_number: _params["pageNumber"] = _page_number
    if _page_size: _params["pageSize"] = _page_size
    return _params


def calculate_time_days_ago(_days: int) -> str:
    """Calculates the timestamp for `_days` ago in ISO format (UTC).

    Args:
        _days (int): Number of days in the past.

    Returns:
        str: ISO 8601 timestamp with 'Z' suffix.
    """
    time_result = datetime.now(timezone.utc) - timedelta(days=_days)
    return time_result.isoformat()


token = get_token()
user_activity = get_user_activity(token)
print(user_activity)