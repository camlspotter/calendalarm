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

## credentials.json

Copy your `client_secret...json` as `credentials.json` in this directory.

	




