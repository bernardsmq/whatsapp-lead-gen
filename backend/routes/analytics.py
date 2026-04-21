from fastapi import APIRouter, Depends, HTTPException
from database import supabase
from auth import verify_token
from datetime import datetime, date
from typing import Optional

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/messages/by-date")
async def get_messages_by_date(date_str: str, user_id: str = Depends(verify_token)):
    """Get all WhatsApp messages sent on a specific date with lead info"""
    try:
        # Parse the date
        target_date = datetime.fromisoformat(date_str).date()

        # Get conversations sent on this date
        all_convs = supabase.table("conversations").select("*").execute().data

        messages_with_leads = []
        for conv in all_convs:
            try:
                created_at = conv.get("created_at")
                if created_at:
                    msg_date = datetime.fromisoformat(created_at.replace("Z", "+00:00")).date()
                    if msg_date == target_date:
                        # Get lead info
                        lead_id = conv.get("lead_id")
                        lead = supabase.table("leads").select("*").eq("id", lead_id).execute()
                        if lead.data:
                            lead_info = lead.data[0]
                            messages_with_leads.append({
                                "id": conv.get("id"),
                                "lead_id": lead_id,
                                "lead_name": f"{lead_info.get('first_name', '')} {lead_info.get('last_name', '')}".strip(),
                                "lead_phone": lead_info.get("phone"),
                                "message": conv.get("content"),
                                "sender": conv.get("sender"),  # "user" or "ai"
                                "created_at": conv.get("created_at"),
                                "delivery_status": "delivered"  # Default status
                            })
            except:
                pass

        # Sort by timestamp
        messages_with_leads.sort(key=lambda x: x["created_at"], reverse=True)

        return messages_with_leads
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activity/recent")
async def get_recent_activity(limit: int = 20, user_id: str = Depends(verify_token)):
    """Get recent activity (new lead added, lead scored, sent to sales, messages)"""
    try:
        activities = []

        # Get recent leads
        recent_leads = supabase.table("leads").select("*").order("created_at", desc=True).limit(limit).execute().data
        for lead in recent_leads:
            activities.append({
                "type": "lead_added",
                "icon": "📝",
                "title": f"New lead added",
                "description": f"{lead.get('first_name', '')} {lead.get('last_name', '')}",
                "timestamp": lead.get("created_at"),
                "lead_id": lead.get("id")
            })

        # Get leads sent to sales
        sent_to_sales = supabase.table("leads").select("*").eq("status", "sent_to_sales").order("updated_at", desc=True).limit(limit).execute().data
        for lead in sent_to_sales:
            activities.append({
                "type": "sent_to_sales",
                "icon": "🎯",
                "title": "Lead sent to sales",
                "description": f"{lead.get('first_name', '')} {lead.get('last_name', '')} - {lead.get('score', 'unknown')} lead",
                "timestamp": lead.get("updated_at"),
                "lead_id": lead.get("id")
            })

        # Get recent messages
        recent_convs = supabase.table("conversations").select("*").order("created_at", desc=True).limit(limit).execute().data
        for conv in recent_convs:
            if conv.get("sender") == "ai":  # Only show AI messages sent
                lead_id = conv.get("lead_id")
                lead = supabase.table("leads").select("*").eq("id", lead_id).execute()
                if lead.data:
                    lead_info = lead.data[0]
                    message_preview = conv.get("content", "")[:50]
                    activities.append({
                        "type": "message_sent",
                        "icon": "💬",
                        "title": "Message sent",
                        "description": f"To {lead_info.get('first_name', '')}: {message_preview}...",
                        "timestamp": conv.get("created_at"),
                        "lead_id": lead_id
                    })

        # Get leads with new scores
        qualified_leads = supabase.table("leads").select("*").eq("status", "qualified").order("updated_at", desc=True).limit(limit).execute().data
        for lead in qualified_leads:
            activities.append({
                "type": "lead_scored",
                "icon": "⭐",
                "title": f"Lead scored as {lead.get('score', 'unknown')}",
                "description": f"{lead.get('first_name', '')} {lead.get('last_name', '')}",
                "timestamp": lead.get("updated_at"),
                "lead_id": lead.get("id")
            })

        # Sort by timestamp (most recent first)
        activities.sort(key=lambda x: x["timestamp"] if x["timestamp"] else "", reverse=True)

        # Return unique activities, limit to requested count
        seen = set()
        unique_activities = []
        for activity in activities:
            key = (activity["type"], activity["lead_id"], activity["timestamp"])
            if key not in seen:
                seen.add(key)
                unique_activities.append(activity)
            if len(unique_activities) >= limit:
                break

        return unique_activities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
