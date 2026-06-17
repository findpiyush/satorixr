import json
import os
from playwright.sync_api import sync_playwright

def generate_ui_markers():
    if not os.path.exists("login/state.json"):
        print("state.json not found! Please run login.py first to authenticate and save session state.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        #load
        context = browser.new_context(storage_state="login/state.json")
        page = context.new_page()
        
        print("navigating to dashboard...")
        page.goto("https://try.satorixr.com/home")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        print("extracting ui markers...") #by finding interactive elements and their bounding boxes
        script = """
        () => {
            const elements = document.querySelectorAll('a, button, input, textarea, select, [role="button"], [role="link"], [tabindex]:not([tabindex="-1"])');
            const markers = [];
            
            elements.forEach((el, index) => {
                const rect = el.getBoundingClientRect();
                
                // Only consider elements that are visible and have size
                if (rect.width > 0 && rect.height > 0 && 
                    window.getComputedStyle(el).visibility !== 'hidden' && 
                    window.getComputedStyle(el).display !== 'none') {
                    
                    const text = el.innerText || el.value || el.getAttribute('aria-label') || el.getAttribute('placeholder') || '';
                    
                    const marker = {
                        id: index,
                        tag: el.tagName.toLowerCase(),
                        bounds: [Math.round(rect.x), Math.round(rect.y), Math.round(rect.width), Math.round(rect.height)]
                    };
                    
                    if (text.trim()) marker.text = text.trim().substring(0, 100);
                    
                    const href = el.getAttribute('href');
                    if (href) marker.href = href;
                    
                    const role = el.getAttribute('role');
                    if (role) marker.role = role;

                    markers.push(marker);
                }
            });
            return markers;
        }
        """
        
        markers = page.evaluate(script)
        
        # save/store in json
        output_file = "ui_markers.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(markers, f, indent=4)
            
        print(f"Success! Extracted {len(markers)} UI markers to {output_file}")
        
        browser.close()

if __name__ == "__main__":
    generate_ui_markers()
