import os
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 8 Curated Color & Mood Themes
THEMES = {
    "GOLDEN_LUXURY": {
        "id": "GOLDEN_LUXURY",
        "name": "Golden Hour & Warm Sun",
        "text_color": (255, 255, 255, 255),
        "shadow_color": (0, 0, 0, 190),
        "vignette_tint": (15, 12, 10),
        "accent_color": (255, 225, 160, 180)
    },
    "EMERALD_MINT": {
        "id": "EMERALD_MINT",
        "name": "Misty Alpine & Forest",
        "text_color": (255, 255, 255, 255),
        "shadow_color": (0, 0, 0, 200),
        "vignette_tint": (8, 18, 12),
        "accent_color": (180, 245, 215, 180)
    },
    "CYAN_HORIZON": {
        "id": "CYAN_HORIZON",
        "name": "Shimmering Ocean & Deep Sea",
        "text_color": (255, 255, 255, 255),
        "shadow_color": (0, 0, 0, 200),
        "vignette_tint": (8, 16, 26),
        "accent_color": (160, 235, 255, 180)
    },
    "SUNSET_EMBER": {
        "id": "SUNSET_EMBER",
        "name": "Fiery Sunset & Twilight Ember",
        "text_color": (255, 255, 255, 255),
        "shadow_color": (0, 0, 0, 200),
        "vignette_tint": (24, 12, 14),
        "accent_color": (255, 205, 175, 180)
    },
    "ROYAL_AMETHYST": {
        "id": "ROYAL_AMETHYST",
        "name": "Twilight Dusk & Celestial",
        "text_color": (255, 255, 255, 255),
        "shadow_color": (0, 0, 0, 200),
        "vignette_tint": (16, 10, 24),
        "accent_color": (225, 200, 255, 180)
    },
    "FROSTED_SILVER": {
        "id": "FROSTED_SILVER",
        "name": "Cozy Rainy Day & Arctic Glass",
        "text_color": (255, 255, 255, 255),
        "shadow_color": (0, 0, 0, 200),
        "vignette_tint": (16, 20, 24),
        "accent_color": (240, 245, 255, 180)
    },
    "DESERT_TERRACOTTA": {
        "id": "DESERT_TERRACOTTA",
        "name": "Warm Dunes & Terracotta",
        "text_color": (255, 255, 255, 255),
        "shadow_color": (0, 0, 0, 200),
        "vignette_tint": (22, 16, 12),
        "accent_color": (255, 220, 180, 180)
    },
    "MONOCHROME_SLATE": {
        "id": "MONOCHROME_SLATE",
        "name": "Minimalist Charcoal & Diamond",
        "text_color": (255, 255, 255, 255),
        "shadow_color": (0, 0, 0, 210),
        "vignette_tint": (12, 14, 16),
        "accent_color": (230, 235, 240, 180)
    }
}

