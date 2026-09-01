import os
import json
import csv
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def scout_events_agent(user_query):
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    instruction = """
    You are the STM Scout, Translator, and Strategist.
    Find 5 Thai events for 2026 and output a RAW JSON LIST.
    
    SCHEMA:
    title, sub_title_thai, description, description_thai, event_type, 
    start_date, end_date, location_name, country_code, lat, lng, 
    organizer_name, event_website, must_see_highlights.

    STRATEGY:
    1. description_thai: 'Travel Blogger' style Thai.
    2. must_see_highlights: Return as a single string separated by semicolons.
    3. Scout: Use Google Search for REAL dates.
    """

    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=1024),
        tools=[types.Tool(google_search=types.GoogleSearch())],
        response_mime_type="application/json",
        system_instruction="""You are a Data Scraper, Translator, and Strategist...""",
    )

    print(f"🚀 Scout Agent is searching for: {user_query}...")
    
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=user_query,
        config=config,
    )
    
    return response.text

def save_to_csv(json_data, filename="scouted_events.csv"):
    try:
        events = json.loads(json_data)
        
        # If the AI returns a dictionary with a key like 'events', extract the list
        if isinstance(events, dict):
            for key in events:
                if isinstance(events[key], list):
                    events = events[key]
                    break

        if not events:
            print("No events found to save.")
            return

        # Get headers from the first item
        headers = events[0].keys()

        with open(filename, mode='w', newline='', encoding='utf-16') as file:
            # Using utf-16 with Tab delimiter is safest for Thai characters in Excel/Sheets
            writer = csv.DictWriter(file, fieldnames=headers, delimiter='\t')
            writer.writeheader()
            for event in events:
                writer.writerow(event)
        
        print(f"✅ Success! File saved to: {os.path.abspath(filename)}")
        print("💡 Tip: Open Google Sheets > File > Import > Upload this file.")
        
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")

if __name__ == "__main__":
    # 1. Run the Agent
    query = "Upcoming Thai festivals and art exhibitions in Europe, Asia and Bangkok 2026"
    raw_json = scout_events_agent(query)
    
    # 2. Export to your PC
    save_to_csv(raw_json)