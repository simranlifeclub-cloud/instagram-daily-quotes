import os
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 8 Luxury Aesthetic Visual Themes
THEMES = {
    "GOLDEN_LUXURY": {
        "id": "GOLDEN_LUXURY",
        "name": "24k Obsidian & Gold",
        "card_fill": (12, 16, 26, 215),
        "card_outline": (255, 225, 160, 90),
        "pill_fill": (24, 32, 50, 245),
        "pill_outline": (255, 215, 130, 185),
        "pill_text": (255, 220, 145, 255),
        "quote_mark": (255, 205, 110, 230),
        "hero_text": (255, 255, 255, 255),
        "separator": (255, 210, 120, 165),
        "subtext": (235, 238, 245, 235),
        "footer": (255, 205, 110, 215),
        "safe_accent": (255, 225, 160, 190)
    },
    "EMERALD_MINT": {
        "id": "EMERALD_MINT",
        "name": "Deep Forest & Mint Sage",
        "card_fill": (8, 22, 18, 220),
        "card_outline": (120, 230, 180, 90),
        "pill_fill": (14, 42, 34, 245),
        "pill_outline": (140, 240, 195, 185),
        "pill_text": (180, 255, 220, 255),
        "quote_mark": (140, 240, 190, 230),
        "hero_text": (255, 255, 255, 255),
        "separator": (120, 230, 180, 165),
        "subtext": (220, 245, 235, 235),
        "footer": (160, 245, 200, 215),
        "safe_accent": (140, 240, 190, 190)
    },
    "CYAN_HORIZON": {
        "id": "CYAN_HORIZON",
        "name": "Midnight Ocean & Electric Cyan",
        "card_fill": (10, 18, 30, 220),
        "card_outline": (100, 210, 255, 95),
        "pill_fill": (18, 36, 60, 245),
        "pill_outline": (120, 225, 255, 185),
        "pill_text": (160, 235, 255, 255),
        "quote_mark": (100, 220, 255, 230),
        "hero_text": (255, 255, 255, 255),
        "separator": (100, 210, 255, 165),
        "subtext": (225, 240, 255, 235),
        "footer": (130, 225, 255, 215),
        "safe_accent": (100, 210, 255, 190)
    },
    "SUNSET_EMBER": {
        "id": "SUNSET_EMBER",
        "name": "Twilight Ember & Rose Gold",
        "card_fill": (24, 14, 18, 220),
        "card_outline": (255, 170, 130, 95),
        "pill_fill": (48, 24, 30, 245),
        "pill_outline": (255, 180, 140, 185),
        "pill_text": (255, 205, 180, 255),
        "quote_mark": (255, 165, 120, 230),
        "hero_text": (255, 255, 255, 255),
        "separator": (255, 165, 120, 165),
        "subtext": (255, 235, 230, 235),
        "footer": (255, 175, 135, 215),
        "safe_accent": (255, 180, 140, 190)
    },
    "ROYAL_AMETHYST": {
        "id": "ROYAL_AMETHYST",
        "name": "Celestial Galaxy & Lilac Velvet",
        "card_fill": (18, 12, 28, 220),
        "card_outline": (210, 170, 255, 90),
        "pill_fill": (36, 22, 56, 245),
        "pill_outline": (220, 180, 255, 185),
        "pill_text": (235, 210, 255, 255),
        "quote_mark": (215, 165, 255, 230),
        "hero_text": (255, 255, 255, 255),
        "separator": (210, 165, 255, 165),
        "subtext": (240, 230, 255, 235),
        "footer": (220, 180, 255, 215),
        "safe_accent": (215, 175, 255, 190)
    },
    "FROSTED_SILVER": {
        "id": "FROSTED_SILVER",
        "name": "Minimalist Frosted Arctic Glass",
        "card_fill": (22, 26, 34, 200),
        "card_outline": (235, 242, 255, 100),
        "pill_fill": (38, 44, 56, 245),
        "pill_outline": (240, 245, 255, 185),
        "pill_text": (245, 250, 255, 255),
        "quote_mark": (240, 245, 255, 230),
        "hero_text": (255, 255, 255, 255),
        "separator": (220, 230, 245, 165),
        "subtext": (240, 245, 255, 240),
        "footer": (230, 240, 255, 220),
        "safe_accent": (235, 242, 255, 190)
    },
    "DESERT_TERRACOTTA": {
        "id": "DESERT_TERRACOTTA",
        "name": "Sahara Dunes & Warm Sand Gold",
        "card_fill": (24, 18, 14, 220),
        "card_outline": (235, 185, 130, 90),
        "pill_fill": (46, 32, 24, 245),
        "pill_outline": (245, 195, 140, 185),
        "pill_text": (255, 225, 180, 255),
        "quote_mark": (245, 180, 110, 230),
        "hero_text": (255, 255, 255, 255),
        "separator": (235, 180, 120, 165),
        "subtext": (245, 235, 225, 235),
        "footer": (245, 190, 130, 215),
        "safe_accent": (240, 190, 130, 190)
    },
    "MONOCHROME_SLATE": {
        "id": "MONOCHROME_SLATE",
        "name": "Brutalist Graphite & Diamond Slate",
        "card_fill": (14, 15, 18, 225),
        "card_outline": (195, 200, 210, 85),
        "pill_fill": (28, 30, 36, 245),
        "pill_outline": (205, 210, 220, 185),
        "pill_text": (235, 240, 245, 255),
        "quote_mark": (210, 215, 225, 230),
        "hero_text": (255, 255, 255, 255),
        "separator": (190, 195, 205, 165),
        "subtext": (230, 235, 240, 235),
        "footer": (200, 205, 215, 215),
        "safe_accent": (210, 215, 225, 190)
    }
}

