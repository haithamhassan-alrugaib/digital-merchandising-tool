"""
Lightweight wireframe SVGs per block type, used in the merchandising input
tool so users can SEE the block shape before filling it in.

Conventions:
- Image placeholder = light grey box with a diagonal X
- Text line = short grey rounded bar
- Button/CTA = small bordered pill
- Everything sits in a 280x150 viewBox so it renders small and consistent
"""

W, H = 280, 150
BORDER = "#D9D4C9"
FILL_LIGHT = "#F2EFE9"
FILL_IMG = "#E5E0D5"
GOLD = "#D4AF37"
CHARCOAL = "#121212"
TEXT_GREY = "#B0AA9A"


def _frame(inner: str) -> str:
    return (
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
        f'preserveAspectRatio="xMidYMid meet">{inner}</svg>'
    )


def _img_box(x, y, w, h):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{FILL_IMG}" stroke="{BORDER}"/>'
        f'<line x1="{x}" y1="{y}" x2="{x+w}" y2="{y+h}" stroke="{BORDER}" stroke-width="1"/>'
        f'<line x1="{x+w}" y1="{y}" x2="{x}" y2="{y+h}" stroke="{BORDER}" stroke-width="1"/>'
    )


def _text_line(x, y, w, h=6, color=TEXT_GREY):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{color}"/>'


def _pill(x, y, w, h=14, color=GOLD):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{color}"/>'


def _dot(cx, cy, r=10):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{FILL_IMG}" stroke="{BORDER}"/>'


# ---------------------------------------------------------------------------
# Per-type wireframe builders
# ---------------------------------------------------------------------------

def hero():
    inner = _img_box(10, 10, 260, 100)
    inner += _text_line(20, 120, 140, 8)
    inner += _text_line(20, 132, 90, 6, color="#D0CABA")
    inner += _pill(220, 122, 50, 16)
    return _frame(inner)


def hero_image():
    inner = _img_box(10, 10, 260, 120)
    inner += _text_line(20, 134, 100, 7)
    return _frame(inner)


def banner():
    inner = _img_box(10, 10, 260, 80)
    inner += _text_line(20, 100, 160, 8)
    inner += _pill(20, 116, 60, 16)
    return _frame(inner)


def category_icon_strip(n=6):
    inner = ""
    gap = W / n
    for i in range(n):
        cx = gap * i + gap / 2
        inner += _dot(cx, 35, r=20)
        inner += _text_line(cx - 18, 62, 36, 5)
    inner += _text_line(10, 100, 260, 1, color=BORDER)
    return _frame(inner)


def category_tile_grid():
    inner = ""
    positions = [(10, 10), (145, 10), (10, 80), (145, 80)]
    for x, y in positions:
        inner += _img_box(x, y, 125, 60)
        inner += _text_line(x + 8, y + 45, 70, 7, color="#FFFFFF")
    return _frame(inner)


def product_carousel(n=4):
    inner = ""
    card_w = 55
    gap = 8
    for i in range(n):
        x = 10 + i * (card_w + gap)
        inner += _img_box(x, 10, card_w, 70)
        inner += _text_line(x, 86, card_w - 8, 6)
        inner += _text_line(x, 96, card_w - 18, 6, color="#D0CABA")
    inner += f'<circle cx="265" cy="45" r="12" fill="#FFFFFF" stroke="{BORDER}"/>'
    inner += f'<path d="M262 40 l6 5 l-6 5" stroke="{CHARCOAL}" stroke-width="2" fill="none"/>'
    return _frame(inner)


def two_up_banner():
    inner = _img_box(10, 10, 125, 110)
    inner += _img_box(145, 10, 125, 110)
    inner += _text_line(18, 130, 100, 7)
    inner += _text_line(153, 130, 100, 7)
    return _frame(inner)


def three_up_strip():
    inner = ""
    for i in range(3):
        x = 10 + i * 88
        inner += _img_box(x, 10, 80, 90)
        inner += _text_line(x + 5, 106, 60, 6)
    return _frame(inner)


