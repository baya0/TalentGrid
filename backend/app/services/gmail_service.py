# app/services/gmail_service.py
"""
Gmail OAuth Integration for CV Import
Scans emails for CV attachments (PDF, DOC, DOCX) and extracts them for parsing.
"""
import base64
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Lazy imports to avoid startup errors if packages not installed
_google_flow = None
_google_credentials = None
_gmail_service_builder = None


def _get_google_imports():
    """Lazy load Google OAuth imports."""
    global _google_flow, _google_credentials, _gmail_service_builder
    if _google_flow is None:
        try:
            from google_auth_oauthlib.flow import Flow
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            _google_flow = Flow
            _google_credentials = Credentials
            _gmail_service_builder = build
        except ImportError:
            raise ImportError(
                "Google OAuth packages not installed. Run: "
                "pip install google-auth-oauthlib google-api-python-client"
            )
    return _google_flow, _google_credentials, _gmail_service_builder


# Gmail API scopes - read-only access to emails
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Supported CV file extensions
CV_EXTENSIONS = {'.pdf', '.doc', '.docx'}


def get_oauth_url(client_id: str, client_secret: str, redirect_uri: str) -> Tuple[str, str]:
    """
    Generate Google OAuth URL for Gmail access.
    Returns (auth_url, state) tuple.
    """
    Flow, _, _ = _get_google_imports()

    if not client_id or not client_secret:
        raise ValueError(
            "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env file. "
            "Get credentials from https://console.cloud.google.com/apis/credentials"
        )

    # Create OAuth flow using client config dict (no file needed)
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri]
        }
    }

    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = redirect_uri

    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    return auth_url, state


def exchange_code_for_tokens(
    code: str,
    state: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str
) -> Dict:
    """
    Exchange authorization code for access tokens.
    Returns token dict with access_token, refresh_token, etc.
    """
    Flow, _, _ = _get_google_imports()

    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri]
        }
    }

    flow = Flow.from_client_config(client_config, scopes=SCOPES, state=state)
    flow.redirect_uri = redirect_uri

    # Exchange code for tokens
    flow.fetch_token(code=code)

    credentials = flow.credentials

    return {
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "expiry": credentials.expiry.isoformat() if credentials.expiry else None
    }


def get_gmail_service(tokens: Dict, client_id: str, client_secret: str):
    """Create Gmail API service from stored tokens."""
    _, Credentials, build = _get_google_imports()

    credentials = Credentials(
        token=tokens.get("access_token"),
        refresh_token=tokens.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )

    return build('gmail', 'v1', credentials=credentials)


def scan_emails_for_cvs(
    tokens: Dict,
    client_id: str,
    client_secret: str,
    max_results: int = 50,
    days_back: int = 30
) -> List[Dict]:
    """
    Scan Gmail inbox for emails with CV attachments.
    Returns list of email summaries with attachment info.
    """
    service = get_gmail_service(tokens, client_id, client_secret)

    # Search for emails with attachments from last N days
    # Query for common CV-related terms and has attachment
    query = f"has:attachment newer_than:{days_back}d"

    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])
    cv_emails = []

    for msg in messages:
        msg_detail = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        # Extract email metadata
        headers = msg_detail.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')

        # Find CV attachments
        attachments = _find_cv_attachments(msg_detail.get('payload', {}))

        if attachments:
            cv_emails.append({
                'message_id': msg['id'],
                'subject': subject,
                'from': from_email,
                'date': date,
                'attachments': attachments
            })

    return cv_emails


def _find_cv_attachments(payload: Dict, attachments: List = None) -> List[Dict]:
    """Recursively find CV attachments in email payload."""
    if attachments is None:
        attachments = []

    # Check if this part is an attachment
    filename = payload.get('filename', '')
    if filename:
        ext = os.path.splitext(filename.lower())[1]
        if ext in CV_EXTENSIONS:
            body = payload.get('body', {})
            attachments.append({
                'filename': filename,
                'attachment_id': body.get('attachmentId'),
                'size': body.get('size', 0),
                'mime_type': payload.get('mimeType', 'application/octet-stream')
            })

    # Recursively check parts
    for part in payload.get('parts', []):
        _find_cv_attachments(part, attachments)

    return attachments


def download_attachment(
    tokens: Dict,
    client_id: str,
    client_secret: str,
    message_id: str,
    attachment_id: str
) -> bytes:
    """Download an attachment from Gmail and return raw bytes."""
    service = get_gmail_service(tokens, client_id, client_secret)

    attachment = service.users().messages().attachments().get(
        userId='me',
        messageId=message_id,
        id=attachment_id
    ).execute()

    # Attachment data is base64url encoded
    data = attachment.get('data', '')
    file_data = base64.urlsafe_b64decode(data)

    return file_data
