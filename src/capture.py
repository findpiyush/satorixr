import os
import json
import time
import shutil
from playwright.sync_api import sync_playwright
from src.visualizer import draw_bounding_boxes

def capture_page_data(page, url, output_dir, viewport_width=1280, viewport_height=800):
    """
    Performs navigation, elements extraction, screenshots, and visual overlay marking
    on an existing page object. Returns (page_info, elements_list).
    """
    os.makedirs(output_dir, exist_ok=True)
    
    screenshot_path = os.path.join(output_dir, "screenshot.png")
    labeled_screenshot_path = os.path.join(output_dir, "screenshot_labeled.png")
    elements_json_path = os.path.join(output_dir, "elements.json")
    metadata_json_path = os.path.join(output_dir, "page_info.json")

    print(f"Navigating to: {url} ...")
    try:
        page.goto(url)
        page.wait_for_load_state("networkidle", timeout=20000)
    except Exception as e:
        print(f"Navigation/load state warning for {url}: {e}")

    # Give page JavaScript additional time to render dynamic or lazy-loaded UI.
    page.wait_for_timeout(3000)
    try:
        page.mouse.move(viewport_width / 2, viewport_height / 2)
        page.wait_for_timeout(500)
    except Exception:
        pass

    try:
        page.wait_for_function(
            "() => window.document.readyState === 'complete' || window.document.readyState === 'interactive'",
            timeout=10000
        )
    except Exception:
        pass

    page_title = page.title()
    current_url = page.url
    print(f"Page title: '{page_title}' | Current URL: '{current_url}'")

    # Javascript extraction script
    extraction_js = """
    () => {
        function getLabelText(el) {
            // 1. Check for label with 'for' attribute matching el.id
            if (el.id) {
                const label = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
                if (label && label.innerText.trim()) {
                    return label.innerText.trim();
                }
            }
            // 2. Check parent label
            let parent = el.parentElement;
            while (parent) {
                if (parent.tagName.toLowerCase() === 'label' && parent.innerText.trim()) {
                    return parent.innerText.trim();
                }
                parent = parent.parentElement;
            }
            return '';
        }

        function getCssSelector(el) {
            if (el.id) {
                try {
                    if (document.querySelectorAll(`#${CSS.escape(el.id)}`).length === 1) {
                        return `#${el.id}`;
                    }
                } catch (e) {}
            }
            const path = [];
            let current = el;
            while (current && current.nodeType === Node.ELEMENT_NODE) {
                let selector = current.nodeName.toLowerCase();
                if (current.id) {
                    selector += `#${current.id}`;
                    path.unshift(selector);
                    break;
                } else {
                    let sib = current, sibIndex = 1;
                    while (sib = sib.previousElementSibling) {
                        if (sib.nodeName.toLowerCase() === current.nodeName.toLowerCase()) {
                            sibIndex++;
                        }
                    }
                    if (sibIndex > 1 || current.nextElementSibling) {
                        selector += `:nth-of-type(${sibIndex})`;
                    }
                }
                path.unshift(selector);
                current = current.parentElement;
            }
            return path.join(' > ');
        }

        function getPlaywrightLocator(el, tag, text, labelText) {
            // 1. data-testid
            const testId = el.getAttribute('data-testid');
            if (testId) {
                return `page.get_by_test_id("${testId}")`;
            }

            // 2. label
            if (labelText) {
                const cleanLabel = labelText.replace(/\\n+/g, ' ').trim().substring(0, 50);
                return `page.get_by_label("${cleanLabel}")`;
            }

            // 3. placeholder (for inputs / textareas)
            const placeholder = el.getAttribute('placeholder');
            if (placeholder && (tag === 'input' || tag === 'textarea')) {
                const cleanPlaceholder = placeholder.replace(/\\n+/g, ' ').trim().substring(0, 50);
                return `page.get_by_placeholder("${cleanPlaceholder}")`;
            }

            // 4. Role-based locator
            let role = el.getAttribute('role');
            if (!role) {
                if (tag === 'button') role = 'button';
                else if (tag === 'a') role = 'link';
                else if (tag === 'input') {
                    const type = el.getAttribute('type') || 'text';
                    if (type === 'checkbox') role = 'checkbox';
                    else if (type === 'radio') role = 'radio';
                    else if (type === 'button' || type === 'submit' || type === 'reset') role = 'button';
                    else role = 'textbox';
                }
                else if (tag === 'textarea') role = 'textbox';
                else if (tag === 'select') role = 'combobox';
            }

            const cleanText = text ? text.replace(/\\s+/g, ' ').trim().substring(0, 50) : '';

            if (role && cleanText) {
                return `page.get_by_role("${role}", { name: "${cleanText}" })`;
            } else if (role) {
                const nameAttr = el.getAttribute('name');
                if (nameAttr) {
                    return `page.locator('${tag}[name="${nameAttr}"]')`;
                }
            }

            // 5. fallback to text
            if (cleanText) {
                return `page.get_by_text("${cleanText}")`;
            }

            // 6. CSS selector fallback
            return `page.locator('${getCssSelector(el)}')`;
        }

        const interactiveCandidates = document.querySelectorAll(
            'a, button, input, textarea, select, [role="button"], [role="link"], [role="checkbox"], [role="radio"], [role="tab"], [role="menuitem"], [tabindex]:not([tabindex="-1"])'
        );

        const textCandidates = document.querySelectorAll(
            'h1, h2, h3, h4, h5, h6, p, span, label, li, td, th, strong, em, small, div'
        );

        const list = [];
        let idCounter = 0;
        const seen = new Set();

        function getBounds(rect) {
            return [
                Math.round(rect.x),
                Math.round(rect.y),
                Math.round(rect.width),
                Math.round(rect.height)
            ];
        }

        function isVisibleInViewport(el, rect) {
            const style = window.getComputedStyle(el);
            const isStyleVisible = style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
            const hasDimensions = rect.width > 0 && rect.height > 0;
            const isInViewport = rect.bottom >= 0 && rect.right >= 0 &&
                                 rect.top <= window.innerHeight && rect.left <= window.innerWidth;
            return isStyleVisible && hasDimensions && isInViewport;
        }

        function pushElement(el, kind, locator) {
            const rect = el.getBoundingClientRect();
            if (!isVisibleInViewport(el, rect)) return;

            const tag = el.tagName.toLowerCase();
            const text = (el.innerText || el.value || el.getAttribute('aria-label') || '').trim();
            const labelText = getLabelText(el);
            const bounds = getBounds(rect);

            const dedupeKey = `${kind}|${tag}|${bounds.join(',')}|${text.substring(0, 120)}`;
            if (seen.has(dedupeKey)) return;
            seen.add(dedupeKey);

            list.push({
                id: idCounter++,
                kind: kind,
                tag: tag,
                text: text.substring(0, 100),
                label: labelText,
                placeholder: el.getAttribute('placeholder') || '',
                type: el.getAttribute('type') || '',
                attributes: {
                    id: el.id || '',
                    name: el.getAttribute('name') || '',
                    class: el.getAttribute('class') || '',
                    href: el.getAttribute('href') || '',
                    role: el.getAttribute('role') || ''
                },
                states: {
                    disabled: el.disabled || el.getAttribute('aria-disabled') === 'true',
                    readonly: el.readOnly || el.getAttribute('aria-readonly') === 'true',
                    checked: el.checked || el.getAttribute('aria-checked') === 'true',
                    required: el.required || el.getAttribute('aria-required') === 'true'
                },
                bounds: bounds,
                selector: getCssSelector(el),
                playwright_locator: locator
            });
        }

        interactiveCandidates.forEach((el) => {
            const tag = el.tagName.toLowerCase();
            const text = (el.innerText || el.value || el.getAttribute('aria-label') || '').trim();
            const labelText = getLabelText(el);
            const locator = getPlaywrightLocator(el, tag, text, labelText);
            pushElement(el, 'interactive', locator);
        });

        textCandidates.forEach((el) => {
            // Skip text nodes that are inside interactive controls; they are already captured.
            if (el.closest('a, button, input, textarea, select, [role="button"], [role="link"], [role="checkbox"], [role="radio"], [role="tab"], [role="menuitem"]')) {
                return;
            }

            const text = (el.innerText || '').replace(/\\s+/g, ' ').trim();
            if (!text) return;

            // Keep only leaf-level readable text blocks to reduce noisy container captures.
            const childElements = Array.from(el.children || []);
            const hasReadableChildText = childElements.some((child) => {
                if (!child || child.nodeType !== Node.ELEMENT_NODE) return false;
                const childText = (child.innerText || '').replace(/\\s+/g, ' ').trim();
                if (!childText) return false;
                const childRect = child.getBoundingClientRect();
                const childStyle = window.getComputedStyle(child);
                const childVisible = childStyle.display !== 'none' && childStyle.visibility !== 'hidden' && childStyle.opacity !== '0';
                return childVisible && childRect.width > 0 && childRect.height > 0;
            });
            if (hasReadableChildText) return;

            // Avoid giant layout wrappers and non-human content blocks.
            const rect = el.getBoundingClientRect();
            const maxReasonableArea = window.innerWidth * window.innerHeight * 0.6;
            if (rect.width * rect.height > maxReasonableArea) return;
            if (text.length > 300) return;

            pushElement(el, 'text', `page.locator('${getCssSelector(el)}')`);
        });

        return list;
    }
    """

    elements = page.evaluate(extraction_js)
    print(f"Extracted {len(elements)} visible interactive elements.")

    # Save screenshot
    page.screenshot(path=screenshot_path)
    print(f"Saved clean screenshot to: {screenshot_path}")

    # Save elements JSON
    with open(elements_json_path, "w", encoding="utf-8") as f:
        json.dump(elements, f, indent=4)
    print(f"Saved elements JSON data to: {elements_json_path}")

    # Save page metadata info
    page_info = {
        "url": current_url,
        "title": page_title,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "viewport": {"width": viewport_width, "height": viewport_height},
        "element_count": len(elements)
    }
    with open(metadata_json_path, "w", encoding="utf-8") as f:
        json.dump(page_info, f, indent=4)
    print(f"Saved page metadata info to: {metadata_json_path}")

    # Draw visual annotations on the screenshot
    if len(elements) > 0:
        try:
            draw_bounding_boxes(screenshot_path, elements, labeled_screenshot_path)
        except Exception as e:
            print(f"Error drawing annotations: {e}")
            shutil.copy(screenshot_path, labeled_screenshot_path)
    else:
        shutil.copy(screenshot_path, labeled_screenshot_path)
        print("No interactive elements found to annotate.")

    return page_info, elements

def capture_page(url, output_dir, state_path="login/state.json", viewport_width=1280, viewport_height=800, headless=True):
    """
    Standalone runner (legacy compatibility). Runs single page capture in its own browser lifecycle.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context_args = {
            "viewport": {"width": viewport_width, "height": viewport_height}
        }
        if os.path.exists(state_path):
            context_args["storage_state"] = state_path
            print(f"Loaded session state from: {state_path}")
        else:
            print(f"Warning: Session state file not found at {state_path}. Proceeding unauthenticated.")

        context = browser.new_context(**context_args)
        page = context.new_page()
        
        page_info, _ = capture_page_data(page, url, output_dir, viewport_width, viewport_height)
        
        browser.close()
        
    return page_info
