import os
import json
from dotenv import load_dotenv
from google import genai


# -----------------------------
# Load Environment Variables
# -----------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing from .env"
    )


# -----------------------------
# Gemini Client
# -----------------------------

client = genai.Client(
    api_key=API_KEY
)


# -----------------------------
# Generate Itinerary
# -----------------------------

def generate_itinerary(
    destination,
    start_date,
    end_date,
    budget,
    interests,
    travel_style
):

    prompt = f"""
You are Safar, an intelligent travel planning assistant.

Create a realistic day-by-day itinerary for the user's trip.

Trip details:

Destination: {destination}
Start date: {start_date}
End date: {end_date}
Budget: ₹{budget}
Interests: {interests}
Travel style: {travel_style}

For every day provide:

1. Day number
2. Date
3. Morning activity
4. Afternoon activity
5. Evening activity
6. Food recommendation
7. Estimated daily spending

Important:

- Create one entry for every day of the trip.
- Keep the activities realistic.
- Keep the estimated spending within the total budget.
- Consider the user's interests and travel style.
- Do not include unnecessary explanations.
- Return ONLY valid JSON.

Return the JSON in exactly this structure:

{{
    "days": [
        {{
            "day": 1,
            "date": "YYYY-MM-DD",
            "morning": "Activity",
            "afternoon": "Activity",
            "evening": "Activity",
            "food": "Food recommendation",
            "estimated_cost": 0
        }}
    ]
}}
"""
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
   )

    print("GEMINI RESPONSE OBJECT:", response)
    print("GEMINI RESPONSE TEXT:", repr(response.text))

    return response.text


# -----------------------------
# Parse Itinerary
# -----------------------------

def parse_itinerary(response_text):

    response_text = response_text.strip()

    if response_text.startswith("```"):

        response_text = response_text.replace(
            "```json",
            ""
        )

        response_text = response_text.replace(
            "```",
            ""
        )

    return json.loads(
        response_text.strip()
    )
def generate_packing_list(
    destination,
    start_date,
    end_date,
    interests,
    travel_style
):
    prompt = f"""
You are Safar, an intelligent travel assistant.

Create a practical packing checklist for this trip.

Destination: {destination}
Start date: {start_date}
End date: {end_date}
Interests: {interests}
Travel style: {travel_style}

Consider:
- Destination conditions
- Trip duration
- Activities
- Travel style
- Essential travel items

Return ONLY valid JSON in this exact format:

{{
    "items": [
        "Item 1",
        "Item 2",
        "Item 3"
    ]
}}

Give 10 to 20 useful items.
Do not add explanations outside the JSON.
"""

    import time

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            return response.text

        except Exception as e:

            if "503" in str(e) or "UNAVAILABLE" in str(e):

                if attempt < 2:

                    time.sleep(3)

                else:

                    raise Exception(
                        "Gemini is temporarily unavailable. "
                        "Please try generating the packing list again in a moment."
                    )

            else:

                raise e
def parse_packing_list(response_text):

    import json

    text = response_text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    data = json.loads(text)

    return data

def generate_travel_story(
    destination,
    start_date,
    end_date,
    travel_style,
    interests,
    journal_entries
):

    journal_text = ""

    for entry in journal_entries:

        journal_text += f"""
Date: {entry.get('date', '')}
Location: {entry.get('location', '')}
Mood: {entry.get('mood', '')}
Entry: {entry.get('entry', '')}
"""

    prompt = f"""
You are Safar, an intelligent travel storyteller.

Create a beautiful personal travel story based on the user's journey.

Trip details:

Destination: {destination}
Start date: {start_date}
End date: {end_date}
Travel style: {travel_style}
Interests: {interests}

Journal entries:

{journal_text}

Write the story as a warm, personal travel memory.

Include:
- A meaningful title
- An engaging introduction
- The important moments from the journey
- Feelings and experiences from the journal
- A memorable ending

Do not invent major events that are not present in the provided information.

Return ONLY valid JSON in this exact format:

{{
    "title": "Travel Story Title",
    "story": "Complete travel story here"
}}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text

def parse_travel_story(response_text):

    response_text = response_text.strip()

    if response_text.startswith("```"):

        response_text = response_text.replace(
            "```json",
            ""
        )

        response_text = response_text.replace(
            "```",
            ""
        )

    return json.loads(
        response_text.strip()
    )

def ask_safar_ai(
    destination,
    start_date,
    end_date,
    travel_style,
    interests,
    journal_entries,
    question
):

    journal_text = ""

    for entry in journal_entries:

        journal_text += f"""
Date: {entry.get('date', '')}
Location: {entry.get('location', '')}
Mood: {entry.get('mood', '')}
Entry: {entry.get('entry', '')}
"""

    prompt = f"""
You are Safar AI, a helpful personal travel assistant.

Trip:
Destination: {destination}
Start date: {start_date}
End date: {end_date}
Travel style: {travel_style}
Interests: {interests}

User's journal:
{journal_text}

User's question:
{question}

Answer naturally and helpfully.

Use the trip information and journal context when relevant.
Do not invent personal experiences that are not provided.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text