import os
from google import genai
from google.genai import types # <--- Import types
from django.conf import settings

def get_ai_client():
    # Uses the unified 2026 Client
    return genai.Client(api_key=settings.GEMINI_API_KEY)

def generate_agent_response(prompt, system_instruction):
    client = get_ai_client()

    # Define the Search Tool (The "Scout" power)
    search_tool = types.Tool(
        google_search=types.GoogleSearch()
    )



    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
        config=types.GenerateContentConfig( # Use the config object
            system_instruction=system_instruction,
            tools=[search_tool], # <--- This enables the LIVE web search
            thinking_config=types.ThinkingConfig(thinking_level="MEDIUM"),
            response_mime_type="application/json" # Forces JSON for your pipeline
        )
    )
    return response.text

class NokinhouseAgent:
    def __init__(self):

        self.model = genai.GenerativeModel("gemini-3-flash")

    def process_task(self, prompt, context=""):
        """
        General purpose agent method for sourcing, coding, or content.
        """
        full_prompt = f"""
        System: You are the Nokinhouse AI Assistant.
        Context: {context}
        User Task: {prompt}
        """

        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error connecting to Gemini: {str(e)}"
    def generate_craft_instructions(self, craft_type):
        """
        Specific agent tool for your digital hosting.
        """
        prompt = f"Write a warm, supportive step-by-step guide in Swedish for a {craft_type} workshop for seniors."
        return self.process_task(prompt)

# Simple Python Pricing Logic for Creative Gaze
def calculate_kit_price(base_cost, complexity_level, shipping_region):
    # Artisan markup is higher for complex designs
    markup = 3.0 if complexity_level == "Artisan" else 2.5
    
    # Add a premium for special Thai materials
    material_premium = 50 if "mulberry" in base_cost else 0
    
    subtotal = (base_cost * markup) + material_premium
    return round(subtotal, -1) - 1 # Rounds to the nearest 9 (e.g., 449 kr)