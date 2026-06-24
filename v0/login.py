import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from fetchOTP import fetch_latest_otp

load_dotenv()

def login():
    email_address = os.environ.get("EMAIL_ADDRESS", "piyush@satorixr.com")
    email_password = os.environ.get("EMAIL_PASSWORD")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto("https://try.satorixr.com/login")
        page.get_by_placeholder("Enter your email to continue").fill(email_address)
        page.get_by_text("Send Verification Code").click()
        print("Waiting for OTP...")
        page.wait_for_timeout(5000)
        
        otp = None
        for _ in range(10): 
            otp = fetch_latest_otp(email_address, email_password)
            if otp:
                break
            time.sleep(3)
            
        if otp:
            print(f"OTP received: {otp}")

            page.get_by_text("Enter the verification code").wait_for(state="visible")
            otp_input = page.locator(
                "input[autocomplete='one-time-code'], input[placeholder*='code'], input[aria-label*='code'], input[type='text']:visible"
            ).first
            if otp_input.count() == 0:
                otp_input = page.locator("input:visible").first

            otp_input.fill(otp)
            page.get_by_text("Verify & Sign In").click()
            page.wait_for_timeout(5000)
            
            # Save storage state
            page.context.storage_state(path="v0/state.json")
            print("Login state saved to state.json")
        else:
            print("Failed to receive OTP.")
        
        # browser.close()

if __name__ == "__main__":
    login()