import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from datetime import datetime
# from prompt_for_eval.azent import get_lead_classification_prompt



# Get current date dynamically
current_date = datetime.now()
current_date_str = current_date.strftime("%B %d, %Y")
current_year = current_date.year
next_year = current_year + 1

# Load API key from .env.local
load_dotenv("/app/.env.local")
api_key = os.getenv("OPENAI_API_KEY")



if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Instantiate the client
client = OpenAI(api_key=api_key)


async def has_user_speech(transcript: str) -> bool:
    for line in transcript.split("\n"):
        if line.strip().lower().startswith(("user:", "you:")):
            return True
    return False


NO_USER_EVAL = "{\n\"clarity\": { \"score\": 0, \"feedback\": \"There is no user speech in the provided transcript.\" },\n\"fluency\": { \"score\": 0, \"feedback\": \"There is no user speech in the provided transcript.\" },\n\"coherence\": { \"score\": 0, \"feedback\": \"There is no user speech in the provided transcript.\" },\n\"engagement\": { \"score\": 0, \"feedback\": \"There is no user speech in the provided transcript.\" },\n\"vocabulary\": { \"score\": 0, \"feedback\": \"There is no user speech in the provided transcript.\" },\n\"listening\": { \"score\": 0, \"feedback\": \"There is no user speech in the provided transcript.\" },\n\"summary\": \"No user speech was present in the conversation for evaluation.\",\n\"tip\": \"Ensure to provide user speech in the transcript for a comprehensive evaluation of communication skills.\"\n}"

async def call_summary(transcript: str) -> str:
    """
    Takes the complete transcipt and returns a 60-100 word summary for the conversation.
    """
    load_dotenv("/app/.env.local")
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    client = OpenAI(api_key=api_key)

    prompt = f"""
    You are a professional conversation summarizer for a flight booking service. 
    Your task is to analyse the conversation transcript and pick out the key points discussed
    between the user and the agent. Summary should be crisp, concise and clear. moreover,
    it should be enough for anyone reading to understand the main points of the conversation.
    it should not exceed 100 words.
    Transcript:
    {transcript}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional conversation summarizer for a flight booking service. Your task is to analyse the conversation transcript and pick out the key points discussed between the user and the agent. Summary should be crisp, concise and clear."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()
        result = {
            "summary": content,
            "status_code": 200
        }
        return result

    except Exception as e:
        # Return default structure with "Not Mentioned"
        result = {
            "summary": "Some error generating summary, please try again later.",
            "status_code": 400
        }
        return result

async def extract_entities_from_transcript(transcript: str, fields: list[tuple[str, str]]) -> dict:
    """
    Extracts specified entities from the USER's responses in a transcript.
    
    Parameters:
        transcript (str): The full conversation transcript.
        entity_fields (list): A list of field names you want to extract.

    Returns:
        dict: Structured result with extracted entities or default values on failure.
    """
    # Load API Key
    load_dotenv("/app/.env.local") 
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    client = OpenAI(api_key=api_key)

    # Prepare dynamic prompt
    field_instructions = "\n".join(
        [f"{i+1}. {field}: {desc}" for i, (field, desc) in enumerate(fields)]
    )

    # JSON template
    json_template = ",\n".join(
        [f'"{field}": {{"text": "...", "value": "...", "confidence": "..."}}' for field, _ in fields]
    )

    prompt = f"""
    You are an intelligent entity extraction system. Given a conversation transcript, extract the following fields ONLY based on what the USER says.

    Ignore the interviewer, assistant, or system. Focus only on USER responses.

    Here are the fields to extract:
    {field_instructions}

    Return a JSON object in the following format:
    {{
    {json_template}
    }}

    Rules:
    - "text": the actual user quote where the information is mentioned
    - "value": cleaned, structured value
    - "confidence": "high", "medium", "low" depending on clarity of user speech
    - If the user does not mention something, return:
    {{ "text": "NA", "value": "Not Mentioned", "confidence": "NA" }}
    - Do NOT include commentary. Only return valid JSON.
    Transcript:
    {transcript}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": "You are a specialized entity extraction system that focuses on job-related lifestyle and earnings information from user responses in conversations. Extract only what the user explicitly states."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content
        # Remove markdown ```json ... ``` wrapping if present
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json\n
        if content.endswith("```"):
            content = content[:-3]  # Remove trailing ```

        content = content.strip()
        return json.loads(content)

    except Exception as e:
        # Return default structure with "Not Mentioned"
        return {
            "error": f"Entity extraction failed: {str(e)}",
            "result": None
        }

