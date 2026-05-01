from fastapi import APIRouter
from database import supabase
from services.twilio_whatsapp_service import twilio_whatsapp_service
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/auto-send", tags=["auto-send"])

@router.post("/check-timeout")
async def check_timeout_leads():
    """Check for leads waiting for details that haven't responded in 2-3 minutes"""
    try:
        print("\n=== CHECKING FOR TIMEOUT LEADS ===")

        # Find leads that are qualified (asked for details, waiting for response)
        leads_response = supabase.table("leads").select("*").eq("status", "qualified").execute()

        if not leads_response.data:
            print("No leads qualified (waiting for response)")
            return {"checked": 0, "sent": 0}

        sent_count = 0
        now = datetime.utcnow()
        timeout_minutes = 2  # Send after 2 minutes of no response

        for lead in leads_response.data:
            # Skip leads already sent to sales
            if lead.get("status") == "sent_to_sales":
                continue

            lead_id = lead["id"]
            first_name = lead.get("first_name", "Lead")
            phone = lead.get("phone")

            # Get last conversation message timestamp
            conv_response = supabase.table("conversations").select("created_at").eq("lead_id", lead_id).order("created_at", desc=True).limit(1).execute()

            if not conv_response.data:
                continue

            last_message_time = conv_response.data[0].get("created_at")
            if not last_message_time:
                continue

            # Parse timestamp
            last_time = datetime.fromisoformat(last_message_time.replace('Z', '+00:00')).replace(tzinfo=None)
            time_diff = now - last_time

            print(f"Lead {first_name}: {time_diff.total_seconds()} seconds since last message")

            # If more than timeout_minutes have passed, send to sales guy
            if time_diff > timedelta(minutes=timeout_minutes):
                print(f"Timeout! Sending {first_name} to sales guy")

                # Get their qualification data
                qual_response = supabase.table("qualifications").select("special_notes").eq("lead_id", lead_id).execute()
                car_type = "not specified"
                duration = "not specified"
                dates = "not specified"

                if qual_response.data and qual_response.data[0].get("special_notes"):
                    import json
                    try:
                        notes = json.loads(qual_response.data[0]["special_notes"])
                        car_type = notes.get("car_type", "not specified")
                        duration = notes.get("duration", "not specified")
                        dates = notes.get("dates", "not specified")
                        # Treat "not mentioned" same as "not specified"
                        if duration == "not mentioned":
                            duration = "not specified"
                        if dates == "not mentioned":
                            dates = "not specified"
                    except:
                        pass

                score = lead.get("score", "cold")

                # Send to sales guy
                sales_phone = os.getenv("SALES_GUY_PHONE", "+971585702655")
                sales_msg = f"🎉 NEW LEAD (Auto-sent - {score})\n\nName: {first_name}\nPhone: {phone}\nCar: {car_type}\nDuration: {duration}\nDates: {dates}"

                twilio_whatsapp_service.send_text_message(sales_phone, sales_msg)

                # Mark as sent (with error handling since message already sent)
                try:
                    supabase.table("leads").update({"status": "sent_to_sales"}).eq("id", lead_id).execute()
                except Exception as e:
                    print(f"⚠️ Warning: Could not update status, but message was sent: {e}")

                # Notify customer
                try:
                    twilio_whatsapp_service.send_text_message(phone, "Thanks! I've sent your info to our sales team. They'll be in touch shortly.")
                except Exception as e:
                    print(f"⚠️ Warning: Could not notify customer: {e}")

                sent_count += 1

        print(f"=== AUTO-SEND COMPLETE: {sent_count} leads sent ===\n")
        return {"checked": len(leads_response.data), "sent": sent_count}

    except Exception as e:
        print(f"✗ Auto-send error: {str(e)}")
        return {"error": str(e)}
