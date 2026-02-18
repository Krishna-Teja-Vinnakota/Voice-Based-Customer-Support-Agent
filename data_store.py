"""
Data Store - Dummy Backend Data
Contains sample customer and order data for POC
"""

# Dummy customer database - using simple numeric IDs for easier speech recognition
CUSTOMERS = {
    "123": {
        "order_id": "123",
        "customer_name": "John Doe",
        "phone_last_digits": "10",
        "status": "Delivered",
        "delivery_date": "2026-01-10",
        "product": "Wireless Headphones",
        "amount": 2999.00,
        "shipping_address": "123 Main St, Ghaziabad, UP"
    },
    "456": {
        "order_id": "456",
        "customer_name": "Jane Smith",
        "phone_last_digits": "25",
        "status": "In Transit",
        "delivery_date": "2026-01-22",
        "product": "Smart Watch",
        "amount": 15999.00,
        "shipping_address": "456 Park Ave, Ghaziabad, UP"
    },
    "789": {
        "order_id": "789",
        "customer_name": "Bob Johnson",
        "phone_last_digits": "47",
        "status": "Processing",
        "delivery_date": "2026-01-25",
        "product": "Laptop",
        "amount": 54999.00,
        "shipping_address": "789 Oak Dr, Ghaziabad, UP"
    }
}


def normalize_order_id(raw_input):
    """
    Normalize order ID from various speech inputs
    Handles: "123", "one two three", "one twenty three", "1 2 3", etc.
    """
    import re
    
    # Convert to lowercase and remove extra spaces
    text = raw_input.lower().strip()
    
    # Number word to digit mapping
    word_to_num = {
        'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
        'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
        'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
        'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
        'eighteen': '18', 'nineteen': '19', 'twenty': '20', 'thirty': '30',
        'forty': '40', 'fifty': '50', 'sixty': '60', 'seventy': '70',
        'eighty': '80', 'ninety': '90'
    }
    
    # Remove common phrases
    text = text.replace("order id is", "")
    text = text.replace("my order id is", "")
    text = text.replace("order id", "")
    text = text.replace("order number", "")
    text = text.replace("it's", "")
    text = text.replace("it is", "")
    text = text.replace("the", "")
    text = text.strip()
    
    # Case 1: Already numeric (123, 456, etc.)
    digits_only = re.sub(r'[^0-9]', '', text)
    if digits_only and len(digits_only) == 3:
        return digits_only
    
    # Case 2: "one two three" -> "123"
    words = text.split()
    if all(word in word_to_num for word in words):
        result = ''.join(word_to_num[word] for word in words)
        if len(result) == 3:
            return result
    
    # Case 3: "one twenty three" -> "123"
    # Handle compound numbers
    if len(words) == 2:
        if words[0] in word_to_num and words[1] in word_to_num:
            first = word_to_num[words[0]]
            second = word_to_num[words[1]]
            # "one" + "twenty three" = "1" + "23" = "123"
            combined = first + second
            if len(combined) == 3:
                return combined
    
    # Case 4: "four fifty six" -> "456"
    if len(words) == 3:
        if words[1] in ['twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']:
            if words[0] in word_to_num and words[1] in word_to_num and words[2] in word_to_num:
                first = word_to_num[words[0]]
                second = word_to_num[words[1]]
                third = word_to_num[words[2]]
                combined = first + second + third
                if len(combined) == 3:
                    return combined
    
    # Case 5: Extract any 3-digit number from text
    numbers = re.findall(r'\d{3}', text)
    if numbers:
        return numbers[0]
    
    # Return cleaned input if nothing matches
    return digits_only if digits_only else text


def get_order_details(order_id):
    """
    Retrieve order details by order ID
    Normalizes the input to handle various formats
    """
    # Normalize the order ID
    normalized_id = normalize_order_id(str(order_id))
    
    # Try exact match first
    if normalized_id in CUSTOMERS:
        return CUSTOMERS[normalized_id]
    
    # Try without normalization (for backward compatibility)
    return CUSTOMERS.get(str(order_id).upper())


def validate_phone_digits(order_id, last_digits):
    """
    Validate phone number last digits for authentication
    Also normalizes phone digit input from speech
    """
    # Normalize order ID
    normalized_order_id = normalize_order_id(str(order_id))
    order = get_order_details(normalized_order_id)
    
    if not order:
        return False
    
    # Normalize the spoken digits
    normalized_digits = normalize_phone_digits(last_digits)
    
    return order["phone_last_digits"] == normalized_digits


def normalize_phone_digits(raw_input):
    """
    Normalize phone digits from various speech inputs
    Handles: "10", "ten", "one zero", "1 0", etc.
    """
    import re
    
    text = raw_input.lower().strip()
    
    # Number word to digit mapping
    word_to_num = {
        'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
        'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
        'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
        'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
        'eighteen': '18', 'nineteen': '19', 'twenty': '20', 'thirty': '30',
        'forty': '40', 'fifty': '50', 'sixty': '60', 'seventy': '70',
        'eighty': '80', 'ninety': '90',
        'twenty-five': '25', 'twenty five': '25', 'forty-seven': '47', 'forty seven': '47'
    }
    
    # Case 1: Already numeric
    digits_only = re.sub(r'[^0-9]', '', text)
    if digits_only and len(digits_only) <= 4:
        return digits_only
    
    # Case 2: Direct word match (e.g., "ten" -> "10", "twenty-five" -> "25")
    if text in word_to_num:
        return word_to_num[text]
    
    # Case 3: "one zero" -> "10"
    words = text.split()
    if all(word in word_to_num for word in words):
        result = ''.join(word_to_num[word] for word in words)
        if len(result) <= 4:
            return result
    
    # Case 4: "twenty five" -> "25"
    if len(words) == 2:
        combined = ' '.join(words)
        if combined in word_to_num:
            return word_to_num[combined]
    
    return digits_only if digits_only else text


def create_refund_request(order_id, reason):
    """Simulate refund request creation"""
    normalized_id = normalize_order_id(str(order_id))
    order = get_order_details(normalized_id)
    
    if order:
        return {
            "success": True,
            "refund_id": f"REF{normalized_id}",
            "order_id": normalized_id,
            "reason": reason,
            "status": "Initiated",
            "message": "Refund request created successfully"
        }
    return {
        "success": False,
        "message": "Order not found"
    }


def get_service_status(service_type):
    """Get service availability status"""
    services = {
        "delivery": "Available in your area",
        "support": "Available 24/7",
        "returns": "Available within 30 days of delivery"
    }
    return services.get(service_type.lower(), "Service information not available")