from fastapi import APIRouter, Depends, HTTPException
from database import supabase
from auth import verify_token
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
async def get_dashboard_stats(user_id: str = Depends(verify_token)):
    try:
        # Get all leads
        all_leads = supabase.table("leads").select("*").execute().data

        # Get lead counts by score
        hot_response = supabase.table("leads").select("id").eq("score", "hot").execute()
        warm_response = supabase.table("leads").select("id").eq("score", "warm").execute()
        cold_response = supabase.table("leads").select("id").eq("score", "cold").execute()

        # Get lead counts by status
        pending_response = supabase.table("leads").select("id").eq("status", "pending").execute()
        active_response = supabase.table("leads").select("id").eq("status", "active").execute()
        qualified_response = supabase.table("leads").select("id").eq("status", "qualified").execute()
        sent_to_sales_response = supabase.table("leads").select("id").eq("status", "sent_to_sales").execute()

        # Calculate qualification rate (leads with car_type, duration, dates all present)
        qualified_leads = 0
        full_info_gathered_count = 0
        for lead in all_leads:
            try:
                qual = supabase.table("qualifications").select("*").eq("lead_id", lead["id"]).execute()
                if qual.data:
                    import json
                    notes = qual.data[0].get("special_notes", "{}")
                    if isinstance(notes, str):
                        try:
                            notes_obj = json.loads(notes)
                        except:
                            notes_obj = {}
                    else:
                        notes_obj = notes if notes else {}

                    car_type = notes_obj.get("car_type", "")
                    duration = notes_obj.get("duration", "")
                    dates = notes_obj.get("dates", "")

                    if car_type and duration and dates and car_type != "not specified" and duration != "not specified" and dates != "not specified":
                        full_info_gathered_count += 1
            except:
                pass

        # Get today's date for sales handoffs
        today = datetime.utcnow().date()
        sales_handoffs_today = 0
        for lead in sent_to_sales_response.data:
            try:
                lead_detail = supabase.table("leads").select("updated_at").eq("id", lead["id"]).execute()
                if lead_detail.data:
                    updated = lead_detail.data[0].get("updated_at")
                    if updated:
                        updated_date = datetime.fromisoformat(updated.replace("Z", "+00:00")).date()
                        if updated_date == today:
                            sales_handoffs_today += 1
            except:
                pass

        # Calculate average score (hot=3, warm=2, cold=1)
        score_sum = 0
        for lead in all_leads:
            if lead["score"] == "hot":
                score_sum += 3
            elif lead["score"] == "warm":
                score_sum += 2
            elif lead["score"] == "cold":
                score_sum += 1

        total_leads = len(all_leads)
        avg_score = round(score_sum / total_leads, 2) if total_leads > 0 else 0

        # Calculate reply rate (% of leads with at least one conversation message)
        conv_response = supabase.table("conversations").select("lead_id").execute()
        leads_with_messages = set(msg["lead_id"] for msg in conv_response.data)
        reply_rate = round(len(leads_with_messages) / total_leads * 100, 1) if total_leads > 0 else 0

        qualification_rate = round(full_info_gathered_count / total_leads * 100, 1) if total_leads > 0 else 0

        return {
            "qualification_rate": qualification_rate,
            "sales_handoffs_today": sales_handoffs_today,
            "avg_score": avg_score,
            "reply_rate": reply_rate,
            "full_info_gathered": round(full_info_gathered_count / total_leads * 100, 1) if total_leads > 0 else 0,
            "total_sales_handoffs": len(sent_to_sales_response.data),
            "by_score": {
                "hot": len(hot_response.data),
                "warm": len(warm_response.data),
                "cold": len(cold_response.data)
            },
            "by_status": {
                "pending": len(pending_response.data),
                "active": len(active_response.data),
                "qualified": len(qualified_response.data),
                "sent_to_sales": len(sent_to_sales_response.data)
            },
            "total": total_leads
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/stats")
async def get_analytics_stats(user_id: str = Depends(verify_token)):
    """Get analytics statistics including qualification rate, sales handoffs, avg score, etc."""
    try:
        # Get all leads
        all_leads = supabase.table("leads").select("*").execute().data
        total_leads = len(all_leads)

        # Get all qualifications
        all_quals = supabase.table("qualifications").select("*").execute().data

        # Calculate qualification rate (leads with car_type, duration, dates all present)
        full_info_gathered_count = 0
        import json
        for qual in all_quals:
            try:
                notes = qual.get("special_notes", "{}")
                if isinstance(notes, str):
                    try:
                        notes_obj = json.loads(notes)
                    except:
                        notes_obj = {}
                else:
                    notes_obj = notes if notes else {}

                car_type = notes_obj.get("car_type", "")
                duration = notes_obj.get("duration", "")
                dates = notes_obj.get("dates", "")

                if car_type and duration and dates and car_type != "not specified" and duration != "not specified" and dates != "not specified":
                    full_info_gathered_count += 1
            except:
                pass

        qualification_rate = round(full_info_gathered_count / total_leads * 100, 1) if total_leads > 0 else 0

        # Get today's sales handoffs
        sent_to_sales = supabase.table("leads").select("id, updated_at").eq("status", "sent_to_sales").execute().data
        today = datetime.utcnow().date()
        sales_handoffs_today = 0
        for lead in sent_to_sales:
            try:
                updated = lead.get("updated_at")
                if updated:
                    updated_date = datetime.fromisoformat(updated.replace("Z", "+00:00")).date()
                    if updated_date == today:
                        sales_handoffs_today += 1
            except:
                pass

        # Calculate average score (hot=3, warm=2, cold=1)
        score_sum = 0
        for lead in all_leads:
            if lead["score"] == "hot":
                score_sum += 3
            elif lead["score"] == "warm":
                score_sum += 2
            elif lead["score"] == "cold":
                score_sum += 1

        avg_score = round(score_sum / total_leads, 2) if total_leads > 0 else 0

        # Calculate reply rate (% of leads with at least one conversation message)
        conv_response = supabase.table("conversations").select("lead_id").execute()
        leads_with_messages = set(msg["lead_id"] for msg in conv_response.data)
        reply_rate = round(len(leads_with_messages) / total_leads * 100, 1) if total_leads > 0 else 0

        # Total sales handoffs
        total_sales_handoffs = len(sent_to_sales)

        return {
            "qualification_rate": qualification_rate,
            "sales_handoffs_today": sales_handoffs_today,
            "avg_score": avg_score,
            "reply_rate": reply_rate,
            "full_info_gathered": qualification_rate,
            "total_sales_handoffs": total_sales_handoffs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
