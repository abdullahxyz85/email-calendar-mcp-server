# Email & Calendar Manager MCP Server

An MCP (Model Context Protocol) server that enables Claude to manage emails and calendar events through Google Gmail, Outlook, and Google Calendar integration.

## Features

- **Email Management**
  - Search and retrieve emails (Gmail/Outlook)
  - Compose and send emails
  - Support for attachments
  - Email filtering and organization

- **Calendar Management**
  - Create calendar events
  - Check calendar availability
  - Set reminders and tasks
  - Manage meeting schedules

- **Security**
  - OAuth 2.0 authentication
  - Secure token storage with encryption
  - Credential management

## Project Structure

```
email-calendar-mcp-server/
├── src/
│   └── email_calendar_mcp/
│       ├── __init__.py
│       ├── main.py                 # MCP Server entry point
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── oauth.py             # OAuth 2.0 flow
│       │   └── token_manager.py     # Token storage and management
│       ├── services/
│       │   ├── __init__.py
│       │   ├── email_service.py     # Email operations (Gmail/Outlook)
│       │   └── calendar_service.py  # Calendar operations
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── email_tools.py       # Email tool definitions
│       │   └── calendar_tools.py    # Calendar tool definitions
│       └── utils/
│           ├── __init__.py
│           ├── logger.py            # Logging configuration
│           └── config.py            # Configuration management
├── tests/                           # Unit tests
├── config/                          # Configuration files
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── pyproject.toml                   # Project configuration
└── README.md                        # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.10+
- Google Cloud account (for Gmail & Calendar)
- Outlook/Microsoft account (optional)

### 2. Installation

```bash
# Clone the repository
cd email-calendar-mcp-server

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable APIs: Gmail API and Google Calendar API
4. Create OAuth 2.0 credentials (OAuth Consent Screen)
5. Download the credentials JSON file
6. Copy credentials to `config/google_credentials.json`

### 4. Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8080/callback
TOKEN_STORAGE_PATH=./tokens
```

### 5. Running the Server

```bash
python -m email_calendar_mcp.main
```

## Available Tools

### Email Tools

- `fetch_emails()` - Search and retrieve emails
- `send_email()` - Compose and send emails

### Calendar Tools

- `schedule_meeting()` - Create calendar events
- `get_calendar()` - Retrieve calendar availability
- `set_reminders()` - Create reminders and tasks

## Security Considerations

- Tokens are encrypted and stored locally
- Never commit `.env` file or credentials to version control
- Use OAuth 2.0 for secure authentication
- Implement proper error handling for sensitive operations

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

### Type Checking

```bash
mypy src/
```

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on the repository.
