from typing import Optional, List, Dict, Any

from mcp.server.fastmcp import FastMCP
mcp = FastMCP("gmail_tool")


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

import base64
from email.message import EmailMessage
# from datetime import datetime
from datetime import datetime, timezone, timedelta
import re

from text_cleaner import parse_readable_content, extract_readable_text



SCOPES = ['https://www.googleapis.com/auth/gmail.compose',
          "https://www.googleapis.com/auth/gmail.readonly"]

# Get the directory where this script is located
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_BASE_DIR)

# Use absolute paths for credentials
TOKEN_PATH = os.path.join(_PARENT_DIR, 'Temp_Tokens', 'gmail_token.json')
CREDENTIALS_PATH = os.path.join(_PARENT_DIR, 'credentials.json')

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists(TOKEN_PATH):
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if not os.path.exists(CREDENTIALS_PATH):
            raise FileNotFoundError(f"Credentials file not found: {CREDENTIALS_PATH}")
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
    with open(TOKEN_PATH, 'w') as token:
        token.write(creds.to_json())



# def gmail_query_to_epoch(query: str) -> str:
#     """
#     Convert Gmail query string with IST datetime into UTC epoch-based query.
#     If only dates are provided (no time), return as-is.
    
#     Example:
#         Input:  "after:2024/09/17T14:00 before:2024/09/17T15:00"
#         Output: "after:1726560000 before:1726563600"
#     """
#     IST = timezone(timedelta(hours=5, minutes=30))

#     def to_epoch(dt_str: str) -> str:
#         # Detect if time is included
#         if "T" in dt_str:
#             # Parse format yyyy/mm/ddThh:mm in IST
#             dt = datetime.strptime(dt_str, "%Y/%m/%dT%H:%M").replace(tzinfo=IST)
#             # Convert IST → UTC epoch
#             return str(int(dt.astimezone(timezone.utc).timestamp()))
#         else:
#             # No time → return unchanged
#             return dt_str

#     # Find all after:/before: terms
#     pattern = r"(after|before):([\d/]+(?:T\d{2}:\d{2})?)"
#     matches = re.findall(pattern, query)

#     for key, value in matches:
#         new_value = to_epoch(value)
#         query = query.replace(f"{key}:{value}", f"{key}:{new_value}")

#     return query

def gmail_query_to_epoch(query: str):
    """
    Convert Gmail query with IST dates/timestamps into UTC epoch query.
    Supports multiple date formats:
      - after:YYYY-MM-DD before:YYYY-MM-DD
      - after:YYYY/MM/DD before:YYYY/MM/DD
      - after:YYYY/MM/DDTHH:MM before:YYYY/MM/DDTHH:MM
    Preserves other query parameters (e.g., from:, subject:, etc.)
    Returns: query string with epoch values for after/before, preserving other terms.
    """
    IST = timezone(timedelta(hours=5, minutes=30))

    def parse_date(date_str):
        """Parse date string in various formats"""
        date_str = date_str.strip()
        # Try different date formats
        formats = [
            "%Y/%m/%dT%H:%M",  # YYYY/MM/DDTHH:MM
            "%Y-%m-%dT%H:%M",  # YYYY-MM-DDTHH:MM
            "%Y/%m/%d",        # YYYY/MM/DD
            "%Y-%m-%d",        # YYYY-MM-DD
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {date_str}")

    def to_epoch(date_str, is_start=True):
        # Detect if timestamp with time is given
        dt = parse_date(date_str)
        dt = dt.replace(tzinfo=IST)
        if not is_start and "T" not in date_str:  # before date without time = next day 00:00
            dt += timedelta(days=1)
        return int(dt.astimezone(timezone.utc).timestamp())

    # Find after and before parts
    after_match = re.search(r"after:([\d/:-T]+)", query)
    before_match = re.search(r"before:([\d/:-T]+)", query)

    # Build new query preserving other parts
    new_query_parts = []
    
    # Add other query parts (everything except after: and before:)
    other_parts = re.sub(r"(after|before):[\d/:-T]+", "", query).strip()
    if other_parts:
        new_query_parts.append(other_parts)
    
    # Add converted after/before
    if after_match:
        try:
            after_epoch = to_epoch(after_match.group(1), is_start=True)
            new_query_parts.append(f"after:{after_epoch}")
        except Exception as e:
            print(f"Error parsing after date: {e}")
    
    if before_match:
        try:
            before_epoch = to_epoch(before_match.group(1), is_start=False)
            new_query_parts.append(f"before:{before_epoch}")
        except Exception as e:
            print(f"Error parsing before date: {e}")

    return " ".join(new_query_parts) if new_query_parts else query



def gmail_send_message(to, subject, content_msg):
  """
  Send an email via Gmail API.
  Returns: dict with message info on success, dict with error info on failure.
  """
  try:
    service = build("gmail", "v1", credentials=creds)
    message = EmailMessage()

    message.set_content(content_msg)

    message["To"] = to
    message["From"] = "kamblemanaswi8@gmail.com"
    message["Subject"] = subject

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"raw": encoded_message}
    # pylint: disable=E1101
    send_message = (
      service.users()
      .messages()
      .send(userId="me", body=create_message)
      .execute()
    )
    # Return success with message ID
    return {
      "success": True,
      "messageId": send_message.get("id"),
      "threadId": send_message.get("threadId"),
      "labelIds": send_message.get("labelIds", [])
    }
  except HttpError as error:
    error_details = {
      "success": False,
      "error": str(error),
      "error_code": error.resp.status if hasattr(error, 'resp') else None
    }
    print(f"Error sending email: {error_details}")
    return error_details
  except Exception as error:
    error_details = {
      "success": False,
      "error": str(error)
    }
    print(f"Unexpected error sending email: {error_details}")
    return error_details


