import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scope for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']

def create_google_meet_space():
    """Creates a Google Meet link by creating a Calendar event."""
    creds = None

    # Load existing credentials from the 'token.json' file
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Initiate OAuth flow if credentials are invalid or missing
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=8080)

        # Save credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Build the Calendar API service
        service = build('calendar', 'v3', credentials=creds)

        # Create an event with Google Meet conferencing enabled
        event = {
            'summary': 'Meeting',
            'description': 'A meeting created via API with a Google Meet link.',
            'start': {
                'dateTime': '2024-11-26T10:00:00-07:00',  # Replace with desired start time
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': '2024-11-26T11:00:00-07:00',  # Replace with desired end time
                'timeZone': 'America/Los_Angeles',
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': 'unique-request-id',  # Unique identifier for the request
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                },
            },
        }

        # Insert the event into the primary calendar
        event = service.events().insert(
            calendarId='primary', 
            body=event, 
            conferenceDataVersion=1
        ).execute()

        # Return the Google Meet link
        return event.get('hangoutLink')

    except Exception as error:
        print(f"An error occurred: {error}")
        return None
