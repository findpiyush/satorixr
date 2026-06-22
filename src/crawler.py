import os
import json
import re
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright
from src.capture import capture_page_data

def get_folder_name(url, base_url):
    """
    Generates a safe folder name based on the URL path.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path.strip('/')
    if not path:
        return "root"
    
    # Sanitize path to replace chars that are invalid on filesystems
    folder_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', path)
    
    # If there are query parameters, append sanitized snippet to make it unique
    if parsed_url.query:
        query_sanitized = re.sub(r'[^a-zA-Z0-9_\-]', '_', parsed_url.query)
        folder_name += "_" + query_sanitized[:30]
        
    return folder_name

def crawl_site(start_url, output_dir="captures", state_path="login/state.json", max_pages=15, viewport_width=1280, viewport_height=800):
    """
    Runs a recursive breadth-first crawl starting from start_url.
    Outputs individual page captures in captures/<folder_name> and a global captures/site_graph.json.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse base details
    parsed_start = urlparse(start_url)
    start_domain = parsed_start.netloc
    
    visited_urls = set()
    queue = [start_url]
    
    graph = {
        "start_url": start_url,
        "max_pages_limit": max_pages,
        "pages": [],
        "links": []
    }
    
    folder_mapping = {} # Maps full URL -> folder name

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
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
        
        while queue and len(visited_urls) < max_pages:
            current_url = queue.pop(0)
            
            # Normalize to remove fragments
            parsed_curr = urlparse(current_url)
            normalized_curr = parsed_curr._replace(fragment="").geturl()
            
            if normalized_curr in visited_urls:
                continue
            
            # Determine directory name
            folder_name = get_folder_name(normalized_curr, start_url)
            
            # De-duplicate folder name if two different paths sanitize to the same name
            counter = 1
            original_folder_name = folder_name
            while folder_name in folder_mapping.values():
                folder_name = f"{original_folder_name}_{counter}"
                counter += 1
                
            folder_mapping[normalized_curr] = folder_name
            page_dir = os.path.join(output_dir, folder_name)
            
            print("\n" + "=" * 60)
            print(f"Crawl Step [{len(visited_urls) + 1}/{max_pages}]: {normalized_curr}")
            print(f"Target Directory: {page_dir}")
            print("=" * 60)
            
            try:
                page_info, elements = capture_page_data(
                    page=page,
                    url=normalized_curr,
                    output_dir=page_dir,
                    viewport_width=viewport_width,
                    viewport_height=viewport_height
                )
                
                visited_urls.add(normalized_curr)
                
                # Add node to graph
                graph["pages"].append({
                    "url": normalized_curr,
                    "folder": folder_name,
                    "title": page_info["title"],
                    "element_count": page_info["element_count"]
                })
                
                # Parse outlinks from interactive elements (anchors or anything with href)
                for el in elements:
                    href = el.get("attributes", {}).get("href")
                    if not href:
                        continue
                    
                    # Resolve relative URLs
                    resolved_url = urljoin(normalized_curr, href)
                    
                    # Normalize target URL
                    parsed_res = urlparse(resolved_url)
                    target_normalized = parsed_res._replace(fragment="").geturl()
                    
                    # Crawl constraints checks:
                    # 1. Must be the same domain
                    if parsed_res.netloc != start_domain:
                        continue
                    
                    # 2. Must not contain logout keywords to preserve session state
                    url_lower = target_normalized.lower()
                    logout_keywords = ["logout", "signout", "sign-out", "exit", "log-out"]
                    if any(kw in url_lower for kw in logout_keywords):
                        print(f"Skipping blacklisted logout URL: {target_normalized}")
                        continue
                    
                    # Record the navigational edge in the site graph
                    edge = {
                        "source": normalized_curr,
                        "target": target_normalized,
                        "text": el.get("text", ""),
                        "element_id": el.get("id"),
                        "locator": el.get("playwright_locator", "")
                    }
                    if edge not in graph["links"]:
                        graph["links"].append(edge)
                    
                    # Enqueue target if it hasn't been visited or enqueued
                    if target_normalized not in visited_urls and target_normalized not in queue:
                        queue.append(target_normalized)
                        
            except Exception as e:
                print(f"Failed to crawl/capture {normalized_curr}: {e}")
                # Mark as visited to prevent infinite attempts
                visited_urls.add(normalized_curr)
                
        browser.close()

    # Save the global site graph JSON
    graph_path = os.path.join(output_dir, "site_graph.json")
    with open(graph_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=4)
        
    print("\n" + "=" * 60)
    print("Crawl complete!")
    print(f"Total pages successfully captured: {len(graph['pages'])}")
    print(f"Saved site graph mapping to: {graph_path}")
    print("=" * 60)
    
    return graph
