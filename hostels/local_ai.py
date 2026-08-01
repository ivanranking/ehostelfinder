"""
Local AI response system for when external API is unavailable.
Provides keyword-based responses for common hostel questions.
Also supports Hugging Face free inference API.
"""

import os, urllib.request, urllib.error, json

HOSTEL_RESPONSES = {
    "amenities": [
        "Popular hostel amenities include:",
        "- Free WiFi throughout the property",
        "- 24/7 security and CCTV monitoring",
        "- Common areas for socializing",
        "- Laundry facilities",
        "- Kitchen access",
        "- Lockers in rooms",
        "- Regular cleaning and housekeeping",
        "Check individual hostel listings for specific amenities!"
    ],
    "booking": [
        "Booking process on EHostelFinder:",
        "1. Browse and filter hostels by university",
        "2. View detailed information and reviews",
        "3. Check availability and pricing",
        "4. Click 'Book Now' to reserve",
        "5. Complete payment and confirmation",
        "You can modify or cancel bookings from your account within 48 hours of check-in."
    ],
    "checkin": [
        "Check-in and Check-out Information:",
        "- Standard check-in time: 2:00 PM",
        "- Standard check-out time: 11:00 AM",
        "- Early check-in may be available (subject to availability)",
        "- Late check-out can often be arranged for a fee",
        "Contact your hostel directly for flexibility on these times."
    ],
    "payment": [
        "Payment Methods:",
        "- Credit/Debit Cards (Visa, Mastercard)",
        "- Digital Wallets (PayPal, Google Pay)",
        "- Bank Transfers",
        "- Mobile Payment Options",
        "All payments are secure and encrypted. You'll receive a confirmation email immediately."
    ],
    "cancellation": [
        "Cancellation Policy:",
        "- Free cancellation up to 7 days before arrival",
        "- 50% refund if cancelled 3-7 days before",
        "- No refund if cancelled within 3 days",
        "- Special policies may apply during peak seasons",
        "Contact support for exceptions or disputes."
    ],
    "safety": [
        "Safety Features:",
        "- 24/7 security staff on duty",
        "- CCTV cameras in common areas",
        "- Individual lockers for valuables",
        "- Secure key card access",
        "- Emergency contact numbers available",
        "- Student ID verification required",
        "EHostelFinder verifies all listed properties!"
    ],
    "price": [
        "Room Pricing Information:",
        "- Prices are per semester (not per night)",
        "- Single occupancy: Full room price",
        "- Shared rooms: Price splits between roommates",
        "- Payment plans may be available for some hostels",
        "- Contact hostel directly for custom arrangements"
    ],
    "availability": [
        "Room Availability:",
        "- Check the 'Available Rooms' section on each hostel page",
        "- Room quantities update in real-time",
        "- Book early to secure your preferred room",
        "- Join waitlist if room is unavailable"
    ]
}

def get_local_ai_response(question: str) -> str:
    """Generate a response based on keywords in the question."""
    question_lower = question.lower()
    
    # Check for keyword matches
    for keyword, response_parts in HOSTEL_RESPONSES.items():
        if keyword in question_lower:
            return '\n'.join(response_parts)
    
    # Default response for unmatched questions
    default_responses = [
        "That's a great question! Here's what I can help with:",
        "",
        "Popular topics I can assist with:",
        "🏠 **Amenities** - What facilities are available",
        "📅 **Booking process** - How to reserve a hostel",
        "🕐 **Check-in/out times** - Arrival and departure information",
        "💳 **Payment methods** - How to pay securely",
        "❌ **Cancellation policy** - Refund and cancellation terms",
        "🔒 **Safety features** - Security measures in place",
        "💰 **Pricing** - Room costs and payment plans",
        "📊 **Availability** - Room availability status",
        "",
        "Feel free to ask about any of these topics, or contact our support team for more help!"
    ]
    return '\n'.join(default_responses)

def get_hf_ai_response(question: str, context: str = None) -> str:
    """Use Hugging Face free inference API for AI responses."""
    hf_token = os.environ.get("HUGGING_FACE_TOKEN", "")
    if not hf_token:
        return get_local_ai_response(question)
    
    try:
        system_prompt = "You are a helpful hostel booking assistant for EHostelFinder in Uganda. Answer concisely about: room types (Single, Double, Triple, Quadruple, Dormitory), pricing, amenities, booking process, check-in, safety, cancellations, and roommate matching. Keep answers brief and helpful."
        
        payload = {
            "inputs": f"<s>[INST] <<SYS>> {system_prompt} <</SYS>> {question} [/INST]</s>",
            "parameters": {"max_new_tokens": 200, "temperature": 0.7, "top_p": 0.95}
        }
        
        req = urllib.request.Request(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {hf_token}", "Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", get_local_ai_response(question)).strip()
            if isinstance(result, dict):
                return result.get("generated_text", get_local_ai_response(question))
    except Exception:
        pass
    
    return get_local_ai_response(question)
