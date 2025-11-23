# Andy - The MCP Agent

Andy is an intelligent executive assistant agent built to help manage emails (Gmail) and calendar events efficiently. It leverages LangGraph and LangChain frameworks to provide a seamless interaction experience.

## Features

- **Email Management**
  - Read and summarize emails from Gmail
  - Send professional emails with context-aware tone
  - Parse and extract key information from email content

- **Calendar Management**
  - View upcoming calendar events
  - Create and schedule new events
  - Handle timezone conversions (IST/UTC)
  - Manage event details including location, attendees, and descriptions

## Technical Stack

- Python 3.x
- LangGraph & LangChain
- Google APIs (Gmail & Calendar)
- Mistral AI Model

## Setup

1. Clone this repository
2. Install dependencies:
```bash
pip install langgraph langchain-core google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv
```

3. Set up Google API credentials:
   - Place your `credentials.json` in the root directory
   - First run will generate required tokens in `Temp_Tokens/` directory

4. Create a `.env` file with required environment variables

## Usage

The agent can be initialized and used as follows:

```python
from graph import get_agent

# Initialize the agent
agent = await get_agent()

# Start conversation
response = agent.invoke({
    "messages": [{"role": "user", "content": "What's on my calendar today?"}]
})
```

## Features in Detail

### Gmail Integration
- Query emails using natural language
- Parse email content intelligently
- Send professionally formatted emails

### Calendar Integration
- View events in IST timezone
- Create events with complete details
- Handle scheduling conflicts
- Manage attendees and locations

## Project Structure

```
├── All_Servers/
│   ├── calendar_tool.py
│   ├── gmail_tool_5.py
├── graph.py
├── prompt.py
└── README.md
```

## Note

This agent uses timezone-aware operations defaulting to IST (UTC+5:30) and maintains professional communication standards while interacting with users.

