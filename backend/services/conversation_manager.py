"""
Conversation Manager: Handles conversation state, context, and field tracking
"""
import json
from datetime import datetime
from typing import Optional, Dict, List, Tuple


class ConversationManager:
    """Manages conversation state per lead to track context and avoid repeated questions"""

    def __init__(self, lead_id: str, supabase_client):
        """Initialize manager for a specific lead"""
        self.lead_id = lead_id
        self.db = supabase_client
        self.state = self._load_state()
        self.history = self._load_history()

    def _load_state(self) -> Dict:
        """Load conversation_state from database, or create empty state if not found"""
        try:
            response = self.db.table("conversation_state").select("*").eq("lead_id", self.lead_id).execute()
            if response.data and len(response.data) > 0:
                state = response.data[0]
                # Parse JSON fields
                if isinstance(state.get("asked_fields"), str):
                    state["asked_fields"] = json.loads(state["asked_fields"])
                return state
        except Exception as e:
            print(f"⚠️ Error loading conversation state: {e}")

        # Return empty state if not found
        return {
            "lead_id": self.lead_id,
            "vehicle_type": None,
            "vehicle_model": None,
            "rental_start_date": None,
            "rental_duration": None,
            "budget": None,
            "asked_fields": {},
            "last_asked_field": None,
            "last_asked_at": None,
            "budget_numeric": None,
            "budget_period": None,
            "user_confirmed": False,
            "confirmed_at": None,
        }

    def _load_history(self) -> List[Dict]:
        """Load recent conversation history (last 30 messages) for context"""
        try:
            response = self.db.table("conversations").select("content,sender,created_at").eq("lead_id", self.lead_id).order("created_at", desc=False).limit(30).execute()
            return response.data or []
        except Exception as e:
            print(f"⚠️ Error loading conversation history: {e}")
            return []

    def get_conversation_history_text(self) -> str:
        """Format conversation history as text for GPT context"""
        lines = []
        for msg in self.history:
            sender = "Lead" if msg["sender"] == "user" else "Bot"
            lines.append(f"{sender}: {msg['content']}")
        return "\n".join(lines)

    def get_missing_fields(self) -> List[str]:
        """
        Returns list of missing fields in priority order.
        Priority: vehicle_model > rental_start_date > rental_duration > budget
        """
        missing = []
        if not self.state.get("vehicle_model"):
            missing.append("vehicle_model")
        if not self.state.get("rental_start_date"):
            missing.append("rental_start_date")
        if not self.state.get("rental_duration"):
            missing.append("rental_duration")
        if not self.state.get("budget"):
            missing.append("budget")
        return missing

    def has_field_been_asked(self, field_name: str) -> Tuple[bool, int]:
        """
        Check if a field has been asked and how many times.
        Returns: (has_been_asked, count)
        """
        asked_count = self.state.get("asked_fields", {}).get(field_name, 0)
        return asked_count > 0, asked_count

    def mark_field_asked(self, field_name: str) -> None:
        """Record that we asked for this field (increments counter)"""
        asked_fields = self.state.get("asked_fields", {})
        asked_fields[field_name] = asked_fields.get(field_name, 0) + 1
        self.state["asked_fields"] = asked_fields
        self.state["last_asked_field"] = field_name
        self.state["last_asked_at"] = datetime.utcnow().isoformat()
        self._save_state()

    def should_ask_field(self, field_name: str, max_asks: int = 2) -> bool:
        """
        Decide if we should ask for this field.
        Returns False if already asked max_asks times.
        """
        _, ask_count = self.has_field_been_asked(field_name)
        return ask_count < max_asks

    def update_field(self, field_name: str, value: str, normalize: bool = True) -> None:
        """
        Extract and store a field value.
        If normalize=True, will also extract numeric values for numeric fields.
        """
        if not value or value.lower() == "not mentioned":
            return

        self.state[field_name] = value

        # Normalize budget if this is a budget field
        if field_name == "budget":
            numeric, period = self._parse_budget(value)
            self.state["budget_numeric"] = numeric
            self.state["budget_period"] = period

        self.state["updated_at"] = datetime.utcnow().isoformat()
        self._save_state()

    def _parse_budget(self, budget_text: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Extract numeric budget and period from text.
        Examples:
        - "$100/day" → (100.0, "day")
        - "AED 500" → (500.0, None)
        - "2000 per month" → (2000.0, "month")
        - "600" → (600.0, None)
        """
        import re

        # Try to find number
        numbers = re.findall(r"\d+(?:\.\d+)?", budget_text.lower())
        if not numbers:
            return None, None

        numeric = float(numbers[0])

        # Try to find period
        period = None
        if "day" in budget_text.lower():
            period = "day"
        elif "week" in budget_text.lower():
            period = "week"
        elif "month" in budget_text.lower():
            period = "month"

        return numeric, period

    def mark_confirmed(self) -> None:
        """Record that user confirmed details"""
        self.state["user_confirmed"] = True
        self.state["confirmed_at"] = datetime.utcnow().isoformat()
        self._save_state()

    def is_ready_for_sales(self) -> bool:
        """
        Check if lead is ready to forward to sales.
        Requires: vehicle_model + rental_start_date + rental_duration (budget optional)
        """
        has_model = bool(self.state.get("vehicle_model"))
        has_start = bool(self.state.get("rental_start_date"))
        has_duration = bool(self.state.get("rental_duration"))
        return has_model and has_start and has_duration

    def is_confirmed(self) -> bool:
        """Check if user has explicitly confirmed"""
        return self.state.get("user_confirmed", False)

    def get_summary(self) -> Dict:
        """Get summary of collected details for display or passing to sales"""
        return {
            "vehicle_type": self.state.get("vehicle_type"),
            "vehicle_model": self.state.get("vehicle_model"),
            "rental_start_date": self.state.get("rental_start_date"),
            "rental_duration": self.state.get("rental_duration"),
            "budget": self.state.get("budget"),
            "confirmed": self.state.get("user_confirmed", False),
        }

    def _save_state(self) -> None:
        """Save state to database"""
        try:
            # Convert asked_fields to JSON string if dict
            state_to_save = self.state.copy()
            if isinstance(state_to_save.get("asked_fields"), dict):
                state_to_save["asked_fields"] = json.dumps(state_to_save["asked_fields"])

            # Upsert (insert or update)
            self.db.table("conversation_state").upsert(state_to_save).execute()
        except Exception as e:
            print(f"⚠️ Error saving conversation state: {e}")

    def clear(self) -> None:
        """Clear all state (for fresh inquiry)"""
        self.state = {
            "lead_id": self.lead_id,
            "vehicle_type": None,
            "vehicle_model": None,
            "rental_start_date": None,
            "rental_duration": None,
            "budget": None,
            "asked_fields": {},
            "last_asked_field": None,
            "last_asked_at": None,
            "budget_numeric": None,
            "budget_period": None,
            "user_confirmed": False,
            "confirmed_at": None,
        }
        self._save_state()
