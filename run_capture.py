import os
import argparse
from urllib.parse import urlparse
from src.capture import capture_page
from src.crawler import crawl_site

def main():
    parser = argparse.ArgumentParser(description="Capture webpage interactive elements and screenshots for LLM test generation.")
    parser.add_argument("--url", default="https://try.satorixr.com/home", help="Target URL to capture")
    parser.add_argument("--name", default=None, help="Name of the output capture folder. Defaults to URL path segment.")
    parser.add_argument("--state", default="login/state.json", help="Path to state.json login storage file")
    parser.add_argument("--width", type=int, default=1280, help="Viewport width (default: 1280)")
    parser.add_argument("--height", type=int, default=800, help="Viewport height (default: 800)")
    parser.add_argument("--crawl", action="store_true", help="Enable recursive crawling mode of the domain starting from URL")
    parser.add_argument("--max-pages", type=int, default=15, help="Maximum number of pages to crawl (default: 15)")

    args = parser.parse_args()

    # Determine folder name based on URL if not explicitly provided
    if not args.name:
        parsed_url = urlparse(args.url)
        path_segments = [seg for seg in parsed_url.path.split('/') if seg]
        if path_segments:
            # use last segment, sanitize it
            folder_name = path_segments[-1].replace('.', '_').replace('-', '_')
        else:
            # fallback to hostname or 'home'
            folder_name = "home"
    else:
        folder_name = args.name

    # If crawling, the output root defaults to "captures" or a customized "captures/[name]" directory
    if args.crawl:
        output_dir = os.path.join("captures", args.name) if args.name else "captures"
    else:
        output_dir = os.path.join("captures", folder_name)
    
    print("=" * 60)
    if args.crawl:
        print(f"Starting crawl for URL: {args.url}")
        print(f"Max Pages Limit: {args.max_pages}")
    else:
        print(f"Starting single page capture for URL: {args.url}")
    print(f"Output directory: {output_dir}")
    print(f"Viewport resolution: {args.width}x{args.height}")
    print("=" * 60)

    try:
        if args.crawl:
            graph = crawl_site(
                start_url=args.url,
                output_dir=output_dir,
                state_path=args.state,
                max_pages=args.max_pages,
                viewport_width=args.width,
                viewport_height=args.height
            )
            print("=" * 60)
            print("Crawl completed successfully!")
            print(f"Total Pages Captured: {len(graph['pages'])}")
            print(f"Total Navigational Links Found: {len(graph['links'])}")
            print(f"Find all results inside: {os.path.abspath(output_dir)}")
            print("=" * 60)
        else:
            page_info = capture_page(
                url=args.url,
                output_dir=output_dir,
                state_path=args.state,
                viewport_width=args.width,
                viewport_height=args.height
            )
            print("=" * 60)
            print("Capture completed successfully!")
            print(f"Target URL: {page_info['url']}")
            print(f"Page Title: {page_info['title']}")
            print(f"Interactive Elements Found: {page_info['element_count']}")
            print(f"Find all results inside: {os.path.abspath(output_dir)}")
            print("=" * 60)
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
