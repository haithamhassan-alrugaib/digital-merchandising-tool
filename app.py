"""
Al Rugaib Furniture — Digital Merchandising Input Tool
Guided flow (Welcome -> Platform -> Page -> Block -> Submit) that writes
submissions straight into the team's shared Google Sheet.
"""

import json
import uuid
from datetime import datetime, timezone

import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

import wireframes

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Al Rugaib — Merchandising Block Update",
    page_icon="🪑",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Brand colors — used consistently in CSS below.
# Note: .streamlit/config.toml fixes the base theme to light, so these
# colors render the same regardless of the viewer's OS/browser dark mode.
# ---------------------------------------------------------------------------
TERRACOTTA = "#C1623D"
TERRACOTTA_DARK = "#9E4D2F"
TEAL = "#1F6F6B"
TEAL_DARK = "#15504D"
CHARCOAL = "#121212"
PARCHMENT = "#FDFBF7"
LIGHT_GREY = "#F2EFE9"
MID_GREY = "#D9D4C9"
GREEN = "#2E7D32"
TEXT_SECONDARY = "#5A574E"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {PARCHMENT}; }}

    h1, h2, h3 {{ font-family: 'Playfair Display', Georgia, serif; color: {CHARCOAL} !important; }}

    /* Force readable text everywhere, regardless of viewer's system theme */
    p, span, label, .stMarkdown, .stCaption, div[data-testid="stMarkdownContainer"] {{
        color: {CHARCOAL};
    }}
    [data-testid="stCaptionContainer"], .stCaption, small {{
        color: {TEXT_SECONDARY} !important;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {LIGHT_GREY};
    }}
    section[data-testid="stSidebar"] * {{
        color: {CHARCOAL} !important;
    }}

    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"],
    .stDateInput input {{
        background-color: #FFFFFF !important;
        color: {CHARCOAL} !important;
        border: 1px solid {MID_GREY} !important;
    }}

    /* ----------------------------------------------------------------- */
    /* UNIFIED BUTTON SYSTEM                                              */
    /* Every button — primary, secondary, icon, or plain — follows the    */
    /* same hover rule: shift toward teal. Never black, never a different */
    /* pattern per button type. Three visual variants share one behavior: */
    /*   1. Default / primary -> terracotta bg, hovers to teal bg         */
    /*   2. Secondary (.secondary-btn) -> white bg, hovers to teal border/text */
    /*   3. Icon-only (small, e.g. the image remove "x") -> same as default */
    /* ----------------------------------------------------------------- */
    .stButton>button {{
        background-color: {TERRACOTTA}; color: #FFFFFF; border: 1px solid {TERRACOTTA};
        border-radius: 6px; padding: 0.6em 1.4em; font-weight: 600;
        transition: all 0.15s ease; min-height: 42px; width: 100%;
    }}
    .stButton>button:hover {{
        background-color: {TEAL} !important; border-color: {TEAL} !important;
        color: #FFFFFF !important;
    }}
    .stButton>button:active {{
        background-color: {TEAL_DARK} !important; border-color: {TEAL_DARK} !important;
    }}
    .stButton>button:focus:not(:active) {{
        background-color: {TERRACOTTA}; border-color: {TEAL};
        box-shadow: 0 0 0 2px {TEAL}33;
    }}
    .stButton>button p {{ color: inherit !important; }}

    /* Secondary (outline) buttons — same teal-on-hover rule, just inverted
       base colors so it still reads as "secondary" at rest. */
    .secondary-btn button {{
        background-color: #FFFFFF !important; color: {CHARCOAL} !important;
        border: 1px solid {MID_GREY} !important;
    }}
    .secondary-btn button:hover {{
        background-color: {TEAL} !important; color: #FFFFFF !important;
        border-color: {TEAL} !important;
    }}
    .secondary-btn button:active {{
        background-color: {TEAL_DARK} !important; border-color: {TEAL_DARK} !important;
    }}

    /* Streamlit's own primary-kind marker — keep in lockstep with the
       default rule above so type="primary" never drifts out of sync. */
    button[kind="primary"] {{
        background-color: {TERRACOTTA} !important; border-color: {TERRACOTTA} !important;
    }}
    button[kind="primary"]:hover {{
        background-color: {TEAL} !important; border-color: {TEAL} !important;
    }}
    button[kind="primary"]:active {{
        background-color: {TEAL_DARK} !important; border-color: {TEAL_DARK} !important;
    }}

    .block-card {{
        background: #FFFFFF; border: 1px solid {MID_GREY}; border-left: 4px solid {TEAL};
        border-radius: 6px; padding: 1.1em 1.3em; margin: 0.8em 0 1.2em 0; color: {CHARCOAL};
    }}
    .info-card {{
        background: {LIGHT_GREY}; border-radius: 6px; padding: 1em 1.2em;
        margin-bottom: 1em; font-size: 0.92em; color: {CHARCOAL};
        border-left: 4px solid {TERRACOTTA};
    }}
    .breadcrumb {{ font-size: 0.85em; color: {TEXT_SECONDARY}; margin-bottom: 0.3em; }}
    .breadcrumb b {{ color: {CHARCOAL}; }}

    .wireframe-label {{
        font-size: 0.78em; color: {TEXT_SECONDARY}; text-transform: uppercase;
        letter-spacing: 0.04em; margin-bottom: 6px; font-weight: 600;
    }}

    /* Progress stepper */
    .stepper {{ display: flex; align-items: center; margin: 1em 0 1.6em 0; }}
    .step-circle {{
        width: 30px; height: 30px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 0.85em; color: #FFFFFF;
        background-color: {MID_GREY}; flex-shrink: 0;
    }}
    .step-circle.active {{ background-color: {TERRACOTTA}; }}
    .step-circle.done {{ background-color: {TEAL}; }}
    .step-label {{
        font-size: 0.78em; margin-left: 0.4em; margin-right: 0.9em; color: {TEXT_SECONDARY};
        white-space: nowrap;
    }}
    .step-label.active {{ color: {CHARCOAL}; font-weight: 700; }}
    .step-line {{ flex-grow: 1; height: 2px; background-color: {MID_GREY}; margin-right: 0.9em; }}

    /* Responsive: stack side-by-side columns on narrow screens so buttons
       and fields never get squeezed/misaligned on mobile. */
    @media (max-width: 640px) {{
        div[data-testid="stHorizontalBlock"] {{
            flex-direction: column !important;
        }}
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
            width: 100% !important;
            flex: 1 1 100% !important;
            margin-bottom: 0.5rem;
        }}
        .stepper {{ flex-wrap: wrap; row-gap: 0.5rem; }}
    }}

    .warning-card {{
        background: #FBF1E6; border-left: 4px solid {TERRACOTTA};
        border-radius: 6px; padding: 0.9em 1.1em; margin: 0.6em 0 1em 0;
        font-size: 0.92em; color: {CHARCOAL};
    }}
    .required-star {{ color: {TERRACOTTA}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Load block library (the skeleton built from the CRO workbook)
# ---------------------------------------------------------------------------
@st.cache_data
def load_blocks():
    with open("data/blocks_data.json", "r", encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))

blocks_df = load_blocks()

# ---------------------------------------------------------------------------
# Google Sheets connection
# ---------------------------------------------------------------------------
SHEET_NAME_TAB = "Block_Updates"

@st.cache_resource
def get_worksheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    gc = gspread.authorize(creds)
    sheet_id = st.secrets["sheet_id"]
    sh = gc.open_by_key(sheet_id)
    return sh.worksheet(SHEET_NAME_TAB)

def submit_row(row: dict):
    """Writes one row per image URL. All rows share the same submission_id
    so the team can tell they belong to the same update. If there's more
    than one image, only the first row carries the full notes/supplier text
    to avoid clutter — every row carries the SKU list and dates either way."""
    ws = get_worksheet()
    image_urls = row["image_urls"] or [""]
    rows_to_write = []
    for i, img in enumerate(image_urls):
        rows_to_write.append(
            [
                row["submission_id"],
                row["block_id"], row["platform"], row["page"], row["block_name"],
                row["sku_handle"], img, row["update_type"],
                row["start_date"], row["end_date"], row["supplier"],
                row["notes"], row["submitted_by"], row["timestamp"], "No", "",
            ]
        )
    ws.append_rows(rows_to_write, value_input_option="USER_ENTERED")

def submit_support_row(submitted_by: str, issue_text: str):
    ws = get_worksheet()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    ws.append_row(
        [
            "",                       # submission_id — n/a
            "", "", "", "",          # block_id, platform, page, block_name — n/a
            "", "", "", "", "", "",  # sku, image, update_type, start, end, supplier — n/a
            "",                       # notes — n/a
            submitted_by, timestamp, "No",
            issue_text,               # Support Issue column
        ],
        value_input_option="USER_ENTERED",
    )

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
defaults = {
    "step": 0, "merch_name": "", "platform": None, "page": None,
    "block_id": None, "last_submit": None, "show_support": False,
    "support_submitted": False, "image_count": 1,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def go_to(step):
    st.session_state.step = step

def reset_wizard(keep_name=True):
    name = st.session_state.merch_name if keep_name else ""
    for k, v in defaults.items():
        st.session_state[k] = v
    st.session_state.merch_name = name

def sign_out():
    """Full sign-out: clears the name and returns to the welcome/name page."""
    reset_wizard(keep_name=False)

# ---------------------------------------------------------------------------
# Sidebar — always-visible instructions, present on every page
# ---------------------------------------------------------------------------
with st.sidebar:
    if st.session_state.merch_name:
        st.markdown(f"**Updating as:** {st.session_state.merch_name}")
        st.divider()

    st.markdown("### 📋 How this works")
    st.markdown(
        """
1. **Pick the platform** — Website or App
2. **Pick the page** — Home, Collection, etc.
3. **Pick the block** — see its wireframe, then pick it
4. **Fill in the product, image, and dates** the block should show
5. **Submit** — saved straight to the shared tracker

No spreadsheet, no formatting to worry about — just pick and fill.
        """
    )
    st.divider()
    st.markdown("### ⏱️ Update type")
    st.markdown(
        """
⚡ **Immediate** — goes live as soon as it's reviewed
📅 **Schedule** — goes live on a specific start date, with an optional end date
        """
    )
    st.divider()
    st.caption("Questions? Use the Contact Support button below.")

    if st.session_state.step > 0:
        st.button(
            "⟲ Start a new update",
            on_click=lambda: reset_wizard(keep_name=True),
            use_container_width=True,
        )

    if st.session_state.merch_name:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        st.button("↪ Sign out", on_click=sign_out, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    if st.button("🛟 Contact support", use_container_width=True):
        st.session_state.show_support = True
        st.session_state.support_submitted = False
        st.rerun()

# ---------------------------------------------------------------------------
# Progress stepper
# ---------------------------------------------------------------------------
STEP_NAMES = ["Platform", "Page", "Block & Details"]

def render_stepper(current):
    html = '<div class="stepper">'
    for i, name in enumerate(STEP_NAMES, start=1):
        if i < current:
            circle_class, content = "done", "✓"
        elif i == current:
            circle_class, content = "active", str(i)
        else:
            circle_class, content = "", str(i)
        label_class = "active" if i == current else ""
        html += f'<div class="step-circle {circle_class}">{content}</div>'
        html += f'<div class="step-label {label_class}">{name}</div>'
        if i < len(STEP_NAMES):
            html += '<div class="step-line"></div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Contact support — modal dialog, available from the sidebar on every step
# ---------------------------------------------------------------------------
@st.dialog("Contact support")
def support_dialog():
    if st.session_state.support_submitted:
        st.success("Thanks — your issue has been sent to the CRO team.")
        if st.button("Close", use_container_width=True):
            st.session_state.show_support = False
            st.session_state.support_submitted = False
            st.rerun()
        return

    st.caption(
        "Describe the problem or question you have. This goes straight to the "
        "CRO team's tracker — no need to message anyone separately."
    )
    issue_text = st.text_area(
        "What's the issue?",
        placeholder="e.g. The image URL field won't accept my Shopify CDN link...",
        height=140,
    )
    submitted_by = st.session_state.merch_name or "Not signed in"
    st.caption(f"Submitting as: {submitted_by}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit", use_container_width=True, type="primary"):
            if not issue_text.strip():
                st.error("Add a description before submitting.")
            else:
                try:
                    submit_support_row(submitted_by, issue_text.strip())
                    st.session_state.support_submitted = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Couldn't send this: {e}")
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.show_support = False
            st.rerun()

if st.session_state.show_support:
    support_dialog()

# ---------------------------------------------------------------------------
# STEP 0 — Welcome / Intro + name capture
# ---------------------------------------------------------------------------
if st.session_state.step == 0:
    st.title("🪑 Digital Merchandising — Block Update Tool")
    st.markdown(
        """
        <div class="info-card">
        Welcome! This tool replaces the old shared spreadsheet for updating what
        products and images show in each block on the website and app.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### What you'll do")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**1. Choose where**")
        st.caption("Pick Website or App, then the page — like Home or a Collection page.")
    with c2:
        st.markdown("**2. See the block**")
        st.caption("A small mockup shows you exactly what that block looks like.")
    with c3:
        st.markdown("**3. Fill it in**")
        st.caption("Add the product SKU and image link, mark the status, submit.")

    st.write("")
    st.markdown(
        """
        <div class="info-card">
        💡 <b>Tip:</b> Each block shows you a mini layout preview, the selection rule to
        follow (e.g. "Best Sellers" or "New Arrivals"), and the max number of products
        allowed — so you don't need to remember the merchandising playbook, it's right
        there when you need it.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.markdown("#### Before you start")
    name = st.text_input(
        "Your name",
        value=st.session_state.merch_name,
        placeholder="e.g. Rahaf Alqahtani",
        help="So updates in the tracker are saved under your name.",
    )

    st.write("")
    start_disabled = not name.strip()
    if st.button("Start an update →", use_container_width=True, type="primary", disabled=start_disabled):
        st.session_state.merch_name = name.strip()
        go_to(1)
        st.rerun()
    if start_disabled:
        st.caption("Enter your name above to continue.")

# ---------------------------------------------------------------------------
# STEP 1 — Platform
# ---------------------------------------------------------------------------
elif st.session_state.step == 1:
    render_stepper(1)
    st.subheader("Where is this block?")
    st.caption("Choose whether you're updating the website or the mobile app.")

    platforms = sorted(blocks_df["platform"].unique())
    cols = st.columns(len(platforms))
    icons = {"Web": "🖥️", "App": "📱"}
    for i, p in enumerate(platforms):
        with cols[i]:
            st.markdown(f"### {icons.get(p, '')} {p}")
            n_blocks = blocks_df.loc[blocks_df["platform"] == p, "block_id"].nunique()
            st.caption(f"{n_blocks} blocks available")
            if st.button(f"Select {p}", key=f"plat_{p}", use_container_width=True):
                st.session_state.platform = p
                go_to(2)
                st.rerun()

# ---------------------------------------------------------------------------
# STEP 2 — Page
# ---------------------------------------------------------------------------
elif st.session_state.step == 2:
    render_stepper(2)
    st.markdown(
        f'<div class="breadcrumb">Platform: <b>{st.session_state.platform}</b></div>',
        unsafe_allow_html=True,
    )
    st.subheader("Which page?")
    st.caption("Pick the page that has the block you want to update.")

    pages = sorted(
        blocks_df.loc[blocks_df["platform"] == st.session_state.platform, "page"].unique()
    )
    for p in pages:
        n_blocks = blocks_df[
            (blocks_df["platform"] == st.session_state.platform) & (blocks_df["page"] == p)
        ]["block_id"].nunique()
        col_a, col_b = st.columns([5, 1])
        with col_a:
            st.markdown(f"**{p}**")
            st.caption(f"{n_blocks} block{'s' if n_blocks != 1 else ''} on this page")
        with col_b:
            if st.button("Select", key=f"page_{p}", use_container_width=True):
                st.session_state.page = p
                go_to(3)
                st.rerun()
        st.divider()

    st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
    st.button("← Back to platform", on_click=go_to, args=(1,))
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# STEP 3 — Block + wireframe + form
# ---------------------------------------------------------------------------
elif st.session_state.step == 3:
    render_stepper(3)
    st.markdown(
        f'<div class="breadcrumb">Platform: <b>{st.session_state.platform}</b> '
        f'&nbsp;→&nbsp; Page: <b>{st.session_state.page}</b></div>',
        unsafe_allow_html=True,
    )
    st.subheader("Pick the block, then fill it in")

    subset = blocks_df[
        (blocks_df["platform"] == st.session_state.platform)
        & (blocks_df["page"] == st.session_state.page)
    ].sort_values("position")

    block_labels = {
        row["block_id"]: f"{int(row['position'])}. {row['name']}"
        for _, row in subset.iterrows()
    }
    block_id = st.selectbox(
        "Block on this page",
        options=list(block_labels.keys()),
        format_func=lambda bid: block_labels[bid],
        help="Blocks are listed in the order they appear on the page, top to bottom.",
    )
    block_row = subset[subset["block_id"] == block_id].iloc[0]

    # --- Wireframe preview ---
    st.markdown('<div class="wireframe-label">What this block looks like</div>', unsafe_allow_html=True)
    st.markdown(wireframes.get_wireframe_html(block_row["block_type"]), unsafe_allow_html=True)

    max_skus = block_row["max_skus"]
    max_skus_line = ""
    if max_skus and str(max_skus) not in ("0", "—", "None", "nan"):
        max_skus_line = f"<br>📦 <b>Max products allowed:</b> {max_skus}"

    st.markdown(
        f"""
        <div class="block-card">
        🧩 <b>Block type:</b> {block_row['block_type']}<br>
        📐 <b>Selection rule to follow:</b> {block_row['rule']}{max_skus_line}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("##### Now fill in the details")
    st.caption("Fields marked with a star are required.")

    # Update type lives OUTSIDE the form so picking it can reveal the End Date
    # field immediately. No default selection — forces an active choice rather
    # than silently defaulting to Immediate.
    update_type = st.radio(
        "Update type ⭐",
        ["⚡ Immediate", "📅 Schedule"],
        index=None,
        horizontal=True,
        help="Immediate = goes live once reviewed. Schedule = goes live on a set date range.",
        key=f"update_type_{block_id}",
    )

    if update_type is None:
        st.markdown(
            '<div class="warning-card">⚠️ Pick <b>Immediate</b> or <b>Schedule</b> above '
            'before filling in dates below — the form won\'t submit without it.</div>',
            unsafe_allow_html=True,
        )

    is_scheduled = update_type == "📅 Schedule"

    # --- Dynamic image URL inputs — live OUTSIDE the form so "Add another
    # image" can grow the list immediately without waiting for form submit.
    st.markdown("**Image URL(s) ⭐**")
    st.caption("Add one or more images. Each becomes its own row in the tracker, grouped under one submission.")

    if "block_id" not in st.session_state or st.session_state.get("_last_block_for_images") != block_id:
        st.session_state.image_count = 1
        st.session_state["_last_block_for_images"] = block_id

    image_values = []
    for i in range(st.session_state.image_count):
        col_img, col_remove = st.columns([6, 1])
        with col_img:
            val = st.text_input(
                f"Image URL {i + 1}",
                placeholder="https://cdn.shopify.com/...",
                key=f"image_url_{block_id}_{i}",
                label_visibility="collapsed" if i > 0 else "visible",
            )
            image_values.append(val)
        with col_remove:
            if st.session_state.image_count > 1:
                if st.button("✕", key=f"remove_img_{block_id}_{i}", help="Remove this image"):
                    st.session_state.image_count -= 1
                    st.rerun()

    if st.button("+ Add another image", key=f"add_img_{block_id}"):
        st.session_state.image_count += 1
        st.rerun()

    st.write("")

    with st.form("update_form", clear_on_submit=False):
        sku_handle = st.text_input(
            "Product SKU / Shopify Handle(s) ⭐",
            placeholder="e.g. confa-grey-sofa-set, agate-living-room-set  (separate multiple with commas)",
            help="The Shopify product handle — found in the product URL, after /products/. Add several separated by commas.",
        )

        st.markdown("**When should this go live? ⭐**")
        date_col1, date_col2 = st.columns(2)
        with date_col1:
            start_date = st.date_input(
                "Start date",
                value=None,
                format="DD/MM/YYYY",
                help="The day this should go live",
            )
        with date_col2:
            end_date = st.date_input(
                "End date",
                value=None,
                format="DD/MM/YYYY",
                help="The day this should come down (Schedule only)",
                disabled=not is_scheduled,
            )

        supplier = st.text_input(
            "Which supplier is requesting this update",
            placeholder="e.g. Roots Furniture",
        )
        notes = st.text_area("Notes (optional)", placeholder="Any context for the CRO team")

        submitted = st.form_submit_button("✓ Submit update", use_container_width=True, type="primary")

        if submitted:
            # Parse comma-separated SKUs into a clean list, then back to a
            # display string (trims stray whitespace around commas).
            sku_list = [s.strip() for s in sku_handle.split(",") if s.strip()]
            sku_display = ", ".join(sku_list)

            image_list = [u.strip() for u in image_values if u.strip()]

            errors = []
            if update_type is None:
                errors.append("Pick Immediate or Schedule above before submitting.")
            if not sku_list and not image_list:
                errors.append("Add at least a product SKU/handle or an image URL.")
            bad_urls = [u for u in image_list if not u.lower().startswith(("http://", "https://"))]
            if bad_urls:
                errors.append("Every image URL should start with http:// or https://")
            if start_date is None:
                errors.append("Add a start date.")
            if is_scheduled and end_date is None:
                errors.append("Schedule updates need an end date too.")
            if is_scheduled and start_date and end_date and end_date < start_date:
                errors.append("End date can't be before the start date.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                row = {
                    "submission_id": uuid.uuid4().hex[:8].upper(),
                    "block_id": block_id,
                    "platform": st.session_state.platform,
                    "page": st.session_state.page,
                    "block_name": block_row["name"],
                    "sku_handle": sku_display,
                    "image_urls": image_list,
                    "update_type": update_type.split(" ", 1)[-1],  # "Immediate" or "Schedule"
                    "start_date": start_date.strftime("%d/%m/%Y") if start_date else "",
                    "end_date": end_date.strftime("%d/%m/%Y") if (is_scheduled and end_date) else "",
                    "supplier": supplier,
                    "notes": notes,
                    "submitted_by": st.session_state.merch_name,
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                }
                try:
                    submit_row(row)
                    st.session_state.last_submit = block_row["name"]
                    st.session_state.image_count = 1
                    go_to(4)
                    st.rerun()
                except Exception as e:
                    st.error(f"Couldn't save to the sheet: {e}")

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        st.button("← Back to pages", on_click=go_to, args=(2,))
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        st.button("Start over", on_click=lambda: reset_wizard(keep_name=True))
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# STEP 4 — Confirmation
# ---------------------------------------------------------------------------
elif st.session_state.step == 4:
    st.title("✅ Saved")
    st.success(f"**{st.session_state.last_submit}** was updated in the shared tracker.")
    st.markdown(
        f"""
        <div class="info-card">
        Logged under <b>{st.session_state.merch_name}</b>. Your update is now visible to
        the CRO team in the shared Google Sheet. No further action needed — they'll
        review and it'll go live on the next publish cycle.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Update another block", use_container_width=True, type="primary"):
            st.session_state.platform = None
            st.session_state.page = None
            st.session_state.block_id = None
            go_to(1)
            st.rerun()
    with c2:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("Done for now", use_container_width=True):
            reset_wizard(keep_name=False)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
