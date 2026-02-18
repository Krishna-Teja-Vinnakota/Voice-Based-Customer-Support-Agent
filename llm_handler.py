"""
LLM Handler - Using Gemini 2.0 Flash 
WITH GUARDRAILS AI INTEGRATION
"""

import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GeminiLLMHandler:
    def __init__(self):
        """Initialize Gemini LLM Handler with Gemini 2.0 Flash"""
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("[LLM] CRITICAL: GEMINI_API_KEY not found in environment. Cannot operate without LLM.")
        
        try:
            # Initialize the new client
            self.client = genai.Client(api_key=api_key)
            # Using Gemini 2.0 Flash - PROVEN TO WORK in your diagnostic
            self.model_name = 'gemini-2.0-flash'
            print(f"[LLM] Gemini 2.0 Flash initialized successfully (Pure LLM Mode)")
            
            # Initialize Guardrails (pass self.client for malicious intent detection)
            from guardrails_handler import GuardrailsHandler
            self.guardrails = GuardrailsHandler(llm_client=self.client)
            print("[LLM] Guardrails AI integrated successfully")
            
        except Exception as e:
            raise RuntimeError(f"[LLM] CRITICAL: Failed to initialize Gemini: {e}")
    
    def validate_and_process_input(self, user_input, conversation_history=None):
        """
        Validate input through guardrails before processing
        
        Returns:
            Tuple of (is_valid, processed_input, rejection_message)
        """
        is_valid, processed_input, rejection_reason = self.guardrails.validate_input(
            user_input,
            conversation_history
        )
        
        if not is_valid:
            # Get user-friendly rejection message
            rejection_msg = self.guardrails.get_rejection_message(rejection_reason)
            return False, processed_input, rejection_msg
        
        return True, processed_input, ""
    
    def detect_intent(self, user_input, conversation_history=None):
        """
        Detect user intent from input using Gemini with full context awareness
        Returns: dict with intent and whether authentication is required
        """
        # Build context from conversation history
        context_str = ""
        if conversation_history:
            recent_history = conversation_history[-6:]  # Last 3 exchanges
            context_str = "\n\nRecent conversation:\n"
            for msg in recent_history:
                role = "Customer" if msg['role'] == 'user' else "Agent"
                context_str += f"{role}: {msg['content']}\n"
        
        prompt = f"""You are an intelligent customer support AI analyzing queries in real-time.
Analyze the customer's message and determine their intent, considering the full conversation context.

{context_str}

Current customer message: "{user_input}"

Analyze this message and respond ONLY with valid JSON (no markdown, no explanation):
{{
    "intent": "the primary intent",
    "requires_authentication": true or false,
    "confidence": 0.0 to 1.0,
    "conversation_complete": true or false,
    "entities": {{
        "order_id": "if mentioned",
        "product": "if mentioned",
        "issue_type": "if mentioned"
    }}
}}

Intent categories (but not limited to these - identify the TRUE intent):
- order_status: Checking order, tracking, "where is my order"
- refund_request: Refund, return, money back, cancellation
- delivery_info: Delivery questions, shipping, ETA, address
- product_inquiry: Questions about products, features, availability
- complaint: Problems, issues, dissatisfaction
- greeting: Hello, hi, starting conversation
- goodbye: Ending conversation, thank you
- authentication_response: Providing order ID or credentials
- general_query: Any other legitimate question

IMPORTANT: 
- Understand context and follow-up questions
- Be flexible - customers don't use perfect keywords

CONVERSATION COMPLETION:
Set "conversation_complete": true if customer says goodbye or indicates they're done.
Set "conversation_complete": false if customer has more questions.

Authentication required for: order_status, refund_request, delivery_info (if asking about specific order)

Output ONLY the JSON object."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=300,
                )
            )
            response_text = response.text.strip()
            
            # Clean up response
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            result = json.loads(response_text)
            print(f"[LLM] Detected intent: {result['intent']} (confidence: {result.get('confidence', 'N/A')})")
            
            # Log if conversation should end
            if result.get('conversation_complete', False):
                print(f"[LLM] Conversation completion detected - user is done")
            
            return result
        
        except json.JSONDecodeError as e:
            print(f"[LLM] JSON parsing error: {e}")
            print(f"[LLM] Raw response: {response_text}")
            return self._retry_intent_detection(user_input)
        
        except Exception as e:
            print(f"[LLM] Error detecting intent: {e}")
            return self._retry_intent_detection(user_input)
    
    def _retry_intent_detection(self, user_input):
        """Retry intent detection with simplified prompt"""
        simple_prompt = f"""Analyze: "{user_input}"