def four_up_strip():
    inner = ""
    for i in range(4):
        x = 10 + i * 65
        inner += _img_box(x, 10, 58, 90)
        inner += _text_line(x + 4, 106, 45, 6)
    return _frame(inner)


def spotlight_card(n=2):
    inner = ""
    card_w = 120
    gap = 20
    for i in range(n):
        x = 10 + i * (card_w + gap)
        inner += _img_box(x, 10, card_w, 90)
        inner += _text_line(x, 106, card_w - 20, 7)
        inner += _pill(x, 122, 70, 14)
    return _frame(inner)


def circular_spotlight(n=5):
    inner = ""
    gap = W / n
    for i in range(n):
        cx = gap * i + gap / 2
        inner += _dot(cx, 40, r=24)
        inner += _text_line(cx - 20, 72, 40, 6)
    return _frame(inner)


def image_pair_grid():
    inner = ""
    positions = [(10, 10), (145, 10), (10, 78), (145, 78)]
    for x, y in positions:
        inner += _img_box(x, y, 125, 60)
    return _frame(inner)


def nav_tabs():
    inner = ""
    labels_w = [55, 55, 55, 55]
    x = 10
    for i, w in enumerate(labels_w):
        color = GOLD if i == 0 else FILL_LIGHT
        inner += f'<rect x="{x}" y="10" width="{w}" height="20" fill="{color}" stroke="{BORDER}"/>'
        x += w
    inner += _img_box(10, 40, 260, 90)
    return _frame(inner)


def vertical_nav_rail():
    inner = ""
    for i in range(5):
        y = 10 + i * 26
        fill = FILL_LIGHT if i != 0 else "#FFFFFF"
        inner += f'<rect x="10" y="{y}" width="70" height="22" fill="{fill}" stroke="{BORDER}"/>'
        inner += _text_line(16, y + 9, 50, 5)
    inner += _img_box(90, 10, 180, 130)
    return _frame(inner)


def mega_menu():
    inner = f'<rect x="0" y="0" width="{W}" height="20" fill="{FILL_LIGHT}"/>'
    for i in range(3):
        x = 10 + i * 60
        inner += _text_line(x, 50 + 0, 45, 6)
        for j in range(3):
            inner += _text_line(x, 65 + j * 14, 50, 5, color="#D0CABA")
    inner += _img_box(200, 30, 70, 90)
    return _frame(inner)


def filter_bar():
    inner = ""
    for i in range(5):
        x = 10 + i * 54
        inner += f'<rect x="{x}" y="10" width="48" height="18" fill="{FILL_LIGHT}" stroke="{BORDER}" rx="2"/>'
        inner += _text_line(x + 6, 17, 30, 4)
    inner += _text_line(10, 50, 80, 6)
    return _frame(inner)


def utility_bar():
    inner = _text_line(10, 20, 100, 7)
    inner += f'<rect x="200" y="14" width="30" height="18" fill="{FILL_LIGHT}" stroke="{BORDER}" rx="2"/>'
    inner += f'<rect x="236" y="14" width="34" height="18" fill="{FILL_LIGHT}" stroke="{BORDER}" rx="2"/>'
    return _frame(inner)


def product_grid():
    inner = ""
    for r in range(2):
        for c in range(4):
            x = 10 + c * 65
            y = 10 + r * 65
            inner += _img_box(x, y, 58, 45)
            inner += _text_line(x, y + 49, 45, 5)
    return _frame(inner)


def social_proof():
    inner = ""
    for i in range(5):
        cx = 20 + i * 16
        inner += f'<circle cx="{cx}" cy="26" r="6" fill="{GOLD}"/>'
    inner += _text_line(10, 50, 200, 7)
    inner += _text_line(10, 62, 150, 6, color="#D0CABA")
    return _frame(inner)


def brand_strip(n=6):
    inner = ""
    gap = W / n
    for i in range(n):
        x = gap * i + 8
        inner += f'<rect x="{x}" y="20" width="{gap-16}" height="30" fill="{FILL_LIGHT}" stroke="{BORDER}"/>'
    return _frame(inner)


def form_block():
    inner = _text_line(10, 15, 160, 8)
    inner += f'<rect x="10" y="35" width="180" height="22" fill="{FILL_LIGHT}" stroke="{BORDER}" rx="3"/>'
    inner += _pill(196, 35, 74, 22)
    return _frame(inner)


