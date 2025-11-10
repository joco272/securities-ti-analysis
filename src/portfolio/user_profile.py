import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

# Default profile values
DEFAULT_USERNAME = "User"
DEFAULT_EMAIL = ""
DEFAULT_TICKER = "AAPL"
DEFAULT_INTERVAL = "1d"
DEFAULT_RISK_TOLERANCE = "Medium"

def get_user_profile():
    """
    Returns the user profile. Creates a default profile if none exists.
    Returns a dictionary with profile settings.
    """
    conn = get_db_connection()
    profile = conn.execute("SELECT * FROM user_profile LIMIT 1").fetchone()
    
    if profile is None:
        # Create default profile using INSERT OR IGNORE to handle race conditions
        try:
            conn.execute("""
                INSERT INTO user_profile (username, email, default_ticker, default_interval, risk_tolerance)
                VALUES (?, ?, ?, ?, ?)
            """, (DEFAULT_USERNAME, DEFAULT_EMAIL, DEFAULT_TICKER, DEFAULT_INTERVAL, DEFAULT_RISK_TOLERANCE))
            conn.commit()
            profile = conn.execute("SELECT * FROM user_profile LIMIT 1").fetchone()
        except conn.IntegrityError:
            # Profile was created by another process, fetch it
            profile = conn.execute("SELECT * FROM user_profile LIMIT 1").fetchone()
    
    conn.close()
    return dict(profile) if profile else None

def update_user_profile(username: str, email: str, default_ticker: str, default_interval: str, risk_tolerance: str):
    """
    Updates the user profile with new values.
    Uses UPSERT logic to handle race conditions.
    """
    conn = get_db_connection()
    
    try:
        # Check if profile exists
        profile = conn.execute("SELECT id FROM user_profile LIMIT 1").fetchone()
        
        if profile:
            # Update existing profile
            conn.execute("""
                UPDATE user_profile 
                SET username = ?, email = ?, default_ticker = ?, default_interval = ?, risk_tolerance = ?
                WHERE id = ?
            """, (username, email, default_ticker.upper(), default_interval, risk_tolerance, profile['id']))
        else:
            # Create new profile
            conn.execute("""
                INSERT INTO user_profile (username, email, default_ticker, default_interval, risk_tolerance)
                VALUES (?, ?, ?, ?, ?)
            """, (username, email, default_ticker.upper(), default_interval, risk_tolerance))
        
        conn.commit()
    finally:
        conn.close()

if __name__ == '__main__':
    # Test block for user profile functionality
    print("Testing User Profile Functionality...")
    
    # 1. Get profile (should create default if none exists)
    profile = get_user_profile()
    print("\nInitial Profile:")
    print(f"- Username: {profile['username']}")
    print(f"- Email: {profile['email']}")
    print(f"- Default Ticker: {profile['default_ticker']}")
    print(f"- Default Interval: {profile['default_interval']}")
    print(f"- Risk Tolerance: {profile['risk_tolerance']}")
    
    # 2. Update profile
    print("\nUpdating profile...")
    update_user_profile("John Doe", "john@example.com", "TSLA", "1h", "High")
    
    # 3. Get updated profile
    updated_profile = get_user_profile()
    print("\nUpdated Profile:")
    print(f"- Username: {updated_profile['username']}")
    print(f"- Email: {updated_profile['email']}")
    print(f"- Default Ticker: {updated_profile['default_ticker']}")
    print(f"- Default Interval: {updated_profile['default_interval']}")
    print(f"- Risk Tolerance: {updated_profile['risk_tolerance']}")
    
    print("\nTest complete.")
