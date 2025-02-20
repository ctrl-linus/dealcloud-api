# Intapp DealCloud API 

API handler for Intapp DealCloud CRM to forward logs to SIEM.

## Requirements
Set the following environment variables:
### Environment Variables
  * `DEALCLOUD_SITE`: Address for the client's DealCloud portal, eg: `clientname.dealcloud.com`
  * `API_CLIENT_ID`: API client_id key, provided by client from DealCloud console
  * `API_CLIENT_SECRET`: API client_secret, provided by client from DealCloud console

### Config Variables
* `LOG_OUTPUT_DIR`: Directory to output log files to
* `SYSLOG_SERVER`: <u>(UNUSED)</u> IP belonging to syslog server
* `SYSLOG_PORT`: <u>(UNUSED)</u> Port to send data to syslog server on

## Additional Documentation
* [DealCloud API Docs: Token](https://api.docs.dealcloud.com/docs/token)
* [DealCloud API Docs: User Activity](https://api.docs.dealcloud.com/docs/management/user_activity)