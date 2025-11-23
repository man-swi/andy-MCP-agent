import os

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json

from mcp.server.fastmcp import FastMCP
import asyncio
from google.oauth2.credentials import Credentials

from google.oauth2 import service_account
import datetime
from googleapiclient.errors import HttpError

from typing import Optional, List, Any

mcp = FastMCP("calendar_server")

# # Path to service account credentials
# # SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
# SERVICE_ACCOUNT_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly",
          "https://www.googleapis.com/auth/calendar"]

# credentials = service_account.Credentials.from_service_account_file(
#     SERVICE_ACCOUNT_FILE, scopes=SCOPES
# )

# -----------------------
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists("Temp_Tokens/calendar_token.json"):
    creds = Credentials.from_authorized_user_file("Temp_Tokens/calendar_token.json", SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)

    # Save the credentials for the next run
    with open("Temp_Tokens/calendar_token.json", "w") as token:
        token.write(creds.to_json())

service = build("calendar", "v3", credentials=creds)
# ----------------------------------------------------------


@mcp.tool("get_calendar_events")
def get_calendar_events() -> List:
    """Use this tool to fetch events information from Calendar
    
    Returns: List of event informations."""

    # Call the Calendar API
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    # print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    # print('Events:\n');print(events)
    output = []
    for event in events:
        output.append({
            "start": datetime.datetime.fromisoformat(event.get("start").get("dateTime")).strftime("%A, %B %d, %Y at %I:%M %p IST"),
            "end": datetime.datetime.fromisoformat(event.get("end").get("dateTime")).strftime("%A, %B %d, %Y at %I:%M %p IST"),
            "summary": event.get("summary"),
            "status": event.get('status'),
            "description" : event.get('description', "No Description"),
            "location": event.get('location', "No location")
        })
    
    if not output:
        return ["No events found."]
    else:
        return output

@mcp.tool("create_calendar_event")
def create_calendar_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: str = None,
    location: str = None,
    attendees: list = None,
):
    """
    Creates a new event on the user's Google Calendar.

    Args:
        summary (str): The title of the event.
        start_time (str): The start date and time of the event in RFC3339 format (e.g., '2025-09-15T09:00:00+05:30').
        end_time (str): The end date and time of the event in RFC3339 format. Usually 30 min more that start_time.
        description (str, optional): A brief description of the event. Defaults to None.
        location (str, optional): The location of the event. Defaults to None.
        attendees (list, optional): A list of dictionaries for attendees, e.g.,
                                     [{'email': 'attendee1@example.com'}, {'email': 'attendee2@example.com'}].
                                     Defaults to None.
    
    Returns:
        dict: The created event resource, or None if an error occurred.
    """
    with open("create_claendar_event_args.txt", 'a') as f:  # 'a' mode for append
        f.write(f"{summary = },\n{start_time = }\n{end_time =},\n{description = },\n{location = },\n{attendees = },\n --------------------------------- \n\n")

    
    try:
        # Define the event body
        event = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {
                "dateTime": start_time,
                "timeZone": "Asia/Kolkata",
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "Asia/Kolkata",
            },
            "attendees": attendees,
        }

        # Remove keys with None values to avoid API errors
        event = {k: v for k, v in event.items() if v is not None}
        
        # Insert the event into the user's calendar
        created_event = service.events().insert(calendarId="primary", body=event).execute()
        
        print(f"Event created: {created_event.get('htmlLink')}")
        return created_event

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

if __name__ == "__main__":
    mcp.run(transport="stdio")
    # output = get_calendar_events()
    # print(output)

# [{'kind': 'calendar#event', 
# 'etag': '"3514482561628414"', 
# 'id': '2pi86udsvvnpvo4icpu9rfji18', 
# 'status': 'confirmed', 
# 'htmlLink': 'https://www.google.com/calendar/event?eid=MnBpODZ1ZHN2dm5wdm80aWNwdTlyZmppMTggaHJpdHdpamthbWJsZTIwMDJAbQ', 
# 'created': '2025-09-07T10:34:40.000Z', 
# 'updated': '2025-09-07T10:34:40.814Z', 
# 'summary': 'Date with Madhu', 
# 'description': 'Take flowers for the lady', 
# 'location': 'Conrad Pune, 7, Mangaldas Rd, Sangamvadi, Pune, Maharashtra 411001, India', 
# 'creator': {'email': 'hritwijkamble2002@gmail.com', 'self': True}, 
# 'organizer': {'email': 'hritwijkamble2002@gmail.com', 'self': True}, 
# 'start': {'dateTime': '2025-09-10T17:00:00+05:30', 'timeZone': 'Asia/Kolkata'}, 
# 'end': {'dateTime': '2025-09-10T18:00:00+05:30', 'timeZone': 'Asia/Kolkata'}, 
# 'iCalUID': '2pi86udsvvnpvo4icpu9rfji18@google.com', 
# 'sequence': 0, 
# 'hangoutLink': 'https://meet.google.com/nqz-xgrh-vry', 
# 'conferenceData': {'entryPoints': [{'entryPointType': 'video', 'uri': 'https://meet.google.com/nqz-xgrh-vry', 'label': 'meet.google.com/nqz-xgrh-vry'}], 'conferenceSolution': {'key': {'type': 'hangoutsMeet'}, 'name': 'Google Meet', 'iconUri': 'https://fonts.gstatic.com/s/i/productlogos/meet_2020q4/v6/web-512dp/logo_meet_2020q4_color_2x_web_512dp.png'}, 'conferenceId': 'nqz-xgrh-vry'}, 
# 'reminders': {'useDefault': True}, 
# 'eventType': 'default'}]
