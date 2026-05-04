"""
Response Generator: Generates intelligent, contextual responses based on conversation state
"""
from typing import Optional, Dict
from services.conversation_manager import ConversationManager
from services.openai_service import openai_service


class ResponseGenerator:
    """Generate contextual, intelligent responses based on message and state"""

    # Car brands inventory
    CAR_BRANDS = {
        "geely": "Geely Emgrand",
        "kia": "Kia",
        "mitsubishi": "Mitsubishi",
        "hyundai": "Hyundai",
        "tesla": "Tesla",
        "bmw": "BMW",
        "mercedes": "Mercedes",
        "audi": "Audi",
        "range rover": "Range Rover",
        "maserati": "Maserati",
        "bentley": "Bentley",
        "rolls royce": "Rolls Royce",
        "lamborghini": "Lamborghini",
        "ferrari": "Ferrari",
        "porsche": "Porsche",
        "mg": "MG",
        "jetour": "Jetour",
    }

    # Car types/categories
    CAR_TYPES = ["economy", "budget", "cheap", "affordable", "luxury", "premium", "sport", "sports", "performance", "suv", "4x4", "jeep", "offroad", "adventure", "family", "spacious", "comfort", "7 seater", "daily"]

    # Pricing info (static)
    PRICING_INFO = {
        "mileage": "Extra mileage is AED 1/km, or AED 0.50/km if you prepay! Daily includes 250 km, weekly 1,400 km, monthly 2,000 km.",
        "insurance": "Optional Full Insurance (CDW) costs AED 30/day, AED 100/week, or AED 250/month. Basic insurance is already included!",
        "deposit": "Security options: AED 1,000 refundable deposit OR non-deposit option at AED 30/day, AED 80/week, AED 150/month.",
        "delivery": "Delivery available: Dubai AED 50, Sharjah AED 150, Ajman AED 250, Other Emirates AED 350. Or collect free from our Business Bay office!",
        "driver": "Additional driver costs AED 100 (optional).",
        "payment": "Card/payment link transactions have a 3.5% admin fee.",
        "office": "Office 1856 - Tamani Arts Offices - Al Asayel Street - Business Bay - Dubai. Complimentary extra mileage on collection!",
        "location": "📍 Business Bay, Dubai\n📞 +971 58 570 2655",
        "cheapest": "Our most affordable option is Geely Emgrand at AED 59/day. Our sales team can provide accurate pricing based on your rental duration and dates.",
    }

    def __init__(self, lead_name: str, conversation_mgr: ConversationManager):
        self.lead_name = lead_name
        self.state = conversation_mgr

    def generate(self, user_message: str, extracted_fields: Dict) -> str:
        """
        Generate response based on message type and conversation state.
        Priority:
        1. Check for direct questions → answer immediately
        2. Acknowledge new information → then ask next question
        3. Ask for missing fields → one at a time
        4. Ask for confirmation → if all details present
        5. Fallback to GPT → for general chat
        """

        message_lower = user_message.lower()

        # PRIORITY 1: Direct questions
        if self._is_direct_question(message_lower):
            answer = self._answer_direct_question(message_lower)
            if answer:
                return answer

        # PRIORITY 2: User provided new information
        if extracted_fields:
            # Update state with new fields
            for field, value in extracted_fields.items():
                if value:
                    self.state.update_field(field, value)

            # Check if they confirmed
            if extracted_fields.get("confirmed"):
                self.state.mark_confirmed()

            # Acknowledge their info
            ack = self._acknowledge_info(extracted_fields)
            if ack:
                # Fall through to ask next question
                pass

        # PRIORITY 3: Ask for missing fields (one at a time)
        missing = self.state.get_missing_fields()
        if missing:
            next_field = missing[0]

            # Check if we should ask this field
            if self.state.should_ask_field(next_field, max_asks=2):
                self.state.mark_field_asked(next_field)
                return self._ask_for_field(next_field)
            elif len(missing) > 1:
                # Already asked this field twice, skip to next
                next_field = missing[1]
                if self.state.should_ask_field(next_field, max_asks=2):
                    self.state.mark_field_asked(next_field)
                    return self._ask_for_field(next_field)

        # PRIORITY 4: All details present, ask for confirmation
        if self.state.is_ready_for_sales() and not self.state.is_confirmed():
            return self._ask_for_confirmation()

        # PRIORITY 5: Everything done, send to sales
        if self.state.is_ready_for_sales() and self.state.is_confirmed():
            return self._sales_handoff_message()

        # PRIORITY 6: Fallback - use GPT for general responses
        return self._gpt_response(user_message)

    def _is_direct_question(self, message_lower: str) -> bool:
        """Detect direct questions asking for specific information"""
        question_indicators = ["?", "what", "how", "do you have", "price", "cost", "you got"]
        return any(indicator in message_lower for indicator in question_indicators)

    def _answer_direct_question(self, message_lower: str) -> Optional[str]:
        """Answer direct questions if we know the answer"""

        # Check for pricing questions
        if "price" in message_lower or "cost" in message_lower or "how much" in message_lower:
            return self._handle_pricing_question(message_lower)

        # Check for availability questions
        if "do you have" in message_lower or "u have" in message_lower or "you got" in message_lower:
            return self._handle_availability_question(message_lower)

        # Check for policy/info questions
        if "mileage" in message_lower or "km" in message_lower:
            return self.PRICING_INFO["mileage"]
        if "insurance" in message_lower or "cdw" in message_lower or "damage" in message_lower:
            return self.PRICING_INFO["insurance"]
        if "deposit" in message_lower or "security" in message_lower:
            return self.PRICING_INFO["deposit"]
        if "delivery" in message_lower or "pickup" in message_lower or "collection" in message_lower:
            return self.PRICING_INFO["delivery"]
        if "driver" in message_lower or "additional" in message_lower:
            return self.PRICING_INFO["driver"]
        if "payment" in message_lower or "card" in message_lower:
            return self.PRICING_INFO["payment"]
        if "location" in message_lower or "address" in message_lower or "office" in message_lower:
            return self.PRICING_INFO["office"]
        if ("where" in message_lower or "contact" in message_lower) and ("you" in message_lower or "office" in message_lower):
            return self.PRICING_INFO["location"]

        return None

    def _handle_pricing_question(self, message_lower: str) -> str:
        """
        Handle pricing questions.
        Don't quote prices directly - explain that sales team provides customized quotes.
        """
        # Check if they're asking about specific car
        mentioned_car = self._find_mentioned_car(message_lower)

        if mentioned_car:
            return f"Great! We have {mentioned_car} models available. To get you the best pricing based on your specific rental duration, dates, and insurance preferences, our sales team will provide a customized quote. When would you like to start your rental?"
        else:
            return "To get you accurate pricing tailored to your rental duration and dates, our sales team will provide a customized quote. Let me gather a few details first. What type of car interests you?"

    def _handle_availability_question(self, message_lower: str) -> str:
        """Handle 'do you have X?' questions"""
        mentioned_car = self._find_mentioned_car(message_lower)

        if mentioned_car:
            # Confirm we have it, then ask for details if needed
            if not self.state.is_ready_for_sales():
                return f"Yes, we have {mentioned_car} models available! When would you like to start your rental?"
            else:
                return f"Yes, absolutely! We have {mentioned_car} models. Our sales team will be in touch shortly with your quote."
        else:
            return "Yes, we have a great range of vehicles! What type are you looking for - economy, luxury, sports, SUV?"

    def _find_mentioned_car(self, text: str) -> Optional[str]:
        """Find car brand/type mentioned in text"""
        text_lower = text.lower()

        # Check for brands first
        for brand_key, brand_name in self.CAR_BRANDS.items():
            if brand_key in text_lower:
                return brand_name

        # Check for car types
        for car_type in self.CAR_TYPES:
            if car_type in text_lower:
                return car_type.capitalize()

        return None

    def _acknowledge_info(self, fields: Dict) -> Optional[str]:
        """Acknowledge information user provided"""
        parts = []

        if fields.get("vehicle_model"):
            parts.append(f"got your interest in {fields['vehicle_model']}")
        if fields.get("rental_start_date"):
            parts.append(f"starting {fields['rental_start_date']}")
        if fields.get("rental_duration"):
            parts.append(f"for {fields['rental_duration']}")
        if fields.get("budget"):
            parts.append(f"budget around {fields['budget']}")

        if not parts:
            return None

        ack = "Perfect! " + ", ".join(parts) + "."
        return ack

    def _ask_for_field(self, field_name: str) -> str:
        """Ask for a specific field with natural variations"""
        ask_count = self.state.has_field_been_asked(field_name)[1]

        if field_name == "vehicle_model":
            if ask_count == 0:
                return "What type of car interests you? We have economy, luxury, sports, SUV, and offroad options."
            else:
                return "Any specific car brand or model in mind? (e.g., BMW, Tesla, Kia, etc.)"

        elif field_name == "rental_start_date":
            if ask_count == 0:
                return "When would you like to start your rental?"
            else:
                return "What date are you looking to start? Tomorrow, next week, or a specific date?"

        elif field_name == "rental_duration":
            if ask_count == 0:
                return "How many days, weeks, or months do you need the vehicle?"
            else:
                return "Would that be for a few days, a week, a month, or longer?"

        elif field_name == "budget":
            if ask_count == 0:
                return "What's your budget range for the rental?"
            else:
                return "No specific budget in mind? That's fine - our sales team can work with various options."

        return "Anything else I should know?"

    def _ask_for_confirmation(self) -> str:
        """Ask for final confirmation of details"""
        summary = self.state.get_summary()
        details = []

        if summary.get("vehicle_model"):
            details.append(summary["vehicle_model"])
        if summary.get("rental_start_date"):
            details.append(f"starting {summary['rental_start_date']}")
        if summary.get("rental_duration"):
            details.append(f"for {summary['rental_duration']}")
        if summary.get("budget"):
            details.append(f"budget {summary['budget']}")

        if not details:
            return "Let me make sure I have everything - shall I forward your inquiry to our sales team?"

        details_str = ", ".join(details)
        return f"Let me confirm: {details_str}. Does everything sound right?"

    def _sales_handoff_message(self) -> str:
        """Message when forwarding to sales"""
        return "Perfect! Our sales team will be in touch shortly with a customized quote and all the details. They'll help you get the best deal. See you soon!"

    def _gpt_response(self, user_message: str) -> str:
        """Fallback: Use GPT for general responses"""
        history = self.state.get_conversation_history_text()
        response = openai_service.generate_response(
            self.lead_name,
            user_message,
            history,
            lead_already_sent=self.state.is_ready_for_sales()
        )
        return response