# Auto-match background image to complementary aesthetic theme
BG_THEME_MAP = {
    "shimmering_ocean.jpg": "CYAN_HORIZON",
    "sunset_clouds_beach.jpg": "SUNSET_EMBER",
    "cozy_rainy_window.jpg": "FROSTED_SILVER",
    "golden_hour_trail.jpg": "GOLDEN_LUXURY",
    "misty_mountain_ridge.jpg": "EMERALD_MINT",
    "tropical_green_foliage.jpg": "EMERALD_MINT",
    "snowy_mountain_peak.jpg": "CYAN_HORIZON",
    "twilight_leaf_silhouette.jpg": "ROYAL_AMETHYST",
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


def extract_and_wrap_quote(quote_data, font, draw, max_width=720):
    """
    Extracts the quote text and wraps it gracefully into 3-4 natural, poetic lines.
    Matches the exact minimalist aesthetic shown in viral nature reels.
    """
    # Prefer explicit quote_text, otherwise combine hero_lines
    if "quote_text" in quote_data and quote_data["quote_text"]:
        raw_text = quote_data["quote_text"].strip()
    elif "hero_lines" in quote_data and quote_data["hero_lines"]:
        raw_text = " ".join(quote_data["hero_lines"]).strip()
    else:
        raw_text = "The things I want are valuable, but the things I have are truly invaluable"

    words = raw_text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
        
    return lines


def render_minimalist_quote(quote_data, base_image, theme=None, is_overlay_only=False):
    """
    Renders pure, elegant, minimalist white typography directly on top of the
    cinematic scene with multi-layer soft text shadows and atmospheric diffusion.
    
    Zero clunky cards, zero borders, zero boxes — 100% authentic aesthetic reel style.
    """
    target_w, target_h = 1080, 1920
    
    if not theme:
        theme = THEMES["GOLDEN_LUXURY"]
        
    tint_r, tint_g, tint_b = theme.get("vignette_tint", (10, 12, 18))

    # 1. Typography configuration
    # Georgia gives the timeless, literary editorial feel seen on aesthetic reels
    font_size = 54
    quote_font = get_font("Georgia.ttf", font_size)
    watermark_font = get_font("Georgia.ttf", 20)

    # Initial probe to determine line heights and layout
    temp_draw = ImageDraw.Draw(base_image)
    lines = extract_and_wrap_quote(quote_data, quote_font, temp_draw, max_width=720)

    # If lines are long, adjust font size slightly for ideal proportion
    if len(lines) > 4:
        font_size = 48
        quote_font = get_font("Georgia.ttf", font_size)
        lines = extract_and_wrap_quote(quote_data, quote_font, temp_draw, max_width=740)

    line_spacing = 24
    bbox_list = [temp_draw.textbbox((0, 0), l, font=quote_font) for l in lines]
    line_heights = [b[3] - b[1] for b in bbox_list]
    total_text_h = sum(line_heights) + (len(lines) - 1) * line_spacing

    # Golden ratio center: slightly above vertical middle (y=890) to stay safely above
    # Instagram's bottom UI (account handle, music track, caption)
    start_y = (target_h - total_text_h) // 2 - 30

    # 2. Subtle Atmospheric Vignette Layer (Guarantees 100% legibility on sunny/bright clips)
    vignette = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    
    center_y = start_y + (total_text_h // 2)
    band_height = max(380, total_text_h + 200)
    y_min = max(0, center_y - band_height // 2)
    y_max = min(target_h, center_y + band_height // 2)

    for y in range(y_min, y_max):
        dist = abs(y - center_y) / (band_height / 2.0)
        if dist < 1.0:
            # Soft cosine curve for perfectly invisible blend
            curve = (math.cos(dist * math.pi) + 1.0) / 2.0
            alpha = int(curve * 60) # gentle 0-60 alpha
            v_draw.line([(0, y), (target_w, y)], fill=(tint_r, tint_g, tint_b, alpha))

    base_image = Image.alpha_composite(base_image, vignette)

    # 3. Multi-Offset Diffused Soft Shadow Layer
    # Creates organic depth without looking like hard stroke/outline
    shadow = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)

    # Multi-directional diffused shadow offsets
    shadow_offsets = [
        (0, 2, 70),
        (0, -2, 40),
        (-2, 0, 40),
        (2, 0, 40),
        (-1, 3, 90),
        (1, 3, 90),
        (0, 4, 150),
        (0, 6, 120),
        (0, 8, 70)
    ]
    for ox, oy, alpha in shadow_offsets:
        curr_y = start_y + oy
        for i, line in enumerate(lines):
            s_draw.text(
                (target_w // 2 + ox, curr_y),
                line,
                font=quote_font,
                fill=(0, 0, 0, alpha),
                anchor="ma"
            )
            curr_y += line_heights[i] + line_spacing

    base_image = Image.alpha_composite(base_image, shadow)

    # 4. Primary Crisp White Typography Layer
    text_layer = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    t_draw = ImageDraw.Draw(text_layer)

    curr_y = start_y
    for i, line in enumerate(lines):
        t_draw.text(
            (target_w // 2, curr_y),
            line,
            font=quote_font,
            fill=(255, 255, 255, 255),
            anchor="ma"
        )
        curr_y += line_heights[i] + line_spacing

    # 5. Subtle, Refined Branding at Bottom
    # Clean, delicate, letterspaced watermark that adds trust without distraction
    watermark_text = "@simranlifeclub"
    w_bbox = t_draw.textbbox((0, 0), watermark_text, font=watermark_font)
    t_draw.text(
        (target_w // 2, 1720),
        watermark_text,
        font=watermark_font,
        fill=(255, 255, 255, 140),
        anchor="ma"
    )

    base_image = Image.alpha_composite(base_image, text_layer)
    return base_image


def render_quote_card(quote_data, output_path, bg_image_path=None, theme_name=None):
    """
    Renders a stunning 1080x1920 Instagram Reel Cover / Post with full-bleed
    cinematic nature photography and minimalist white centered typography.
    """
    target_w, target_h = 1080, 1920
    
    bg_filename = os.path.basename(bg_image_path) if bg_image_path else None
    theme = get_theme_for_background(bg_filename, theme_name)

    if bg_image_path and os.path.exists(bg_image_path):
        im = Image.open(bg_image_path).convert("RGBA")
        if im.size != (target_w, target_h):
            im = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
    else:
        im = create_procedural_background(target_w, target_h, theme["id"]).convert("RGBA")

    im = render_minimalist_quote(quote_data, im, theme=theme, is_overlay_only=False)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    im.convert("RGB").save(output_path, "JPEG", quality=96)
    return output_path, theme["id"]


def render_quote_card_overlay(quote_data, output_path, theme_name=None):
    """
    Renders an elegant, transparent 1080x1920 overlay with soft text shadows
    and crisp white typography for direct compositing over motion video loops in FFmpeg.
    """
    target_w, target_h = 1080, 1920
    theme = get_theme_for_background(None, theme_name)
    
    # 1. Full transparency canvas
    transparent_canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    overlay = render_minimalist_quote(quote_data, transparent_canvas, theme=theme, is_overlay_only=True)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    overlay.save(output_path, "PNG")
    return output_path, theme["id"]


if __name__ == "__main__":
    sample_quote = {
        "slot": "morning",
        "quote_text": "The things I want are valuable, but the things I have are truly invaluable",
        "hero_lines": ["The things I want are valuable,", "but the things I have are truly invaluable"]
    }
    out_path = os.path.join(BASE_DIR, "output", "test_aesthetic_render.jpg")
    test_bg = os.path.join(BASE_DIR, "assets", "backgrounds", "shimmering_ocean.jpg")
    render_quote_card(sample_quote, out_path, test_bg)
    print(f"Test aesthetic card successfully rendered: {out_path}")
