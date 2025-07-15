import asyncio
import logging
import sys
import io
from contextlib import redirect_stdout, redirect_stderr
from typing import Optional, Dict, Any, Callable

from twikit import Client
from config import TwitterConfig, RateLimitConfig, TwitterCredentials
from rate_limiter import RateLimitHandler
from cookie_manager import RedisCookieManager

logger = logging.getLogger(__name__)


class VerificationChallenge(Exception):
    """Exception raised when Twitter requires verification."""
    def __init__(self, challenge_type: str, message: str, hint: Optional[str] = None):
        self.challenge_type = challenge_type
        self.message = message
        self.hint = hint
        super().__init__(message)


class AuthSessionManager:
    """Manages authentication sessions with verification challenges."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, session_id: str, auth_id: str, password: str, 
                      client: Client, config: TwitterConfig) -> None:
        """Create a new authentication session."""
        self.sessions[session_id] = {
            'auth_id': auth_id,
            'password': password,
            'client': client,
            'config': config,
            'challenge_pending': False,
            'challenge_type': None,
            'verification_response': None
        }
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get authentication session by ID."""
        return self.sessions.get(session_id)
    
    def set_challenge(self, session_id: str, challenge_type: str) -> None:
        """Mark session as having a pending challenge."""
        if session_id in self.sessions:
            self.sessions[session_id]['challenge_pending'] = True
            self.sessions[session_id]['challenge_type'] = challenge_type
    
    def set_verification_response(self, session_id: str, response: str) -> None:
        """Set the verification response for a session."""
        if session_id in self.sessions:
            self.sessions[session_id]['verification_response'] = response
            self.sessions[session_id]['challenge_pending'] = False
    
    def cleanup_session(self, session_id: str) -> None:
        """Remove session data."""
        self.sessions.pop(session_id, None)


class InteractiveAuthHandler:
    """Handles Twitter authentication with verification challenge support."""
    
    def __init__(self, session_manager: AuthSessionManager):
        self.session_manager = session_manager
    
    async def authenticate_with_challenge_support(self, session_id: str, auth_id: str, 
                                                 password: str, cookies_file: str) -> None:
        """Authenticate with support for verification challenges."""
        
        # Create client and session
        client = Client('en-US')
        config = TwitterConfig(
            credentials=TwitterCredentials(
                auth_id=auth_id,
                password=password,
                cookies_file=cookies_file
            ),
            output_dir="output"
        )
        
        self.session_manager.create_session(session_id, auth_id, password, client, config)
        
        # Attempt authentication with input interception
        try:
            await self._login_with_input_interception(session_id, client, auth_id, password, cookies_file)
        except VerificationChallenge:
            # Challenge was raised and handled, authentication will continue when response is provided
            pass
    
    async def continue_authentication(self, session_id: str, verification_response: str) -> None:
        """Continue authentication after verification response is provided."""
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError("Invalid session ID")
        
        # Set the verification response
        self.session_manager.set_verification_response(session_id, verification_response)
        
        # Continue the authentication process
        client = session['client']
        auth_id = session['auth_id']
        password = session['password']
        cookies_file = session['config'].credentials.cookies_file
        
        try:
            await self._login_with_input_interception(session_id, client, auth_id, password, cookies_file)
        except VerificationChallenge:
            # Another challenge might be needed
            pass
    
    async def _login_with_input_interception(self, session_id: str, client: Client,
                                           auth_id: str, password: str, cookies_file: str) -> None:
        """Login with input() call interception to catch verification prompts."""

        # Buffer to capture stdout/stderr from twikit
        captured = io.StringIO()

        # Mock input function to intercept verification prompts
        original_input = __builtins__["input"] if isinstance(__builtins__, dict) else __builtins__.input

        def mock_input(prompt: str = ""):
            """Intercept input prompts and raise challenges when detected."""
            # Combine last printed line with the prompt text for detection
            output = captured.getvalue().strip().splitlines()
            last_line = output[-1] if output else ""
            combined = f"{last_line} {prompt}".lower()

            if "confirmation code" in combined and "sent" in combined:
                challenge_type = "confirmation_code"
                hint = self._extract_email_hint(combined)
                raise VerificationChallenge(challenge_type, last_line or prompt, hint)

            if ("email address" in combined and "verify" in combined) or "verify your identity" in combined:
                challenge_type = "email_verification"
                hint = self._extract_email_hint(combined)
                raise VerificationChallenge(challenge_type, last_line or prompt, hint)

            # Check for a previously supplied verification response
            session = self.session_manager.get_session(session_id)
            if session and session.get("verification_response"):
                response = session["verification_response"]
                session["verification_response"] = None
                return response

            raise RuntimeError(f"Unexpected input prompt: {prompt}")

        try:
            # Patch the input function and capture stdout/stderr from twikit
            if isinstance(__builtins__, dict):
                __builtins__["input"] = mock_input
            else:
                __builtins__.input = mock_input

            with redirect_stdout(captured), redirect_stderr(captured):
                await client.login(
                    auth_info_1=auth_id,
                    password=password,
                    cookies_file=cookies_file,
                )

        finally:
            # Restore original input function
            if isinstance(__builtins__, dict):
                __builtins__["input"] = original_input
            else:
                __builtins__.input = original_input
    
    def _extract_email_hint(self, prompt: str) -> Optional[str]:
        """Extract email hint from verification prompt."""
        # Look for patterns like "te*****@g****.*" or "te*****@g***.***"
        import re
        email_pattern = r'[a-zA-Z0-9*]+@[a-zA-Z0-9*]+\.[a-zA-Z0-9*]+'
        match = re.search(email_pattern, prompt)
        return match.group(0) if match else None