Reply with only this JSON:
{{"intent": "order_status or refund_request or delivery_info or general_query or greeting or goodbye", "requires_authentication": true or false}}"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=simple_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=200,
                )
            )
            response_text = response.text.strip()
            
            # Clean response
            if "```" in response_text:
                response_text = response_text.split("```")[1].replace("json", "").strip()
            
            result = json.loads(response_text)
            result['confidence'] = 0.6
            return result
        except:
            # Last resort - treat as general query
            return {
                "intent": "general_query",
                "requires_authentication": False,
                "confidence": 0.4
            }
    
    def generate_response(self, user_input, context, order_data=None):
        """
        Generate natural, intelligent response using Gemini with full context
        """
        # Build comprehensive context
        system_context = """You are an intelligent, empathetic customer support agent for an e-commerce company.

Your personality:
- Warm, friendly, and professional
- Natural conversational style (like a real human)
- Concise but complete (2-3 sentences typically)

Your capabilities:
- Check order status and tracking
- Process refund requests
- Answer delivery questions
- Provide product information
- Handle complaints professionally

CRITICAL: You ONLY help with e-commerce orders. For off-topic questions, say:
"I'm here to help with your orders and shopping queries only. Please ask me about your order status, delivery, refunds, or products."

EXCEPTION - CONTEXT-AWARE:
If a question contains unusual words BUT is clearly about the customer's order, answer it normally.
Example: "Did the elections delay my order?" → This is about THEIR ORDER (help them)"""

        # Add conversation history
        conversation_str = ""
        if context.get('conversation_history'):
            recent = context['conversation_history'][-10:]
            conversation_str = "\n\nConversation so far:\n"
            for msg in recent:
                role = "Customer" if msg['role'] == 'user' else "You"
                conversation_str += f"{role}: {msg['content']}\n"
        
        # Add authentication context
        auth_context = ""
        if context.get('authenticated'):
            auth_context = f"\n\nAuthentication: Customer is VERIFIED for order {context.get('order_id')}"
        else:
            auth_context = "\n\nAuthentication: Customer is NOT verified yet"
        
        # Add order data
        order_context = ""
        if order_data:
            order_context = f"""

Current Order Data:
- Order ID: {order_data.get('order_id')}
- Product: {order_data.get('product')}
- Status: {order_data.get('status')}
- Delivery Date: {order_data.get('delivery_date')}
- Amount: ₹{order_data.get('amount')}

Use this information naturally in your response."""

        # Build the complete prompt
        full_prompt = f"""{system_context}

{auth_context}
{conversation_str}
{order_context}

Customer's current message: "{user_input}"

Your response (2-3 sentences):"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.95,
                    max_output_tokens=150,
                )
            )
            
            generated_response = response.text.strip()
            
            # Clean up any artifacts
            if generated_response.startswith('"') and generated_response.endswith('"'):
                generated_response = generated_response[1:-1]
            
            print(f"[LLM] Generated response ({len(generated_response)} chars)")
            return generated_response
        
        except Exception as e:
            print(f"[LLM] Error generating response: {e}")
            return self._retry_response_generation(user_input, order_data)
    
    def _retry_response_generation(self, user_input, order_data):
        """Retry response generation with simplified approach"""
        simple_prompt = f"""Customer says: "{user_input}"

{f"Order info: {order_data.get('order_id')} - {order_data.get('product')} - {order_data.get('status')}" if order_data else ""}

Respond as a helpful customer support agent (2-3 sentences):"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=simple_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=150,
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"[LLM] Retry also failed: {e}")
            raise RuntimeError("Unable to generate response. LLM service may be unavailable.")
    

# Global LLM handler instance
llm_handler = GeminiLLMHandler()