async def conversation_eval(transcript: str) -> dict:
    """
    Evaluates a conversation based on clarity, fluency, coherence, engagement,
    vocabulary, and listening. Returns scores, feedback, a summary, and a tip.
    
    If data is insufficient, score is 0 and feedback explains that.
    """
    load_dotenv("/app/.env.local")
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    client = OpenAI(api_key=api_key)

    prompt = f"""
    You are an expert communication evaluator.

    Your task is to analyze the USER's responses in the transcript below and evaluate their speaking performance based on the following categories:

    1. **Clarity** – How clear and understandable the user's responses are.
    2. **Fluency** – The natural flow and smoothness of speech (even if text).
    3. **Coherence** – How logically ideas are connected.
    4. **Engagement** – Whether the user was actively participating or sounded interested.
    5. **Vocabulary** – Use of varied and appropriate vocabulary.
    6. **Listening** – Whether the user responded appropriately to what was said (shows active listening).
    7. **Summary** – Summarize the user's overall participation.
    8. **Tip** – Suggest one improvement the user can focus on next time.

    Rules:
    - Score each attribute from 0 to 5 (0 = not enough data, 5 = excellent).
    - Give short feedback for each score.
    - If there's not enough user data for a category, return: {{ "score": 0, "feedback": "Not enough data to evaluate" }}

    Return your response in exactly the following JSON format:

    {{
        "clarity": {{"score": ..., "feedback": "..."}},
        "fluency": {{"score": ..., "feedback": "..."}},
        "coherence": {{"score": ..., "feedback": "..."}},
        "engagement": {{"score": ..., "feedback": "..."}},
        "vocabulary": {{"score": ..., "feedback": "..."}},
        "listening": {{"score": ..., "feedback": "..."}},
        "summary": "...",
        "tip": "..."
    }}

    Only include the JSON. Do not add commentary.

    Transcript:
    {transcript}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional communication coach and evaluator. Evaluate user conversations with structured metrics."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )
        content = response.choices[0].message.content
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json\n
        if content.endswith("```"):
            content = content[:-3]  # Remove trailing ```

        content = content.strip()
        return json.loads(content)
        # result = json.loads(llm_output)
        # return result
    
    except Exception as e:
        return {
            "error": f"Evaluation failed: {str(e)}",
            "conversation_eval": {
                attr: {"score": 0, "feedback": "Not enough data to evaluate"}
                for attr in ["clarity", "fluency", "coherence", "engagement", "vocabulary", "listening"]
            } | {
                "summary": "Not enough data to evaluate",
                "tip": "Not enough data to provide a tip"
            }
        }

async def extract_job_entities_mysyara(transcript: str, fields: list[tuple[str, str]] = None) -> dict:
    """
    Extracts car-related entities from a conversation transcript, focusing on USER responses.
    """

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You extract structured car-related information from user responses in conversations. \
                                Only consider information explicitly stated by the USER. Do not guess."
                },
                {
                    "role": "user",
                    "content": f"""
        Extract the following fields from the user's responses ONLY in the conversation transcript below:

        - Name
        - Mobile_Number
        - Car_Make_Model
        - Year
        - Approximate_Mileage
        - Location
        - Slot_Booking_Time

        If a field is not mentioned, set "text": "NA", "value": "Not mentioned", "confidence": "NA".

        Format the result strictly as JSON like this:
        {{
        "Name": {{ "text": "...", "value": "...", "confidence": "high/medium/low/NA" }},
        "Mobile_Number": {{ "text": "...", "value": "...", "confidence": "high/medium/low/NA" }},
        "Car_Make_Model": {{ "text": "...", "value": "...", "confidence": "high/medium/low/NA" }},
        "Year": {{ "text": "...", "value": "...", "confidence": "high/medium/low/NA" }},
        "Approximate_Mileage": {{ "text": "...", "value": "...", "confidence": "high/medium/low/NA" }},
        "Location": {{ "text": "...", "value": "...", "confidence": "high/medium/low/NA" }},
        "Slot_Booking_Time": {{ "text": "...", "value": "...", "confidence": "high/medium/low/NA" }},
        }}

        Transcript:
        {transcript}
        """
                }
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()
        # print("🧪 RAW RESPONSE:\n", content)

        # Remove markdown ```json ... ``` wrapping if present
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json\n
        if content.endswith("```"):
            content = content[:-3]  # Remove trailing ```

        content = content.strip()
        return json.loads(content)

    except Exception as e:
        return {
            "error": f"Extraction failed: {str(e)}",
            "Name": {"text": "NA", "value": "Not mentioned", "confidence": "NA"},
            "Mobile_Number": {"text": "NA", "value": "Not mentioned", "confidence": "NA"},
            "Car_Make_Model": {"text": "NA", "value": "Not mentioned", "confidence": "NA"},
            "Year": {"text": "NA", "value": "Not mentioned", "confidence": "NA"},
            "Approximate_Mileage": {"text": "NA", "value": "Not mentioned", "confidence": "NA"},
            "Location": {"text": "NA", "value": "Not mentioned", "confidence": "NA"},
            "Slot_Booking_Time": {{ "text": "...", "value": "...", "confidence": "high/medium/low/NA" }}
        }

async def evaluate_call_success(transcript: str) -> dict:
    """
    Evaluates if a call was successful from customer's perspective.
    
    Args:
        transcript: Full conversation transcript
        
    Returns:
        dict: {"status": "Success"|"Failure"|"Undetermined", "status_code": 200|400}
    """
    load_dotenv("/app/.env.local")
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return {
            "status": "Undetermined",
            "status_code": 400,
            "error": "API key not configured"
        }
    
    client = OpenAI(api_key=api_key)

    prompt = f"""
    You are evaluating a customer service call transcript to determine if it was successful.

    Evaluation Criteria:
    - Did the conversation go well, primarily from the customer's perspective?
    - Were all customer questions answered satisfactorily?
    - Were there any unresolved issues or imperfect responses?

    Rules:
    - Respond with ONLY ONE WORD: "Success", "Failure", or "Undetermined"
    - Success: Customer's needs were met, questions answered, positive resolution
    - Failure: Customer frustrated, unresolved issues, poor service
    - Undetermined: Insufficient information, call dropped early, unclear outcome

    Transcript:
    {transcript}

    Your one-word evaluation:
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a call quality evaluator. Respond with only ONE word: Success, Failure, or Undetermined."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # Low temperature for consistent results
            max_tokens=10     # Only need one word
        )

        content = response.choices[0].message.content.strip()
        
        # Validate response
        valid_statuses = ["Success", "Failure", "Undetermined"]
        
        # Extract the status word (in case GPT adds punctuation)
        for status in valid_statuses:
            if status.lower() in content.lower():
                return {
                    "status": status,
                    "status_code": 200
                }
        
        # If no valid status found, return Undetermined
        return {
            "status": "Undetermined",
            "status_code": 200
        }

    except Exception as e:
        print(f"Error evaluating call success: {e}")
        return {
            "status": "Undetermined",
            "status_code": 400,
            "error": str(e)
        }


