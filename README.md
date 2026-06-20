# Al Rugaib — Digital Merchandising Block Update Tool

A simple guided form for the Virtual Merchandising team: pick **Platform → Page → Block**,
fill in the product SKU/handle and image URL, hit submit. It writes straight into the
shared `Block_Updates` tab of the Google Sheet — no Excel, no training needed.

This README assumes you've already done these two things (if not, ask Claude to
walk you through them again):
- Created the Google Sheet with a `Block_Updates` tab and the 12 header columns
- Created a Google Cloud service account, downloaded its JSON key, and shared the
  Sheet with the service account's email as **Editor**

---

## 1. Put this folder on GitHub

1. Go to [github.com/new](https://github.com/new)
2. Repo name: `alrugaib-merch-input` (or anything you like)
3. Visibility: **Private** is recommended (this is an internal tool)
4. Don't initialize with a README (we already have one) → **Create repository**
5. On your computer, in this folder, run:
   ```bash
   git init
   git add .
   git commit -m "Initial merchandising input app"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/alrugaib-merch-input.git
   git push -u origin main
   ```

   > **Important:** `.gitignore` already excludes `.streamlit/secrets.toml` and any
   > `*.json` key files, so your real credentials never get pushed. Only
   > `secrets.toml.example` (with placeholder text) goes to GitHub — that's fine,
   > it has no real secrets in it.

---

## 2. Deploy on Streamlit Community Cloud (free)

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
2. Click **Create app** → **From an existing repo**
3. Pick your `alrugaib-merch-input` repo, branch `main`, main file path `app.py`
4. **Before clicking Deploy**, click **Advanced settings** → **Secrets**, and paste
   in your real values using this exact shape (copy from your downloaded JSON key
   file and your Sheet's URL):

   ```toml
   sheet_id = "1AbCdEfGhIjKlMnOpQrStUvWxYz"

   [gcp_service_account]
   type = "service_account"
   project_id = "your-real-project-id"
   private_key_id = "abc123..."
   private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvQ...\n-----END PRIVATE KEY-----\n"
   client_email = "merchandising-sheet-writer@your-real-project-id.iam.gserviceaccount.com"
   client_id = "123456789"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/merchandising-sheet-writer%40your-real-project-id.iam.gserviceaccount.com"
   ```

   Every one of these fields is in the JSON file you downloaded in Step 2 of
   the Google Cloud setup — just match the field names (`project_id`,
   `private_key`, `client_email`, etc.) to the same names in the JSON.

   **The `private_key` field is the only fiddly one** — in the JSON it already
   contains `\n` characters, copy it exactly as-is, in quotes, on one line.

5. Click **Deploy**. First deploy takes 1-2 minutes.
6. You'll get a public-ish URL like `alrugaib-merch-input.streamlit.app` — share
   that link with Rahaf and the rest of the team. (You can restrict access to
   specific emails under the app's **Settings → Sharing** if you don't want it
   fully public.)

---

## 3. Test it

1. Open the app URL
2. Pick **Web → Home → Hero Banner**
3. Fill in a test SKU and image URL, pick a status, submit
4. Check your Google Sheet's `Block_Updates` tab — a new row should appear within
   a few seconds

If you see a permissions error, the most common cause is forgetting to **share
the Sheet** with the service account's `client_email` as Editor — go back and
check that.

---

## 4. Updating the block list later

The dropdown options come from `data/blocks_data.json`. If a new block gets
added to the site/app, or one gets removed, update that file (or ask Claude to
regenerate it from the master Excel workbook) and push the change — Streamlit
Cloud redeploys automatically on every push to `main`.

---

## What this does NOT do

- It does not edit the Excel workbook directly — the Sheet is the live working
  copy. Periodically export/sync `Block_Updates` back into the workbook's
  "Block Library" tab (copy-paste, or ask Claude to build a sync step) so the
  CRO master file and the team's day-to-day input stay aligned.
- It does not validate that an uploaded image URL is actually live/reachable —
  worth a periodic spot-check.
- It does not enforce the Max SKUs rule — it's shown as guidance text on the
  block card, but the form will accept more if someone pastes them in.
