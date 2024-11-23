# Calendar

## Preparation of Google Cloud

- Access https://console.cloud.google.com/projectcreate
- Name the project then CREATE
- Choose the new project
- Access https://console.cloud.google.com/apis/dashboard
- Library
  - Search 'PAM' and select Privileged Access Manager API
    - ENABLE it
    - Back to Library
  - Search 'Calendar' and select Google Calendar API
    - ENABLE it
	- CREATE CREDENTIALS
	  - Credential Type: Check User data
	  - OAuth Consent Screen: Name your project and set email addresses
	- Scope
	  - No modif required
    - OAuth Client ID
	  - Desktop Application and name it.
	- Your Credentials
	  - Download the credential and save `client_secret...json`

## _data/app-credentials.json

Copy your `client_secret...json` as `_data/app_credentials.json` in this directory.

## Add a Google account

- `./get48h.py add-token <name>`, for ex, `./get48.py add-token default`
- Choose a Google account and allow access.  The project is not approved yet, you have to make the browser proceed to an unsafe zone.
- If successful, it creates `_data/token-<name>.json`.
- It also creates `_data/calendars.json`. Check the file and removes calendars you are not interested.

## List the events in near future

- `./get48.py list`






