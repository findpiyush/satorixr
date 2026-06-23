from playwright.sync_api import sync_playwright

def login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://try.satorixr.com/login", timeout=60000)
        page.get_by_placeholder("Enter your email to continue").fill("piyush@satorixr.com")
        page.get_by_text("Send Verification Code").click()
        page.wait_for_timeout(5000)
        # browser.close()

if __name__ == "__main__":
    login()