def gmail_list_messages(query):
    original_query = query
    try:
        query = gmail_query_to_epoch(query)
        print(f"Original query: {original_query}")
        print(f"Converted query: {query}\n")
    except Exception as e:
        print(f"Warning: Error converting query to epoch, using original: {e}")
        query = original_query
        print(f"Using original query: {query}\n")
    try:
        service = build("gmail", "v1", credentials=creds)
        # print("Service built successfully. \n")

        results = (
            service.users().messages().list(userId="me", labelIds=["INBOX"], q=query).execute()
        )
        messages = results.get("messages", [])
        print(f"{len(messages) = }\n\n")
        if not messages:
            print("No messages found.")
            return [{"Change query":"No Emails Found for the query"}]
        # print(f"{len(messages) = }\n")

        email_data = []
        
        for message in messages:
            msg = (
                service.users().messages().get(userId="me", id=message["id"]).execute()
            )
            
            # Extract headers
            headers = msg['payload']['headers']
        
            email_info = dict()

            # Get header information
            for header in headers:
                name = header['name'].lower()
                if name == 'from':
                    email_info['from'] = header['value']
                # elif name == 'to':
                #     email_info['to'] = header['value']
                elif name == 'date':
                    email_info['date'] = header['value']
                elif name == 'subject':
                    email_info['subject'] = header['value']
            
            # Get email content
            if 'parts' in msg['payload']:
                # Multipart message
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            # email_info['content'] = base64.urlsafe_b64decode(data).decode()
                            extracted_content = base64.urlsafe_b64decode(data).decode()
                            # f.write(f"Content : {extract_readable_text(parse_readable_content(extracted_content))}")
                            # f.write("\n" + "-" * 80 + "\n\n")

                            email_info['content'] = parse_readable_content(extracted_content)
                            break
            else:
                # Single part message
                data = msg['payload']['body'].get('data', '')
                if data:
                    extracted_content = base64.urlsafe_b64decode(data).decode()
                    # f.write(f"Content : {extract_readable_text(parse_readable_content(extracted_content))}")
                    # f.write("\n" + "-" * 80 + "\n\n")
                            
                    email_info['content'] = parse_readable_content(extracted_content)

            
            email_data.append(email_info)
            print(f"{len(email_data) = }\n\n")
        
        return email_data
        
    except HttpError as error:
        return f"An error occurred: {error}"
    

@mcp.tool("send_gmail")
def send_gmail(to: str, subject: str, content_msg: str) -> dict:
    """Use this tool to send GMail 
    
    Parameters:
    to (str) : email id of Reciever
    subject (str) : Subject of Email
    content_msg (str) : Actual message for the reciever.
    """

    with open("send_gmail_args.txt", 'a') as f:  # 'a' mode for append
        f.write(f"{to = },\n{subject = }\n{content_msg = }\n --------------------------------- \n\n")

    return gmail_send_message(to, subject, content_msg)

@mcp.tool("get_gmail")
def get_gmail(query: str) -> List[Dict[str, Any]]:
    """
    Use this tool to fetch Gmail messages matching the given query.

    Parameters:
    query (str) : a string and should be a standard Gmail search filter in RFC 3339 / ISO 8601 timestamp,
    e.g., 'from:someone@example.com is:unread after:2024/09/17 before:2024/09/18',
    'after:2024/09/17T14:00 before:2024/09/17T15:00',
    'is:unread after:2024/09/17 before:2024/09/18', etc

    Returns:
    List: Scraped data of gmails that includes information of sender mail id, Time of recieving email, content message
    Remember: Message content data might have unclear data, read and understand properly.
    """

    with open("get_gmail_args.txt", 'a') as f:  # 'a' mode for append
        f.write(f"{query = },\n --------------------------------- \n\n")

    return gmail_list_messages(query)

if __name__ == "__main__":
#   gmail_list_messages()
    # gmail_send_message()
    mcp.run(transport="stdio")
    # out = get_gmail(query = "after:2025/09/18 before:2025/09/19")
    # print(out)
