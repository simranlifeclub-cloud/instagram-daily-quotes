import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def get_font(font_name, size):
    """
    Loads font from bundled assets/fonts folder, with fallback to system paths.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bundled_path = os.path.join(base_dir, "assets", "fonts", font_name)
    
    if os.path.exists(bundled_path):
        try:
            return ImageFont.truetype(bundled_path, size)
        except Exception:
            pass
            
    # System fallbacks
    fallbacks = [
        f"/System/Library/Fonts/Supplemental/{font_name}",
        f"/System/Library/Fonts/{font_name}",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
    ]
    for p in fallbacks:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
                
    return ImageFont.load_default()


def create_procedural_background(width=1080, height=1920):
    """
    Creates a luxury obsidian & warm gold ambient gradient background
    if no photo background is provided.
    """
    im = Image.new("RGB", (width, height), (10, 12, 20))
    draw = ImageDraw.Draw(im)
    
    # Deep midnight base gradient
    for y in range(height):
        ratio = y / height
        r = int(12 + 10 * math.sin(ratio * math.pi))
        g = int(16 + 12 * ratio)
        b = int(28 + 18 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
        
    return im


def render_quote_card(quote_data, output_path, bg_image_path=None):
    """
    Renders a stunning 1080x1920 Instagram Post / Reel Card for daily publishing.
    """
    target_w, target_h = 1080, 1920
    
    if bg_image_path and os.path.exists(bg_image_path):
        im = Image.open(bg_image_path).convert("RGBA")
        im = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
    else:
        im = create_procedural_background(target_w, target_h).convert("RGBA")
        
    # Atmospheric darkening & vignette overlay for text contrast
    darken = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    d_draw = ImageDraw.Draw(darken)
    
    for y in range(target_h):
        dist_from_center = abs(y - 1000) / 1000.0
        alpha = int(45 + 55 * (1.0 - dist_from_center) + 35 * (y / target_h))
        d_draw.line([(0, y), (target_w, y)], fill=(10, 12, 18, min(140, alpha)))
        
    im = Image.alpha_composite(im, darken)
    draw = ImageDraw.Draw(im)
    
    # Load Typography
    tag_font = get_font("Georgia-Bold.ttf", 24)
    quote_mark_font = get_font("Georgia-Bold.ttf", 120)
    main_quote_font = get_font("Georgia-Bold.ttf", 48)
    sub_quote_font = get_font("Georgia-Italic.ttf", 36)
    footer_font = get_font("Georgia-Bold.ttf", 26)
    safe_font = get_font("Georgia.ttf", 24)

    # 1. Glassmorphism Card Frame
    card_x0, card_y0 = 70, 660
    card_x1, card_y1 = 1010, 1420
    card_w = card_x1 - card_x0
    card_h = card_y1 - card_y0
    
    card_overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card_overlay)
    
    card_draw.rounded_rectangle(
        [card_x0, card_y0, card_x1, card_y1],
        radius=44,
        fill=(12, 16, 26, 205),
        outline=(255, 230, 180, 80),
        width=2
    )
    im = Image.alpha_composite(im, card_overlay)
    draw = ImageDraw.Draw(im)

    # 2. Dynamic Category Badge Pill
    category_text = quote_data.get("category", "DAILY MINDSET • INNER RESILIENCE")
    pill_t_bbox = draw.textbbox((0, 0), category_text, font=tag_font)
    pill_t_w = pill_t_bbox[2] - pill_t_bbox[0]
    pill_w = pill_t_w + 56
    pill_h = 44
    pill_x0 = (target_w - pill_w) // 2
    pill_y0 = card_y0 + 38
    
    pill_overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(pill_overlay)
    p_draw.rounded_rectangle(
        [pill_x0, pill_y0, pill_x0 + pill_w, pill_y0 + pill_h],
        radius=22,
        fill=(24, 32, 50, 240),
        outline=(255, 215, 130, 180),
        width=2
    )
    im = Image.alpha_composite(im, pill_overlay)
    draw = ImageDraw.Draw(im)
    
    draw.text(
        (target_w // 2, pill_y0 + 22),
        category_text,
        font=tag_font,
        fill=(255, 220, 145, 250),
        anchor="mm"
    )

    # 3. Gold Opening Quote Mark
    draw.text(
        (target_w // 2, card_y0 + 135),
        "“",
        font=quote_mark_font,
        fill=(255, 205, 110, 220),
        anchor="mm"
    )

    # 4. Hero Quote Lines
    hero_lines = quote_data.get("hero_lines", ["Words to live by."])
    curr_y = card_y0 + 220
    for line in hero_lines:
        # Drop shadow
        draw.text((target_w // 2 + 2, curr_y + 2), line, font=main_quote_font, fill=(0, 0, 0, 190), anchor="mm")
        # Main text
        draw.text((target_w // 2, curr_y), line, font=main_quote_font, fill=(255, 255, 255, 255), anchor="mm")
        curr_y += 70

    # 5. Elegant Gold Separator Line
    curr_y += 18
    sep_len = 160
    draw.line(
        [(target_w // 2 - sep_len // 2, curr_y), (target_w // 2 + sep_len // 2, curr_y)],
        fill=(255, 210, 120, 160),
        width=2
    )
    curr_y += 45

    # 6. Subtext / Takeaway (Multi-line auto-wrap)
    subtext = quote_data.get("subtext", "")
    words = subtext.split()
    sub_lines = []
    curr_line = ""
    for w in words:
        test_line = curr_line + (" " if curr_line else "") + w
        bbox = draw.textbbox((0, 0), test_line, font=sub_quote_font)
        if (bbox[2] - bbox[0]) > 800:
            if curr_line:
                sub_lines.append(curr_line)
            curr_line = w
        else:
            curr_line = test_line
    if curr_line:
        sub_lines.append(curr_line)

    for line in sub_lines:
        draw.text((target_w // 2 + 1, curr_y + 1), line, font=sub_quote_font, fill=(0, 0, 0, 160), anchor="mm")
        draw.text((target_w // 2, curr_y), line, font=sub_quote_font, fill=(230, 235, 245, 235), anchor="mm")
        curr_y += 54

    # 7. Card Footer Call to Action
    footer_text = quote_data.get("footer", "— SAVE & SHARE IF YOU NEEDED THIS —")
    draw.text(
        (target_w // 2, card_y1 - 42),
        footer_text,
        font=footer_font,
        fill=(255, 205, 110, 210),
        anchor="mm"
    )

    # 8. Instagram / Shorts Platform Safe Zone Headers
    draw.text((target_w // 2, 160), "DAILY INSPIRATION", font=safe_font, fill=(255, 255, 255, 170), anchor="mm")
    draw.text((target_w // 2, 1780), "✦ Wisdom For The Journey ✦", font=safe_font, fill=(255, 255, 255, 180), anchor="mm")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    im.convert("RGB").save(output_path, "PNG", quality=98)
    print(f"Rendered quote card saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    sample_quote = {
        "category": "DAILY MINDSET • INNER RESILIENCE",
        "hero_lines": [
            "The mountain you are carrying,",
            "you were only meant to climb."
        ],
        "subtext": "Trust the quiet season. Your timing is not late — it is preparing you.",
        "footer": "— SAVE & SHARE IF YOU NEEDED THIS —"
    }
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bg_path = os.path.join(base_dir, "assets", "backgrounds", "serene_sunrise.jpg")
    out_path = os.path.join(base_dir, "output", "test_render.png")
    render_quote_card(sample_quote, out_path, bg_path)
