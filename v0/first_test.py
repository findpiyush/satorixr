# https://youtu.be/VZ5LU8vHT0s?si=83Mine03Www7uZ2H
from playwright.sync_api import sync_playwright #controls the browser in a syunchronous way

#with statement safely starts and stops Playwright for us
with sync_playwright() as p: #p gives access to browsers
    browser = p.chromium.launch(headless=False)  
    page = browser.new_page() #inside the browser, we're opening a new tab(page)
    page.goto('https://google.com')
    print(page.title())
    browser.close()