# Auto-match background image to complementary aesthetic theme
BG_THEME_MAP = {
    "misty_forest.jpg": "EMERALD_MINT",
    "emerald_waterfall.jpg": "EMERALD_MINT",
    "ocean_waves.jpg": "CYAN_HORIZON",
    "city_twilight.jpg": "SUNSET_EMBER",
    "starry_night.jpg": "ROYAL_AMETHYST",
    "golden_mountain.jpg": "GOLDEN_LUXURY",
    "serene_sunrise.jpg": "GOLDEN_LUXURY",
    "desert_dunes.jpg": "DESERT_TERRACOTTA",
    "minimalist_arch.jpg": "FROSTED_SILVER"
}


def get_font(font_name, size):
    """
    Loads font from bundled assets/fonts folder, with fallback to system paths.
    """
    bundled_path = os.path.join(BASE_DIR, "assets", "fonts", font_name)
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


def get_theme_for_background(bg_filename=None, preferred_theme=None):
    """Resolves visual theme from preference or background filename."""
    if preferred_theme and preferred_theme in THEMES:
        return THEMES[preferred_theme]
    
    if bg_filename:
        base_name = os.path.basename(bg_filename).lower()
        if base_name in BG_THEME_MAP:
            return THEMES[BG_THEME_MAP[base_name]]
    
    return random.choice(list(THEMES.values()))


