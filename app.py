"""
Al Rugaib Furniture — Digital Merchandising Input Tool
Guided 3-step form (Platform -> Page -> Block) that writes submissions
straight into the team's shared Google Sheet.
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
)

GOLD = "#D4AF37"
CHARCOAL = "#121212"
PARCHMENT = "#FDFBF7"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {PARCHMENT}; }}
    h1, h2, h3 {{ font-family: 'Playfair Display', serif; color: {CHARCOAL}; }}
    .stButton>button {{
        background-color: {GOLD}; color: white; border: none;
        border-radius: 0px; padding: 0.6em 1.4em; font-weight: 600;
    }}
    .stButton>button:hover {{ background-color: {CHARCOAL}; color: {GOLD}; }}
    .block-card {{
        background: white; border: 1px solid #D9D4C9; border-radius: 0px;
        padding: 1.2em; margin-bottom: 1em;
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
# Header
# ---------------------------------------------------------------------------
st.title("Digital Merchandising — Block Update")
st.caption(
    "Update what's showing in a website or app block. Pick the page, pick the "
    "block, fill in the product and image, submit. It lands straight in the "
    "shared tracker — no spreadsheet needed."
)
st.divider()

# ---------------------------------------------------------------------------
# Session state for the wizard
# ---------------------------------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1
if "platform" not in st.session_state:
    st.session_state.platform = None
if "page" not in st.session_state:
    st.session_state.page = None
if "block_id" not in st.session_state:
    st.session_state.block_id = None

def reset_wizard():
    for k in ("step", "platform", "page", "block_id"):
        st.session_state[k] = None
    st.session_state.step = 1

# ---------------------------------------------------------------------------
# STEP 1 — Platform
# ---------------------------------------------------------------------------
if st.session_state.step == 1:
    st.subheader("Step 1 of 3 — Where is this block?")
    platforms = sorted(blocks_df["platform"].unique())
    cols = st.columns(len(platforms))
    for i, p in enumerate(platforms):
        with cols[i]:
            if st.button(f"📱 {p}" if p == "App" else f"🖥️ {p}", use_container_width=True, key=f"plat_{p}"):
                st.session_state.platform = p
                st.session_state.step = 2
                st.rerun()

# ---------------------------------------------------------------------------
# STEP 2 — Page
# ---------------------------------------------------------------------------
elif st.session_state.step == 2:
    st.subheader("Step 2 of 3 — Which page?")
    st.caption(f"Platform: **{st.session_state.platform}**")

    pages = sorted(
        blocks_df.loc[blocks_df["platform"] == st.session_state.platform, "page"].unique()
    )
    for p in pages:
        if st.button(p, use_container_width=True, key=f"page_{p}"):
            st.session_state.page = p
            st.session_state.step = 3
            st.rerun()

    st.button("← Back", on_click=lambda: st.session_state.update(step=1))

# ---------------------------------------------------------------------------
# STEP 3 — Block + form
# ---------------------------------------------------------------------------
elif st.session_state.step == 3:
    st.subheader("Step 3 of 3 — Which block, and what's going in it?")
    st.caption(f"Platform: **{st.session_state.platform}**  |  Page: **{st.session_state.page}**")

    subset = blocks_df[
        (blocks_df["platform"] == st.session_state.platform)
        & (blocks_df["page"] == st.session_state.page)
    ].sort_values("position")

    block_labels = {
        row.block_id: f"{int(row.position)}. {row['name']}"
        for row in subset.itertuples()
    }
    block_id = st.selectbox(
        "Block",
        options=list(block_labels.keys()),
        format_func=lambda bid: block_labels[bid],
    )
    block_row = subset[subset["block_id"] == block_id].iloc[0]

    with st.container():
        st.markdown('<div class="block-card">', unsafe_allow_html=True)
        st.markdown(f"**Block type:** {block_row['block_type']}")
        st.markdown(f"**Selection rule to follow:** {block_row['rule']}")
        max_skus = block_row["max_skus"]
        if max_skus and str(max_skus) not in ("0", "—", "None", "nan"):
            st.markdown(f"**Max products allowed in this block:** {max_skus}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    with st.form("update_form", clear_on_submit=False):
        sku_handle = st.text_input(
            "Product SKU / Shopify Handle(s)",
            placeholder="e.g. confa-grey-sofa-set  (separate multiple with commas)",
        )
        image_url = st.text_input(
            "Image URL",
            placeholder="https://cdn.shopify.com/...",
        )
        status = st.selectbox(
            "Status",
            ["🟢 Live & Current", "🟡 Needs Refresh", "🔴 Outdated / Broken", "⚪ Planned"],
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

        submitted = st.form_submit_button("Submit update", use_container_width=True)

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
                    st.success(f"Saved — {block_row['name']} updated in the tracker. ✅")
                    st.balloons()
                except Exception as e:
                    st.error(f"Couldn't save to the sheet: {e}")

    col1, col2 = st.columns(2)
    with col1:
        st.button("← Back to pages", on_click=lambda: st.session_state.update(step=2))
    with col2:
        st.button("Start over", on_click=reset_wizard)
