"""
Authentication Handler - Manages user authentication for secure data access
"""

from data_store import get_order_details, validate_phone_digits, normalize_order_id, normalize_phone_digits


class AuthHandler:
    def __init__(self):
        self.pending_auth = {}  # Tracks authentication state per session
    
    def requires_authentication(self, intent):
        """Check if the intent requires authentication"""
        protected_intents = [
            "order_status",
            "refund_request",
            "account_info",
            "payment_info",
            "delivery_address"
        ]
        return intent in protected_intents
    
    def start_authentication(self, session_id):
        """Initialize authentication process"""
        self.pending_auth[session_id] = {
            "step": "awaiting_order_id",
            "order_id": None,
            "attempts": 0
        }
        return "Sure, I can help you with that. Please tell me your three-digit order ID."
    
    def process_auth_input(self, session_id, user_input):
        """Process authentication input step by step"""
        if session_id not in self.pending_auth:
            return None, "Authentication not initiated"
        
        auth_state = self.pending_auth[session_id]
        
        # Get order ID
        if auth_state["step"] == "awaiting_order_id":
            # Extract order ID from user input
            order_id = self._extract_order_id(user_input)
            
            if not order_id:
                return None, "I couldn't find a valid order ID. Please say your three-digit order ID, for example, 'one two three' or 'four five six'."
            
            order = get_order_details(order_id)
            if not order:
                auth_state["attempts"] += 1
                if auth_state["attempts"] >= 3:
                    del self.pending_auth[session_id]
                    return None, "I'm sorry, I couldn't verify your order. Please try again later or speak with a human agent."
                return None, f"Order {order_id} not found. Please check and try again."
            
            # Move to phone verification
            auth_state["order_id"] = order_id
            auth_state["step"] = "awaiting_phone_digits"
            return None, "For security, please confirm the last two digits of your registered phone number."
        
        # Verify phone digits
        elif auth_state["step"] == "awaiting_phone_digits":
            order_id = auth_state["order_id"]
            digits = self._extract_digits(user_input)
            
            if not digits:
                return None, "I couldn't hear the digits clearly. Please say the last two digits of your phone number."
            
            # Validate phone digits
            if validate_phone_digits(order_id, digits):
                # Authentication successful
                del self.pending_auth[session_id]
                return order_id, "verified"
            else:
                auth_state["attempts"] += 1
                if auth_state["attempts"] >= 3:
                    del self.pending_auth[session_id]
                    return None, "Authentication failed. For security reasons, this session will end. Please call again."
                return None, "The digits don't match our records. Please try again."
        
        return None, "Authentication error"
    
    def _extract_order_id(self, text):
        """
        Extract order ID from text using intelligent normalization
        Handles: "123", "one two three", "one twenty three", etc.
        """
        # Use the smart normalization function from data_store
        normalized_id = normalize_order_id(text)
        
        # Check if we got a valid 3-digit order ID
        if normalized_id and len(normalized_id) == 3 and normalized_id.isdigit():
            # Verify it exists in our system
            order = get_order_details(normalized_id)
            if order:
                print(f"[Auth] Successfully extracted order ID: {normalized_id} from '{text}'")
                return normalized_id
            else:
                print(f"[Auth] Extracted {normalized_id} but order not found")
        
        print(f"[Auth] Could not extract valid order ID from: '{text}'")
        return None
    
    def _extract_digits(self, text):
        """
        Extract phone digits from spoken text using intelligent normalization
        Handles: "10", "ten", "one zero", "twenty-five", etc.
        """
        # Use the smart normalization function from data_store
        normalized_digits = normalize_phone_digits(text)
        
        # Check if we got valid digits
        if normalized_digits and normalized_digits.isdigit() and len(normalized_digits) <= 4:
            print(f"[Auth] Successfully extracted digits: {normalized_digits} from '{text}'")
            return normalized_digits
        
        print(f"[Auth] Could not extract valid digits from: '{text}'")
        return None
    
    def is_pending_auth(self, session_id):
        """Check if session has pending authentication"""
        return session_id in self.pending_auth


# Global auth handler instance
auth_handler = AuthHandler()