def create_procedural_background(width=1080, height=1920, theme_id="GOLDEN_LUXURY"):
    """
    Creates dynamic ambient gradient background if no photo background is provided.
    """
    im = Image.new("RGB", (width, height), (10, 12, 20))
    draw = ImageDraw.Draw(im)
    
    base_tones = {
        "EMERALD_MINT": (8, 24, 16),
        "CYAN_HORIZON": (8, 18, 32),
        "SUNSET_EMBER": (28, 14, 18),
        "ROYAL_AMETHYST": (20, 10, 30),
        "DESERT_TERRACOTTA": (26, 18, 12),
        "FROSTED_SILVER": (16, 20, 26),
        "MONOCHROME_SLATE": (12, 14, 16),
        "GOLDEN_LUXURY": (14, 16, 24)
    }
    r0, g0, b0 = base_tones.get(theme_id, (14, 16, 24))

    for y in range(height):
        ratio = y / height
        r = int(r0 + 12 * math.sin(ratio * math.pi))
        g = int(g0 + 14 * ratio)
        b = int(b0 + 20 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
        
    return im


def get_safe_zone_text(quote_data):
    """Generates context-rich header text for Instagram safe zone."""
    slot = quote_data.get("slot", "").lower()
    headers = {
        "morning": "✦ MORNING CLARITY & AMBITION ✦",
        "midday": "✦ RELENTLESS FOCUS & DISCIPLINE ✦",
        "afternoon": "✦ INNER RESILIENCE & GRIT ✦",
        "evening": "✦ EVENING WISDOM & GROWTH ✦",
        "night": "✦ PEACE OF MIND & SELF BELIEF ✦"
    }
    return headers.get(slot, "✦ DAILY INSPIRATION & WISDOM ✦")


def render_quote_card(quote_data, output_path, bg_image_path=None, theme_name=None):
    """
    Renders a stunning 1080x1920 Instagram Post / Reel Card for daily publishing
    with dynamic aesthetic themes, custom typography, and glassmorphic elevation.
    """
    target_w, target_h = 1080, 1920
    
    # 1. Resolve Theme
    bg_filename = os.path.basename(bg_image_path) if bg_image_path else None
    theme = get_theme_for_background(bg_filename, theme_name)
    theme_id = theme["id"]

    # 2. Base Background Layer
    if bg_image_path and os.path.exists(bg_image_path):
        im = Image.open(bg_image_path).convert("RGBA")
        im = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
    else:
        im = create_procedural_background(target_w, target_h, theme_id).convert("RGBA")
        
    # 3. Atmospheric Darkening & Vignette Overlay for Text Contrast
    darken = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    d_draw = ImageDraw.Draw(darken)
    
    for y in range(target_h):
        dist_from_center = abs(y - 1000) / 1000.0
        alpha = int(45 + 55 * (1.0 - dist_from_center) + 40 * (y / target_h))
        d_draw.line([(0, y), (target_w, y)], fill=(10, 12, 18, min(145, alpha)))
        
    im = Image.alpha_composite(im, darken)
    draw = ImageDraw.Draw(im)
    
    # 4. Load Typography
    tag_font = get_font("Georgia-Bold.ttf", 24)
    quote_mark_font = get_font("Georgia-Bold.ttf", 120)
    main_quote_font = get_font("Georgia-Bold.ttf", 48)
    sub_quote_font = get_font("Georgia-Italic.ttf", 36)
    footer_font = get_font("Georgia-Bold.ttf", 26)
    safe_font = get_font("Georgia-Bold.ttf", 23)

    # 5. Measure Content Height for Dynamic Golden-Ratio Card Centering
    hero_lines = quote_data.get("hero_lines", ["Words to live by."])
    subtext = quote_data.get("subtext", "")
    
    # Wrap subtext
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

    # Calculate optimal card bounds
    content_height = 140 + (len(hero_lines) * 72) + 70 + (len(sub_lines) * 54) + 110
    card_h = max(740, min(840, content_height))
    card_y0 = (target_h - card_h) // 2 + 30
    card_y1 = card_y0 + card_h
    card_x0, card_x1 = 70, 1010
    
    # 6. Glassmorphism Card Frame
    card_overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card_overlay)
    
    card_draw.rounded_rectangle(
        [card_x0, card_y0, card_x1, card_y1],
        radius=44,
        fill=theme["card_fill"],
        outline=theme["card_outline"],
        width=2
    )
    im = Image.alpha_composite(im, card_overlay)
    draw = ImageDraw.Draw(im)

    # 7. Category Badge Pill
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
        fill=theme["pill_fill"],
        outline=theme["pill_outline"],
        width=2
    )
    im = Image.alpha_composite(im, pill_overlay)
    draw = ImageDraw.Draw(im)
    
    draw.text(
        (target_w // 2, pill_y0 + 22),
        category_text,
        font=tag_font,
        fill=theme["pill_text"],
        anchor="mm"
    )

    # 8. Opening Quote Mark
    draw.text(
        (target_w // 2, card_y0 + 135),
        "“",
        font=quote_mark_font,
        fill=theme["quote_mark"],
        anchor="mm"
    )

    # 9. Hero Quote Lines
    curr_y = card_y0 + 220
    for line in hero_lines:
        # Drop shadow for depth
        draw.text((target_w // 2 + 2, curr_y + 2), line, font=main_quote_font, fill=(0, 0, 0, 190), anchor="mm")
        # Main text
        draw.text((target_w // 2, curr_y), line, font=main_quote_font, fill=theme["hero_text"], anchor="mm")
        curr_y += 72

    # 10. Themed Separator Line & Accents
    curr_y += 14
    sep_len = 160
    draw.line(
        [(target_w // 2 - sep_len // 2, curr_y), (target_w // 2 + sep_len // 2, curr_y)],
        fill=theme["separator"],
        width=2
    )
    curr_y += 45

    # 11. Subtext / Takeaway Lines
    for line in sub_lines:
        draw.text((target_w // 2 + 1, curr_y + 1), line, font=sub_quote_font, fill=(0, 0, 0, 160), anchor="mm")
        draw.text((target_w // 2, curr_y), line, font=sub_quote_font, fill=theme["subtext"], anchor="mm")
        curr_y += 54

    # 12. Card Footer Call to Action
    footer_text = quote_data.get("footer", "— SAVE & SHARE IF YOU NEEDED THIS —")
    draw.text(
        (target_w // 2, card_y1 - 42),
        footer_text,
        font=footer_font,
        fill=theme["footer"],
        anchor="mm"
    )

    # 13. Platform Safe Zone Top & Bottom Headers
    top_safe_text = get_safe_zone_text(quote_data)
    draw.text((target_w // 2, 160), top_safe_text, font=safe_font, fill=theme["safe_accent"], anchor="mm")
    draw.text((target_w // 2, 1780), "✦ Simran Life Club ✦", font=safe_font, fill=(255, 255, 255, 180), anchor="mm")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    im.convert("RGB").save(output_path, "PNG", quality=98)
    return output_path, theme["id"]


if __name__ == "__main__":
    sample_quote = {
        "slot": "morning",
        "category": "MORNING MINDSET • RESILIENCE",
        "hero_lines": [
            "The mountain you are carrying,",
            "you were only meant to climb."
        ],
        "subtext": "Trust the quiet season. Your timing is not late — it is preparing you.",
        "footer": "— SAVE & SHARE IF YOU NEEDED THIS —"
    }
    out_path = os.path.join(BASE_DIR, "output", "test_render.png")
    test_bg = os.path.join(BASE_DIR, "assets", "backgrounds", "misty_forest.jpg")
    render_quote_card(sample_quote, out_path, test_bg)
    print(f"Test card successfully rendered with theme!")
