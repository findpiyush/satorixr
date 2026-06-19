import os
from PIL import Image, ImageDraw, ImageFont

def draw_bounding_boxes(image_path, elements, output_path):
    """
    Loads a screenshot, draws semi-transparent bounding boxes and numeric ID badges
    for each element, and saves the annotated screenshot.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Screenshot not found at {image_path}")

    with Image.open(image_path) as img:
        # Create an RGBA overlay for semi-transparent highlights
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)

        # Try to load a standard system font
        try:
            # Arial is standard on Windows
            font_path = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Fonts", "arial.ttf")
            font = ImageFont.truetype(font_path, 11)
        except Exception:
            font = ImageFont.load_default()

        for el in elements:
            bounds = el.get("bounds")
            if not bounds or len(bounds) != 4:
                continue
            
            x, y, w, h = bounds
            el_id = str(el.get("id"))

            # Draw semi-transparent bounding box
            draw_overlay.rectangle(
                [x, y, x + w, y + h],
                fill=(255, 0, 0, 15),       # very translucent red
                outline=(230, 0, 0, 160),   # semi-translucent red border
                width=2
            )

            # Determine text size for the badge
            try:
                # Pillow 10+
                bbox = draw_overlay.textbbox((x, y), el_id, font=font)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
            except AttributeError:
                # Fallback for older Pillow versions
                tw, th = draw_overlay.textsize(el_id, font=font) if hasattr(draw_overlay, "textsize") else (8, 10)

            # Pad the badge
            pad_x = 3
            pad_y = 1
            badge_w = tw + pad_x * 2
            badge_h = th + pad_y * 2

            # Position badge at the top-left of the bounding box
            bx = max(0, x)
            by = max(0, y - badge_h)

            # Draw solid badge background (bright red)
            draw_overlay.rectangle(
                [bx, by, bx + badge_w, by + badge_h],
                fill=(230, 0, 0, 255)
            )

            # Draw ID text in white
            draw_overlay.text((bx + pad_x, by + pad_y), el_id, fill=(255, 255, 255, 255), font=font)

        # Composite the overlay onto the original image
        if img.mode != "RGBA":
            img_rgba = img.convert("RGBA")
        else:
            img_rgba = img

        composite = Image.alpha_composite(img_rgba, overlay)
        composite.convert("RGB").save(output_path, "PNG")
        print(f"Annotated screenshot saved to: {output_path}")

if __name__ == "__main__":
    # Quick visualizer sanity test
    test_elements = [{"id": 0, "bounds": [50, 50, 100, 40]}]
    # create a mock image if run directly
    mock_img = Image.new("RGB", (200, 200), (240, 240, 240))
    mock_img.save("mock_screenshot.png")
    draw_bounding_boxes("mock_screenshot.png", test_elements, "mock_screenshot_labeled.png")
    os.remove("mock_screenshot.png")
    os.remove("mock_screenshot_labeled.png")
    print("Visualizer self-test complete.")
