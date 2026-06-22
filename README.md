# Web Crawler & Page Capture Tool for LLM Test Generation

This tool is a specialized crawling and page-capturing system designed to map a website's layout, structure, and interactive behaviors. The outputs (interactive element lists, robust Playwright locators, screenshots, and visual annotations) are formatted to be fed into Large Language Models (LLMs) to automatically generate comprehensive end-to-end (E2E) Playwright test cases.

---

## Features

- **Automated Login & Session Handling**: Logs in via automated flow, extracts OTPs directly from the mailbox, and saves authentication states for subsequent crawls.
- **Recursive BFS Crawling**: Recursively traverses pages on the same domain up to a user-defined limit, avoiding logout paths to keep the session intact.
- **Playwright Locator Generator**: Automatically suggests the most robust locator calls (e.g., `page.get_by_role`, `page.get_by_label`, `page.get_by_placeholder`, `page.get_by_test_id`) for each element.
- **Unique Selector Solver**: Computes fallback CSS selector paths for elements without text, roles, or attributes.
- **Visual Annotations (Pillow-based)**: Renders a duplicate screenshot (`screenshot_labeled.png`) featuring precise boundary borders and numerical ID badges matching the element JSON records.
- **Global Site Navigation Graph**: Generates a unified `site_graph.json` documenting how pages are connected, complete with corresponding link texts, ids, and recommended click locators.

---

## Directory Structure

```
├── login/
│   ├── login.py            # Playwright script to authenticate with OTP
│   ├── fetchOTP.py         # IMAP client script to fetch login email code
│   └── state.json          # Authenticated session storage state (generated)
├── src/
│   ├── __init__.py         # Package indicator
│   ├── capture.py          # Viewport extraction and JSON generator
│   ├── crawler.py          # Recursive BFS traversal and link builder
│   └── visualizer.py       # PIL screenshot annotation script
├── run_capture.py          # Command Line Interface (CLI) entry point
├── requirements.txt        # Python external dependencies
└── captures/               # Main output directory
    ├── site_graph.json     # Global navigation topology (crawling mode only)
    └── [page_name]/
        ├── page_info.json  # Metadata (url, title, viewport, counts)
        ├── elements.json   # Extracted elements database
        ├── screenshot.png  # Clean viewport screenshot
        └── screenshot_labeled.png # Visual debug overlay screenshot
```

---

## Prerequisites & Installation

### 1. Setup Virtual Environment
Create and activate a Python virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Install Playwright Browsers
```powershell
playwright install chromium
```

---

## Configuration

Add your login credentials to a `.env` file in the root directory:
```env
EMAIL_ADDRESS="your_email@satorixr.com"
EMAIL_PASSWORD="your_app_password_here"
```

---

## Usage

### 1. Perform Authentication
Run the authentication script to obtain `state.json`. It will wait for the OTP to arrive in your mailbox, fill it, sign in, and persist the state:
```powershell
python login/login.py
```

### 2. Run Site Crawler (Recommended)
To recursively traverse and capture pages starting from the home route, use the `--crawl` flag:
```powershell
python run_capture.py --url https://try.satorixr.com/home --crawl --max-pages 10
```
- `--url`: Start URL of the crawl.
- `--crawl`: Enables recursive crawling mode.
- `--max-pages`: Caps the maximum number of pages crawled (default: 15).

### 3. Run Single Page Capture
To capture only a specific page:
```powershell
python run_capture.py --url https://try.satorixr.com/products --name products
```
- `--name`: Explicit name for the output folder (defaults to URL path segment).

---

## Understanding the Outputs

All generated files are saved within the `captures/` folder:

### 1. Page Metadata (`page_info.json`)
Saves core facts about the captured screen:
```json
{
    "url": "https://try.satorixr.com/home",
    "title": "SatoriXR",
    "timestamp": "2026-06-18 09:53:52",
    "viewport": { "width": 1280, "height": 800 },
    "element_count": 19
}
```

### 2. Element Records (`elements.json`)
Lists every visible, interactive element with coordinates and details:
```json
{
    "id": 1,
    "tag": "a",
    "text": "Home",
    "label": "",
    "placeholder": "",
    "type": "",
    "attributes": {
        "id": "",
        "name": "",
        "class": "router-link-active ...",
        "href": "/home",
        "role": ""
    },
    "states": {
        "disabled": false,
        "readonly": false,
        "checked": false,
        "required": false
    },
    "bounds": [16, 96, 224, 40],
    "selector": "div#app > div > div:nth-of-type(1) > div > nav > ul > li:nth-of-type(1) > a",
    "playwright_locator": "page.get_by_role(\"link\", { name: \"Home\" })"
}
```

### 3. Site Navigation Graph (`site_graph.json`)
Contains node configurations (`pages`) and edges (`links`) representing the pathways between pages. Perfect for multi-page integration test generation:
```json
{
    "pages": [...],
    "links": [
        {
            "source": "https://try.satorixr.com/products",
            "target": "https://try.satorixr.com/product/create",
            "text": "Create Product",
            "element_id": 9,
            "locator": "page.get_by_role(\"link\", { name: \"Create Product\" })"
        }
    ]
}
```

### 4. Bounding Box Screenshots (`screenshot_labeled.png`)
A visually annotated screenshot illustrating red-bordered rectangles and small numerical ID tags corresponding to the element IDs in `elements.json`.

---

## Feeding Outputs to an LLM to Write Test Cases

To generate Playwright tests, construct a prompt for your LLM containing:
1. **The Context**: Explain that you want to write a Playwright end-to-end test.
2. **The Graph**: Supply `site_graph.json` so the LLM understands how pages connect and how to traverse them.
3. **Target Pages**: Supply `elements.json` and optionally upload `screenshot_labeled.png` for the page you want to write tests for.
4. **The Instructions**: Ask the LLM to write a script that navigates the workflow using the recommended `playwright_locator` properties and assertions.

### Example Prompt:
> *"Write a Playwright test script in Python that logs in, navigates to the Products list page, and clicks on 'Create Product' to submit a new product form. I have attached `site_graph.json` showing the routes. To navigate, use the `playwright_locator` fields provided in the elements databases. Assert that the product is created successfully."*