def influencer_grid():
    inner = ""
    for r in range(2):
        for c in range(6):
            x = 8 + c * 45
            y = 10 + r * 60
            inner += f'<rect x="{x}" y="{y}" width="38" height="38" fill="{FILL_IMG}" stroke="{BORDER}"/>'
            inner += _text_line(x + 2, y + 42, 32, 5)
    return _frame(inner)


def image_copy_row():
    inner = _text_line(10, 20, 100, 8)
    inner += _text_line(10, 36, 130, 6, color="#D0CABA")
    inner += _text_line(10, 46, 110, 6, color="#D0CABA")
    inner += _img_box(180, 10, 90, 90)
    return _frame(inner)


def auction_row():
    inner = _img_box(10, 10, 70, 70)
    inner += _text_line(90, 16, 100, 7)
    inner += _text_line(90, 30, 80, 6, color="#D0CABA")
    inner += _text_line(90, 42, 90, 6, color="#D0CABA")
    inner += _pill(90, 56, 70, 16)
    return _frame(inner)


def video_block():
    inner = _img_box(50, 10, 180, 110)
    inner += f'<circle cx="140" cy="65" r="18" fill="#FFFFFF" stroke="{BORDER}"/>'
    inner += f'<polygon points="134,56 134,74 150,65" fill="{CHARCOAL}"/>'
    return _frame(inner)


def mixed_grid_banner():
    inner = product_grid_inner_partial()
    inner += _img_box(10, 110, 260, 30)
    return _frame(inner)


def product_grid_inner_partial():
    inner = ""
    for c in range(4):
        x = 10 + c * 65
        inner += _img_box(x, 10, 58, 90)
    return inner


# ---------------------------------------------------------------------------
# Type -> builder map
# ---------------------------------------------------------------------------
_BUILDERS = {
    "Hero": hero,
    "Hero Image": hero_image,
    "Banner": banner,
    "Category Icon Strip": category_icon_strip,
    "Category Tile Grid": category_tile_grid,
    "Product Carousel": product_carousel,
    "Product Carousel x3": lambda: product_carousel(n=5),
    "2-up Banner": two_up_banner,
    "2-up Promo Card": two_up_banner,
    "3-up Banner Strip": three_up_strip,
    "4-up Banner Strip": four_up_strip,
    "Spotlight Card x2": spotlight_card,
    "Circular Spotlight Carousel": circular_spotlight,
    "Image Pair Grid": image_pair_grid,
    "Nav Tabs": nav_tabs,
    "Vertical Nav Rail": vertical_nav_rail,
    "Nav Mega-Menu": mega_menu,
    "Filter Component": filter_bar,
    "Utility Bar": utility_bar,
    "Product Grid": product_grid,
    "Social Proof": social_proof,
    "Brand Strip": brand_strip,
    "Brand Carousel": lambda: brand_strip(n=5),
    "Form Block": form_block,
    "Influencer Tile Grid": influencer_grid,
    "Image + Copy Row": image_copy_row,
    "Auction Listing Row": auction_row,
    "Video Block": video_block,
    "Mixed Grid + Banner": mixed_grid_banner,
    "Personalized Carousel": product_carousel,
}


def get_wireframe(block_type: str) -> str:
    """Return an SVG wireframe string for the given block type, or a generic
    placeholder if the type isn't mapped."""
    builder = _BUILDERS.get(block_type)
    if builder is None:
        inner = _img_box(10, 10, 260, 100)
        inner += _text_line(20, 122, 140, 7)
        return _frame(inner)
    return builder()


def get_wireframe_html(block_type: str) -> str:
    """Return the wireframe wrapped in a styled container div, ready to pass
    to st.markdown(..., unsafe_allow_html=True)."""
    svg = get_wireframe(block_type)
    return (
        f'<div style="background:#FFFFFF;border:1px solid {BORDER};'
        f'border-radius:4px;padding:10px;width:100%;box-sizing:border-box;">'
        f'<div style="width:100%;">{svg}</div></div>'
    )
