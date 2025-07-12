# Gmail Bot Setup

## Overview

This bot checks a Gmail inbox for unread emails every N minutes and sends automatic replies using the OpenAI API. It stores message data (including sender hashes, message bodies, and reply threads) in a SQLite database. All settings are configurable, and secrets are stored in a `.env` file.

## Setup Instructions

1. **Create a Google Cloud Project**

   * Visit [https://console.cloud.google.com/](https://console.cloud.google.com/)
   * Create a new project (ensure it is under "No organization")

2. **Enable the Gmail API**

   * Navigate to "APIs & Services" > "Library"
   * Search for "Gmail API" and click "Enable"

3. **Create OAuth Credentials**

   * Go to "APIs & Services" > "Credentials"
   * Click "Create Credentials" > "OAuth client ID"
   * Choose "Desktop App" as the application type
   * Click "Create" and note the `client_id` and `client_secret`

4. **Configure the OAuth Consent Screen**

   * Navigate to "OAuth consent screen"
   * Choose "External"
   * Fill out the app name and developer email
   * Add `http://localhost` as an authorized domain (not strictly needed for desktop apps but may help)
   * Add the Gmail address of the bot you want to monitor to the "Test users" list
   * Save the configuration

5. **Get a Refresh Token**

   * Run the provided `get_refresh_token.py` script
   * Log in with the Gmail account you want the bot to monitor
   * The script will print an `ACCESS TOKEN` and `REFRESH TOKEN`
   * Copy the `REFRESH TOKEN` into your `.env` file

6. **Set Up Your `.env` File**
   Create a file called `.env` in your project root and add:

   ```
   GMAIL_CLIENT_ID=your-client-id
   GMAIL_CLIENT_SECRET=your-client-secret
   GMAIL_REFRESH_TOKEN=your-refresh-token
   OPENAI_API_KEY=your-openai-api-key
   ```

7. **Run the Bot**
   Run the bot manually:

   ```bash
   python3 bot/main.py
   ```

   This will:

   * Fetch unread messages
   * Store message data in SQLite
   * Generate a reply (currently hardcoded)
   * Send the reply
   * Mark the original message as read

## Notes

* Only the Gmail account used to log in during the OAuth process will be monitored.
* To switch inboxes, rerun `get_refresh_token.py`, log in with a different Gmail account, and update the `.env` with the new `refresh_token`.
* You must add each account to the test users list on the OAuth consent screen before it can be used.

## Troubleshooting

* If you get a browser error like "Something went wrong" during OAuth, try using an incognito window or switch browsers.

* If you see an error like `run_console` not found, upgrade your auth libraries:

  ```bash
  pip install --upgrade google-auth-oauthlib google-auth google-api-python-client
  ```

* If you want to manually authorize without a redirect, use `flow.run_console()` instead of `flow.run_local_server()` in `get_refresh_token.py`.

You're now ready to run the Gmail bot and respond to messages automatically!
