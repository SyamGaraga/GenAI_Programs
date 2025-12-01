from fastapi import FastAPI, Request, HTTPException
from typing import Dict, Any

app = FastAPI()

@app.post("/webhook/payment")
async def payment_webhook(request: Request):
    payload = await request.json()
    event_type = payload.get("event")
    
    if not event_type:
        raise HTTPException(status_code=400, detail="Missing event type")
    
    print(f"Received event: {event_type}")
    # Verify signature if provided (e.g., Stripe: check X-Signature header)
    # Process the event (e.g., update database, notify users)
    # Example: if event_type == "payment.succeeded": update_order_status(payload["data"]["id"])
    
    return {"status": "ok"}