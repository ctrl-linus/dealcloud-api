import requests
import os
import json
import datetime
import numbers

site = os.getenv("DEALCLOUD_SITE")
client_id = os.getenv("DEALCLOUD_CLIENT_ID")
client_secret = os.getenv("DEALCLOUD_CLIENT_SECRET")

# API Endpoints
api_endpoint_token = "/api/rest/v1/oauth/token"
api_endpoint_user_activity = "/api/rest/v1/management/user/activity"

session = requests.Session()


# Request Bearer token
# Required to interact with API
# Expires after 15 minutes, currently fetching a new token on each request
# Scope must be user_management for User Activity log access
#
# return token: string
def get_token():
    token_response_raw = session.post(
        f"https://{site}{api_endpoint_token}",
        data=f"scope=user_management&grant_type=client_credentials",
        auth = (client_id, client_secret),
        headers={"content-type": "application/x-www-form-urlencoded"}
        )
    token_response = token_response_raw.json()
    token = token_response["access_token"]
    return token


# Request user activity
#
# _token: str (required) - Bearer token as returned by get_token()
# _user_ids: list[int] (optional) - an array of integers, if not provided, all users will be returned.
# _date_from: str (optional, default: 90 days ago) - the start date of the search, if not provided, the default value is 90 days ago. 90 days ago is also the maximum date range allowed.
# _date_to: str (optional, default: now) - the end date of the search, if not provided, the default value is today. This value must be at least 1 day greater than DateFrom. Date Filters are evaluated to the nearest date.
# _activity: int (optional) - the activity type, if not provided, all activity types will be returned.
# _source: int (optional) - the source type, if not provided, all source types will be returned.
# _export_data_type: int (optional) - enables filtering of export data (only if activity: 8 is specified). If not provided, all types will be returned.
# _page_number: int (optional, default: 1) - the page number of the response, if not provided, the default value is 1. This can be used to increase the number of records returned.
# _page_size: int (optional, default: 10) - the number of records returned per page, if not provided, the default value is 10. This can be used to increase the number of records returned.
#
# return user_activity: json
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
        ): 
    
    # Ensure inputs are valid
    validate_inputs(_token, _user_ids, _date_from, _date_to, _activity, _source, _export_data_type, _page_number, _page_size)

    # Format input into json objects
    _data_json = build_data_json(_user_ids, _date_from, _date_to, _activity, _source, _export_data_type)
    _params_json = build_param_json(_page_number, _page_size)
    print(_data_json)
    
    # Make API request with given parameters
    user_activity_raw = session.post(
        f"https://{site}{api_endpoint_user_activity}",
        data=_data_json,
        params=_params_json,
        headers={
            "content-type": "application/json",
            "Authorization": f"Bearer {_token}"
            }
    )
    user_activity: json = user_activity_raw.json()
    return user_activity


# Create data json object from input
# Avoids including parameters that aren't relevant
# Eg: If no activity type specified, ignore
#
# return _data_json: json
def build_data_json(_user_ids: list[int], _date_from: str, _date_to: str, _activity: int, _source: int, _export_data_type: int):
    _data: dict = {}
    if _user_ids: _data["userIds"] = _user_ids
    if _date_from: _data["dateFrom"] = _date_from
    if _date_to: _data["dateTo"] = _date_to
    if _activity: _data["activity"] = _activity
    if _source: _data["source"] = _source
    if _activity == 8 and _export_data_type: _data["exportDataType"] = _export_data_type
    _data_json: json = json.dumps(_data)
    return _data_json


# Create params json object from input
# Avoids including parameters that aren't relevant
# Eg: If no activity type specified, ignore
#
# return _data_json: json
def build_param_json(_page_number: int, _page_size: int):
    _params: dict = {}
    if _page_number: _params["pageNumber"] = _page_number
    if _page_size: _params["pageSize"] = _page_size
    _params_json: json = json.dumps(_params)
    return _params_json

# Input validation
def validate_inputs(_token, _user_ids, _date_from, _date_to, _activity, _source, _export_data_type, _page_number, _page_size):
    validate_token(_token)
    if _user_ids: validate_user_ids(_user_ids)
    if _date_from: validate_date_from(_date_from)
    if _date_to: validate_date_to(_date_to)
    if _activity: validate_activity(_activity)
    if _source: validate_source(_source)
    if _export_data_type: validate_export_data_type(_export_data_type, _activity)
    if _page_number: validate_page_number(_page_number)
    if _page_size: validate_page_size(_page_size)

# Validate API Token
# Assert that token is string 
def validate_token(_token: str):
    assert isinstance(_token, str), f"Token is invalid!"

# Validate User IDs
# Assert that user id value is list
def validate_user_ids(_user_ids):
    assert isinstance(_user_ids, list), f"Value of _user_ids is not a list ({_user_ids})"

# Validate date from
# Assert that date from is string
def validate_date_from(_date_from):
    assert isinstance(_date_from, str), f"Value of _date_from is not a str ({_date_from})"

# Validate date to
# Assert that date to is string
def validate_date_to(_date_to):
    assert isinstance(_date_to, str), f"Value of _date_to is not a str ({_date_to})"

# Validate activity
# Assert that activity is int
# Assert that activity value is in bounds (0, 10)
def validate_activity(_activity: int):
    assert isinstance(_activity, int), f"Value of _activity is not an int ({_activity})"
    assert _activity > 0 and _activity < 11, f"Value of _activity is out of bounds ({_activity})"

# Validate source
# Assert that source is int
# Assert that source value is in bounds (1, 5)
def validate_source(_source: int):
    assert isinstance(_source, int), f"Value of _source is not an int ({_source})"
    assert _source > 0 and _source < 5, f"Value of _source is out of bounds ({_source})"

# Validate export data type
# Assert that activity is set to Export Data event
# Assert that export data type is int
# Assert that export data type value is in bounds (1, 5)
def validate_export_data_type(_export_data_type, _activity):
    assert _activity == 8, f"Value of _activity is not 8 (Export Data) ({_activity})"
    assert isinstance(_export_data_type, int), f"Value of _export_data_type is not an int ({_export_data_type})"
    assert _export_data_type > 0 and _export_data_type < 5, f"Value of _export_data_type is out of bounds ({_export_data_type})"

# Validate page number
# Assert that page number is int
def validate_page_number(_page_number):
    assert isinstance(_page_number, int), f"Value of _page_number is not an int ({_page_number})"

# Validate page size
# Assert that page size is int
def validate_page_size(_page_size):
    assert isinstance(_page_size, int), f"Value of _page_size is not an int ({_page_size})"

time_now = datetime.datetime.now()
time_diff = datetime.timedelta(days=3)
time_from = time_now - time_diff
time_from = time_from.isoformat()
time_from = f"{time_from}Z"

time_now = datetime.datetime.now()
time_diff = datetime.timedelta(days=2)
time_to = time_now - time_diff
time_to = time_to.isoformat()
time_to = f"{time_to}Z"

token = get_token()
user_activity = get_user_activity(token)
print(user_activity)