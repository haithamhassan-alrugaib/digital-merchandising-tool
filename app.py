"""
Al Rugaib Furniture — Digital Merchandising Input Tool
Guided flow (Welcome -> Platform -> Page -> Block -> Submit) that writes
submissions straight into the team's shared Google Sheet.
"""

import json
from datetime import datetime, timezone

import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ---------------------------------------------------------------------------
# Page config + brand styling
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Al Rugaib — Merchandising Block Update",
    page_icon="🪑",
    layout="centered",
    initial_sidebar_state="expanded",
)

GOLD = "#D4AF37"
CHARCOAL = "#121212"
PARCHMENT = "#FDFBF7"
LIGHT_GREY = "#F2EFE9"
MID_GREY = "#D9D4C9"
GREEN = "#2E7D32"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {PARCHMENT}; }}
    h1, h2, h3 {{ font-family: 'Playfair Display', Georgia, serif; color: {CHARCOAL}; }}
    p, label, .stMarkdown {{ font-family: 'Manrope', sans-serif; }}

    .stButton>button {{
        background-color: {GOLD}; color: white; border: none;
        border-radius: 4px; padding: 0.6em 1.4em; font-weight: 600;
        transition: all 0.15s ease;
    }}
    .stButton>button:hover {{ background-color: {CHARCOAL}; color: {GOLD}; }}

    .secondary-btn button {{
        background-color: transparent !important; color: {CHARCOAL} !important;
        border: 1px solid {MID_GREY} !important;
    }}
    .secondary-btn button:hover {{
        background-color: {LIGHT_GREY} !important; color: {CHARCOAL} !important;
    }}

    .block-card {{
        background: white; border: 1px solid {MID_GREY}; border-left: 4px solid {GOLD};
        border-radius: 4px; padding: 1.1em 1.3em; margin: 0.8em 0 1.2em 0;
    }}
    .info-card {{
        background: {LIGHT_GREY}; border-radius: 4px; padding: 1em 1.2em;
        margin-bottom: 1em; font-size: 0.92em;
    }}
    .breadcrumb {{
        font-size: 0.85em; color: #6B6B6B; margin-bottom: 0.3em;
    }}
    .breadcrumb b {{ color: {CHARCOAL}; }}

    /* Progress stepper */
    .stepper {{ display: flex; align-items: center; margin: 1em 0 1.6em 0; }}
    .step-circle {{
        width: 30px; height: 30px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 0.85em; color: white;
        background-color: {MID_GREY}; flex-shrink: 0;
    }}
    .step-circle.active {{ background-color: {GOLD}; }}
    .step-circle.done {{ background-color: {GREEN}; }}
    .step-label {{
        font-size: 0.78em; margin-left: 0.4em; margin-right: 0.9em; color: #6B6B6B;
        white-space: nowrap;
    }}
    .step-label.active {{ color: {CHARCOAL}; font-weight: 700; }}
    .step-line {{
        flex-grow: 1; height: 2px; background-color: {MID_GREY}; margin-right: 0.9em;
    }}
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
    ws = get_worksheet()
    ws.append_row(
        [
            row["block_id"], row["platform"], row["page"], row["block_name"],
            row["sku_handle"], row["image_url"], row["status"], row["owner"],
            row["notes"], row["submitted_by"], row["timestamp"], "No",
        ],
        value_input_option="USER_ENTERED",
    )

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
defaults = {"step": 0, "platform": None, "page": None, "block_id": None, "last_submit": None}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def go_to(step):
    st.session_state.step = step

def reset_wizard():
    for k, v in defaults.items():
        st.session_state[k] = v

