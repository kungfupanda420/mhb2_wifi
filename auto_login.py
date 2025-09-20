import requests
import time
import logging
import sys
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('internet_auto_login.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def check_internet_connection():
    """Check if we have an active internet connection"""
    try:
        response = requests.get("https://httpbin.org/get", timeout=0.1)
        if response.status_code == 200:
            logging.info(" Internet connection is active")
            return True
        return False
    except Exception as e:
        logging.warning(f"No internet connection: {str(e)}")
        return False

def get_credentials():
    auth_user = os.getenv("AUTH_USER")
    auth_pass = os.getenv("AUTH_PASS")
    if not auth_user or not auth_pass:
        logging.error("AUTH_USER or AUTH_PASS not set in environment variables")
        sys.exit(1)
    return auth_user, auth_pass

def login_to_portal():
    """Attempt to login to the captive portal"""
    url = "http://172.20.28.1:8002/index.php?zone=hostelzone"
    auth_user, auth_pass = get_credentials()
    payload = {
        "auth_user": auth_user,
        "auth_pass": auth_pass,
        "redirurl": "https://www.google.com",
        "accept": "Login"
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        logging.info("Attempting to login to portal...")
        response = requests.post(url, data=payload, headers=headers, timeout=5, allow_redirects=True)
        # print(response.text)
        logging.debug(f"Status Code: {response.status_code}")
        logging.debug(f"Final URL: {response.url}")
        
        # Check for successful login indicators
        if response.status_code == 200 and ("success" in response.text.lower() or "google" in response.url.lower()):
            logging.info("✓ Login successful!")
            return True
        elif response.status_code == 302:
            logging.info("✓ Login successful (redirected)")
            return True
        else:
            logging.warning("✗ Login may have failed")
            logging.debug(f"Response text: {response.text[:500]}...")
            return False
            
    except Exception as e:
        logging.error(f"✗ Error during login: {str(e)}")
        return False

def main():
    logging.info("=== Starting Internet Auto-Login Service ===")
    
    # Check if we're already connected
    if check_internet_connection():
        logging.info("Already connected to internet")
        return
    
    # Try to login
    logging.info("No internet connection detected")
    if login_to_portal():
        logging.info("Waiting to verify connection...")
        time.sleep(5)
        logging.info("✓ Internet connection verified after login!")
        # else:
        #     logging.warning("Login appeared successful but internet not working")
    else:
        logging.error("✗ Failed to login to portal")

if __name__ == "__main__":
    main()