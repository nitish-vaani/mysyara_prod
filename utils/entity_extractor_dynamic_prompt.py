def generate_prompt_to_get_entities_from_transcript(transcript: str, fields: list[tuple[str, str]]) -> dict:
    """
    Extracts specified entities from the USER's responses in a transcript.
    
    Parameters:
        transcript (str): The full conversation transcript.
        entity_fields (list): A list of field names you want to extract.

    Returns:
        dict: Structured result with extracted entities or default values on failure.
    """
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
    return prompt
    
