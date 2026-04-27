# CloseAI — Invoice Intelligence

AI-powered invoice extraction and spend analytics. Upload PDF/image invoices, get structured data, anomaly detection, and a month-end finance report — all in seconds.

---

## Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Backend  | Python + FastAPI + Anthropic SDK    |
| AI Model | `claude-opus-4-5`                   |
| Frontend | Vanilla HTML/JS (single file)       |
| Deploy   | Render.com (backend) + Netlify (frontend) |

---

## Local Development

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Start the backend

```bash
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`. Test it:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### 4. Open the frontend

Open `frontend/index.html` directly in your browser (double-click or `open frontend/index.html`).

The frontend auto-detects localhost and points to `http://localhost:8000`.

---

## Production Deploy

### Step 1 — Push to GitHub

```bash
git add .
git commit -m "Initial CloseAI build"
git push
```

### Step 2 — Deploy Backend on Render.com (free tier)

1. Go to [render.com](https://render.com) → **New → Web Service**
2. Connect your GitHub repository
3. Render will auto-detect `render.yaml` and pre-fill settings
4. Under **Environment Variables**, add:
   - `ANTHROPIC_API_KEY` → your key (starts with `sk-ant-`)
5. Click **Deploy**

Wait ~2 minutes for the first deploy. Your backend URL will be:
```
https://closeai-backend.onrender.com
```
(or similar — copy the exact URL from the Render dashboard)

### Step 3 — Update Frontend with Your Backend URL

Open `frontend/index.html` and find this line near the top of the `<script>` block:

```js
const BACKEND_URL = (
  window.BACKEND_URL ||
  (window.location.hostname === 'localhost' ...
    ? 'http://localhost:8000'
    : 'https://closeai-backend.onrender.com')   // <-- update this
);
```

Replace `https://closeai-backend.onrender.com` with your actual Render URL.

### Step 4 — Deploy Frontend on Netlify

1. Go to [netlify.com/drop](https://app.netlify.com/drop)
2. Drag the entire `frontend/` folder onto the page
3. Netlify gives you a public URL instantly (e.g. `https://closeai-abc123.netlify.app`)
4. Share that URL with your team

---

## Features

- **Drag-and-drop upload** — PDF, PNG, JPG, WebP; multiple files at once
- **Period selector** — tag invoices to a financial period
- **Dashboard** — Total Spend, Anomaly count, High Value count, Category count
- **Anomaly detection** — flags `high_value`, `round_number_risk`, `missing_fields`, `no_due_date`, `duplicate_risk`
- **Invoice ledger** — sortable table with vendor, invoice #, date, amount, category, confidence
- **Spend by category** — animated progress bars per spend type
- **AI month-end report** — generated client-side from extracted data
- **Export CSV** — full invoice data as CSV
- **Download Report** — plain-text finance report

---

## API Reference

### `POST /api/process-invoice`

Upload a single invoice file.

```
Content-Type: multipart/form-data
Body: file=<invoice file>
```

**Response:**
```json
{
  "vendor_name": "Acme Corp",
  "invoice_number": "INV-2025-001",
  "invoice_date": "2025-04-01",
  "due_date": "2025-04-30",
  "total_amount": 4500.00,
  "currency": "GBP",
  "category": "SaaS",
  "line_items": [{"description": "Subscription Q2", "amount": 4500.00}],
  "payment_terms": "Net 30",
  "anomalies": [],
  "anomaly_details": null,
  "confidence": "high",
  "filename": "invoice.pdf"
}
```

### `GET /health`

```json
{"status": "ok"}
```

---

## Environment Variables

| Variable           | Required | Description              |
|--------------------|----------|--------------------------|
| `ANTHROPIC_API_KEY`| Yes      | Your Anthropic API key   |
| `PORT`             | Auto     | Set by Render automatically |