if __name__ == "__main__":
    # Example usage
    transcript = """
AGENT: Hi! You've reached MySyara, your trusted car care partner. I am Sam, how can I assist you today?.
interrupted: False

USER: Yeah. Can you tell me, like, what are the car services you have?.
interrupted: False

AGENT: Sure! We offer a variety of car services such as on-demand doorstep car wash, monthly doorstep car wash subscription, in-garage car wash, car servicing, oil change, doorstep battery replacement & boosting, pre-purchase inspections, car detailing & tinting, painting & denting, tire replacement, engine diagnostics, on-demand repairs, and car renewal & registration assistance. How can I assist you further with these services?.
interrupted: False

USER: Say I want to book a car wash..
interrupted: False

AGENT: That's great! Before we proceed, could you please let me know which emirate you are located in? MySyara currently operates in Dubai, Abu Dhabi, Sharjah, and Ajman. This information will help me provide you.
interrupted: True

USER: Yes. Yes. I'm in Dubai..
interrupted: False

AGENT: Great to hear that you are in Dubai! We offer a doorstep car wash service in Dubai. Would you prefer a doorstep car wash service or an in-garage car wash service? Let me know your preference, and I can.
interrupted: True

USER: Yeah. Those type is fine..
interrupted: False

AGENT: Got it! Could you please provide me with your full name so that I can proceed with booking the car wash service for you?.
interrupted: False

USER: Yeah. Go ahead. Is the latest party..
interrupted: False

AGENT: Sorry, I didn't quite catch that. Could you please repeat your full name for me to proceed with booking the car wash service for you?.
interrupted: False

USER: Yes. My name is..
interrupted: False

AGENT: Thank you for providing your name. What is the best number to reach you on for confirmation and updates regarding the car wash service booking?.
interrupted: False

USER: Yeah. (945) 092-9771..
interrupted: False

AGENT: Great, thank you for sharing your contact number. Could you please tell me the make and model of your car for the car wash booking?.
interrupted: False
"""

    import asyncio
    field = [('Name', 'What is the name Of the User'),
                             ('Mobile_Number', "What is the users mobile number?"),
                             ('Car_Make_Model', "What is the Car mnufacturing company and the name of the car"),
                             ('Year', "What is the make year of the car"),
                             ('Approximate_Mileage', "What is the milage on the vehicle"),
                             ('Location', "What is the location of the User"),
                             ('Slot_Booking_Time', "If the User has asked for a specific time for pickup, what is it?")
                             ]
    result1 = asyncio.run(extract_entities_from_transcript(transcript, fields=field))
    # result = asyncio.run(call_summary(transcript))
    print(json.dumps(result1, indent=2))

