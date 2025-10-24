from .openai_eval import *

extractors = {
    "mysyara": {
                # "function": extract_job_entities_mysyara,
                "function":extract_entities_from_transcript,
                "entities": [('Name', 'What is the name Of the User'),
                             ('Mobile_Number', "What is the users mobile number?"),
                             ('Car_Make_Model', "What is the Car mnufacturing company and the name of the car"),
                             ('Year', "What is the make year of the car"),
                             ('Approximate_Mileage', "What is the milage on the vehicle"),
                             ('Location', "What is the location of the User"),
                             ('Slot_Booking_Time', "If the User has asked for a specific time for pickup, what is it?")
                             ]},
}

need_conversation_eval = ['mysyara'] #Conversation Evaluation based on clarity, coherence etc.

skip_db_search = [] #Skip DB search for conversation_eval and entity extraction.

regenerate_summaries = [] #Regenerate  the summary and save it in db.