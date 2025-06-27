# email_utils.py
# Additional utility functions for email verification

import re
from typing import Tuple, bool

def validate_email_format(email: str) -> Tuple[bool, str]:
    """
    Validate email format using regex
    Returns: (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "Please enter a valid email address"
    
    # Additional checks
    if len(email) > 254:  # RFC 5321 limit
        return False, "Email address is too long"
    
    local, domain = email.rsplit('@', 1)
    
    if len(local) > 64:  # RFC 5321 limit
        return False, "Email local part is too long"
    
    # Check for common disposable email domains (optional)
    disposable_domains = [
        '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
        'mailinator.com', 'yopmail.com', 'temp-mail.org'
    ]
    
    if domain.lower() in disposable_domains:
        return False, "Disposable email addresses are not allowed"
    
    return True, ""

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Count different character types
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    strength_score = sum([has_upper, has_lower, has_digit, has_special])
    
    if strength_score < 2:
        return False, "Password must contain at least 2 of: uppercase, lowercase, numbers, special characters"
    
    # Check for common weak passwords
    weak_passwords = [
        'password', '12345678', 'qwerty123', 'admin123',
        'password123', 'letmein', 'welcome123'
    ]
    
    if password.lower() in weak_passwords:
        return False, "This password is too common. Please choose a stronger password"
    
    return True, ""

def get_email_verification_status_message(is_verified: bool, email: str) -> str:
    """
    Get appropriate message based on email verification status
    """
    if is_verified:
        return f"✅ Email {email} is verified and ready to use!"
    else:
        return f"⚠️ Please verify your email address ({email}) before logging in. Check your inbox for the verification link."

def format_firebase_error(error_message: str) -> str:
    """
    Format Firebase error messages to be more user-friendly
    """
    error_mappings = {
        "EMAIL_EXISTS": "This email address is already registered. Please use a different email or try logging in.",
        "WEAK_PASSWORD": "Password is too weak. Please use at least 6 characters with a mix of letters and numbers.",
        "INVALID_EMAIL": "Please enter a valid email address.",
        "USER_DISABLED": "This account has been disabled. Please contact support for assistance.",
        "USER_NOT_FOUND": "No account found with this email address. Please check your email or register for a new account.",
        "WRONG_PASSWORD": "Incorrect password. Please try again or reset your password.",
        "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many failed login attempts. Please try again later.",
        "EMAIL_NOT_FOUND": "No account found with this email address.",
        "INVALID_LOGIN_CREDENTIALS": "Invalid email or password. Please check your credentials and try again.",
        "OPERATION_NOT_ALLOWED": "This sign-in method is not enabled. Please contact support.",
        "EXPIRED_OOB_CODE": "The verification link has expired. Please request a new verification email.",
        "INVALID_OOB_CODE": "The verification link is invalid. Please request a new verification email."
    }
    
    for key, message in error_mappings.items():
        if key in error_message:
            return message
    
    return "An unexpected error occurred. Please try again later."

class EmailVerificationTracker:
    """
    Track email verification attempts and provide user feedback
    """
    
    def __init__(self):
        self.max_attempts = 3
        self.cooldown_minutes = 5
    
    def can_resend_verification(self, user_email: str, session_state) -> Tuple[bool, str]:
        """
        Check if user can resend verification email based on attempt limits
        """
        key = f"verification_attempts_{user_email}"
        attempts_key = f"{key}_count"
        last_attempt_key = f"{key}_last_time"
        
        import time
        current_time = time.time()
        
        # Get current attempts
        attempts = session_state.get(attempts_key, 0)
        last_attempt = session_state.get(last_attempt_key, 0)
        
        # Check cooldown period
        if current_time - last_attempt < (self.cooldown_minutes * 60):
            remaining_time = int((self.cooldown_minutes * 60) - (current_time - last_attempt))
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            return False, f"Please wait {minutes}m {seconds}s before requesting another verification email."
        
        # Check max attempts
        if attempts >= self.max_attempts:
            return False, f"Maximum verification attempts ({self.max_attempts}) reached. Please contact support."
        
        return True, ""
    
    def record_verification_attempt(self, user_email: str, session_state):
        """
        Record a verification email attempt
        """
        key = f"verification_attempts_{user_email}"
        attempts_key = f"{key}_count"
        last_attempt_key = f"{key}_last_time"
        
        import time
        session_state[attempts_key] = session_state.get(attempts_key, 0) + 1
        session_state[last_attempt_key] = time.time()