# ---------------------------------------------------------------------------
# Sidebar — always-visible instructions, present on every page
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📋 How this works")
    st.markdown(
        """
1. **Pick the platform** — Website or App
2. **Pick the page** — Home, Collection, etc.
3. **Pick the block** — the exact section on that page
4. **Fill in the product + image** the block should show
5. **Submit** — it's saved straight to the shared tracker

No spreadsheet, no formatting to worry about — just pick and fill.
        """
    )
    st.divider()
    st.markdown("### 🎨 Status meanings")
    st.markdown(
        """
🟢 **Live & Current** — published, looks right
🟡 **Needs Refresh** — live but getting stale
🔴 **Outdated / Broken** — wrong product or broken link, fix ASAP
⚪ **Planned** — approved, not live yet
        """
    )
    st.divider()
    st.caption("Questions? Ping the CRO team on the shared channel.")
    if st.session_state.step > 0:
        st.button("⟲ Start a new update", on_click=reset_wizard, use_container_width=True)

# ---------------------------------------------------------------------------
# Progress stepper (shown on steps 1-3, not on welcome/done screens)
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
# STEP 0 — Welcome / Intro
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
        st.markdown("**2. Choose the block**")
        st.caption("Pick the exact section, like 'Hero Banner' or 'Best Sellers Carousel'.")
    with c3:
        st.markdown("**3. Fill it in**")
        st.caption("Add the product SKU and image link, mark the status, submit.")

    st.write("")
    st.markdown(
        """
        <div class="info-card">
        💡 <b>Tip:</b> Each block shows you the selection rule to follow (e.g. "Best Sellers" or
        "New Arrivals") and the max number of products allowed — so you don't need to
        remember the merchandising playbook, it's right there when you need it.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    if st.button("Start an update →", use_container_width=True, type="primary"):
        go_to(1)
        st.rerun()

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
# STEP 3 — Block + form
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
    with st.form("update_form", clear_on_submit=False):
        sku_handle = st.text_input(
            "Product SKU / Shopify Handle(s)",
            placeholder="e.g. confa-grey-sofa-set  (separate multiple with commas)",
            help="The Shopify product handle — found in the product URL, after /products/",
        )
        image_url = st.text_input(
            "Image URL",
            placeholder="https://cdn.shopify.com/...",
            help="Paste a direct link to the image — right-click the image and 'Copy image address'",
        )
        status = st.selectbox(
            "Status",
            ["🟢 Live & Current", "🟡 Needs Refresh", "🔴 Outdated / Broken", "⚪ Planned"],
            help="See the sidebar for what each status means",
        )
        owner = st.selectbox(
            "Your name",
            [
                "Rahaf Alqahtani", "Norah Albuolayan", "Abeer Aldkheel",
                "Dina Bokhamseen", "Aisha Khubrany", "Shahad Almuqayrin",
                "Shahad Alojaimi", "Zaha Albaadi", "Other (add in notes)",
            ],
        )
        notes = st.text_area("Notes (optional)", placeholder="Any context for the CRO team")

        submitted = st.form_submit_button("✓ Submit update", use_container_width=True, type="primary")

        if submitted:
            if not sku_handle and not image_url:
                st.error("Add at least a product SKU/handle or an image URL before submitting.")
            else:
                row = {
                    "block_id": block_id,
                    "platform": st.session_state.platform,
                    "page": st.session_state.page,
                    "block_name": block_row["name"],
                    "sku_handle": sku_handle,
                    "image_url": image_url,
                    "status": status,
                    "owner": owner,
                    "notes": notes,
                    "submitted_by": owner,
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                }
                try:
                    submit_row(row)
                    st.session_state.last_submit = block_row["name"]
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
        st.button("Start over", on_click=reset_wizard)
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# STEP 4 — Confirmation
# ---------------------------------------------------------------------------
elif st.session_state.step == 4:
    st.title("✅ Saved")
    st.success(f"**{st.session_state.last_submit}** was updated in the shared tracker.")
    st.markdown(
        """
        <div class="info-card">
        Your update is now visible to the CRO team in the shared Google Sheet.
        No further action needed — they'll review and it'll go live on the next
        publish cycle.
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
            reset_wizard()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
