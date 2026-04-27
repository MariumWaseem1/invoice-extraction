import os
import base64
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import anthropic

app = FastAPI(title="CloseAI Invoice Extraction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

EXTRACTION_PROMPT = """You are a finance AI. Analyse this invoice and return ONLY valid JSON, no markdown.
{
  "vendor_name": string,
  "invoice_number": string or null,
  "invoice_date": "YYYY-MM-DD" or null,
  "due_date": "YYYY-MM-DD" or null,
  "total_amount": number,
  "currency": "GBP/USD/EUR",
  "category": "one of: SaaS, Professional Services, Utilities, Travel & Expenses, Marketing, HR & Recruitment, Other",
  "line_items": [{"description": string, "amount": number}],
  "payment_terms": string or null,
  "anomalies": ["from: duplicate_risk, round_number_risk, missing_fields, no_due_date, high_value"],
  "anomaly_details": string or null,
  "confidence": "high/medium/low"
}
Flag total > 10000 as high_value. Flag perfectly round amounts as round_number_risk. Flag missing invoice_number or date as missing_fields."""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/process-invoice")
async def process_invoice(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename or ""
    content_type = file.content_type or ""

    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    b64_data = base64.standard_b64encode(content).decode("utf-8")

    if filename.lower().endswith(".pdf") or content_type == "application/pdf":
        media_type = "application/pdf"
        source_type = "document"
    elif filename.lower().endswith(".png") or content_type == "image/png":
        media_type = "image/png"
        source_type = "image"
    elif filename.lower().endswith((".jpg", ".jpeg")) or content_type in ("image/jpeg", "image/jpg"):
        media_type = "image/jpeg"
        source_type = "image"
    elif filename.lower().endswith(".webp") or content_type == "image/webp":
        media_type = "image/webp"
        source_type = "image"
    else:
        media_type = "image/jpeg"
        source_type = "image"

    if source_type == "document":
        content_block = {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": b64_data,
            },
        }
    else:
        content_block = {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": b64_data,
            },
        }

    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        content_block,
                        {"type": "text", "text": EXTRACTION_PROMPT},
                    ],
                }
            ],
        )
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"Anthropic API error: {str(e)}")

    raw_text = message.content[0].text.strip()

    # Strip markdown code fences if the model wraps the response
    if raw_text.startswith("```"):
        lines = raw_text.splitlines()
        lines = [l for l in lines if not l.startswith("```")]
        raw_text = "\n".join(lines).strip()

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail=f"Invalid JSON from model: {raw_text[:200]}")

    result["filename"] = filename
    return result
