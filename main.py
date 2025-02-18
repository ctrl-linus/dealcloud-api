import requests
import os
import json

site = os.getenv("DEALCLOUD_SITE")
client_id = os.getenv("DEALCLOUD_CLIENT_ID")
client_secret = os.getenv("DEALCLOUD_CLIENT_SECRET")

# API Endpoints
api_endpoint_token = "/api/rest/v1/oauth/token"
api_endpoint_user_activity = "/api/rest/v1/management/user/activity"

session = requests.Session()


# Request OAUTH token
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
# _activity: int (optional) - the activity type, if not provided, all activity types will be returned.
# _page_number: int (optional, default: 1) - the page number of the response, if not provided, the default value is 1. This can be used to increase the number of records returned.
# _page_size: int (optional, default: 10) - the number of records returned per page, if not provided, the default value is 10. This can be used to increase the number of records returned.
#
# return user_activity: json
def get_user_activity(
        _token: str, 
        _user_ids: list[int] = None, 
        _activity: int = None, 
        _page_number: int = None,
        _page_size: int = None
        ): 
    # Format data input into json object
    _data_json = build_data_json(_user_ids, _activity)
    _params_json = build_param_json(_page_number, _page_size)
    print(_params_json)
    
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
def build_data_json(_user_ids: list[int], _activity: int, ):
    _data: dict = {}
    if _user_ids:  _data["userIds"] = _user_ids
    if _activity: _data["activity"] = _activity
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

token = get_token()
user_activity = get_user_activity(token, _user_ids = [20843], _activity=8, _page_size=1)
print(user_activity)