from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from services.sheet_parser import sheet_parser
from services.n8n_client import n8n_client
from database import supabase
from auth import verify_token
from uuid import uuid4
import os

router = APIRouter(prefix="/sheets", tags=["sheets"])

@router.post("/upload")
async def upload_sheet(file: UploadFile = File(...), user_id: str = Depends(verify_token)):
    try:
        print(f"\n=== UPLOAD START ===")
        print(f"User ID: {user_id}")
        print(f"File: {file.filename}")

        # Read file content
        content = await file.read()

        # Parse file
        leads_data = sheet_parser.parse_file(file.filename, content)
        print(f"Parsed {len(leads_data)} leads from file")
        print(f"First lead: {leads_data[0] if leads_data else 'None'}")

        # Create batch record
        batch = {
            "admin_id": user_id,
            "filename": file.filename,
            "total_leads": len(leads_data),
            "processed_count": 0,
            "status": "processing"
        }

        batch_response = supabase.table("batch_uploads").insert(batch).execute()
        batch_id = batch_response.data[0]["id"] if batch_response.data else None

        # Insert leads into database
        for lead_data in leads_data:
            # Clean data - map column names if needed
            # Handle "Name" column by using it as first_name if First Name doesn't exist
            first_name = lead_data.get("First Name") or lead_data.get("first_name")
            if not first_name and lead_data.get("Name"):
                first_name = lead_data.get("Name").split()[0]  # Use first word as first_name
                last_name = " ".join(lead_data.get("Name").split()[1:]) if len(lead_data.get("Name").split()) > 1 else None
            else:
                last_name = lead_data.get("Last Name")

            lead = {
                "phone": lead_data.get("Mobile No") or lead_data.get("phone"),
                "first_name": first_name,
                "middle_name": lead_data.get("Middle Name"),
                "last_name": last_name or lead_data.get("Last Name"),
                "email": lead_data.get("Email"),
                "gender": lead_data.get("Gender"),
                "nationality": lead_data.get("Nationality"),
                "creation_date": lead_data.get("Creation Date"),
                "status": "pending",
                "score": "cold"
            }

            try:
                # Validate required fields
                if not lead.get("phone") or not lead.get("first_name"):
                    print(f"Skipping lead - missing required fields. Data: {lead}")
                    continue

                # Insert lead
                print(f"Inserting lead: {lead}")
                response = supabase.table("leads").insert(lead).execute()
                print(f"Supabase response: {response}")
                print(f"Response data: {response.data}")

                if response.data:
                    lead_id = response.data[0]["id"]
                    print(f"Successfully inserted lead {lead_id}: {lead.get('first_name')} {lead.get('last_name')}")

                    # Create qualification record
                    qual = {
                        "lead_id": lead_id,
                        "completed_criteria": 0
                    }
                    supabase.table("qualifications").insert(qual).execute()

                    # Trigger n8n workflow to send WhatsApp message
                    n8n_webhook = os.getenv("N8N_WEBHOOK_SEND_TEMPLATE")
                    if n8n_webhook:
                        try:
                            n8n_client.trigger_workflow_webhook(n8n_webhook, {
                                "lead_id": lead_id,
                                "phone": lead["phone"],
                                "first_name": lead["first_name"]
                            })
                        except Exception as e:
                            print(f"Warning: Failed to trigger n8n for lead {lead_id}: {str(e)}")
                else:
                    print(f"Insert response was empty for lead: {lead}")

            except Exception as e:
                print(f"Failed to create lead: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        # Update batch status
        supabase.table("batch_uploads").update({
            "status": "completed",
            "processed_count": len(leads_data)
        }).eq("id", batch_id).execute()

        result = {
            "message": "Sheet uploaded successfully",
            "batch_id": batch_id,
            "leads_processed": len(leads_data),
            "leads": leads_data  # Return the actual lead data so frontend can display it
        }
        print(f"=== UPLOAD SUCCESS ===")
        print(f"Result: {result}\n")
        return result

    except Exception as e:
        print(f"=== UPLOAD ERROR ===")
        print(f"Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batches")
async def get_batches(user_id: str = Depends(verify_token)):
    try:
        response = supabase.table("batch_uploads").select("*").eq("admin_id", user_id).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
