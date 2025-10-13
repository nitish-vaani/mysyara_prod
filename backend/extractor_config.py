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

    "shunya": {
                # "function": extract_job_entities_shunya,
                "function":extract_entities_from_transcript,
                "entities":[("current_company", "Where the user is currently working (name of the company)"),
                            ("job_role", "The user's job title or role (e.g., DevOps Engineer, Delivery Executive)"),
                            ("tech_or_nontech", "Whether the user works in a technical or non-technical role"),
                            ("monthly_salary", "The user's current monthly take-home salary (include amount and currency, if stated)"),
                            ("expected_salary", "The salary or increment the user is expecting (amount or percentage, include currency if mentioned). If the user says 50 percent increment, Calculate the Expected salary by increasing current salary by said percent "),
                            ("notice_period", "The duration of the user's notice period before joining a new job"),
                            ("experience", "Total years of relevant experience stated by the user"),
                            ("reconnect_date_time", "If the user asks to be contacted later, extract the date/time they mention for reconnecting"),
                            ]},

    "sbi": {
            "function":extract_entities_from_transcript,
            "entities":[("Starting from", "Where is the user boarding the flight from?"), 
                        ("Going To", "Destination of the user?"),
                        ("Number of Seats", "What is the total number of tickets the user wants to book?"),
                        ("Meal Preferences", "What is users meal preference?"),
                        ("Seat Preference", "What is the Users seat preference?"),
                        ("Round Trip or One Way", "Is the user looking for a round trip or one way ticket?"),
                        ("Travel Date", "Which date is the user looking to travel?"),
                        ("Flight Details", "What are the flight details the user is looking for? (e.g. flight number, timings, etc.)"),
                        ("Total Fare", "What is the total fare for the tickets?"),
                        ]},

    "azent": {"function": extract_entities_from_transcript}

    
}

need_conversation_eval = ['shunya', 'mysyara'] #Conversation Evaluation based on clarity, coherence etc.

skip_db_search = ['azent', "sbi"] #Skip DB search for conversation_eval and entity extraction.

regenerate_summaries = [] #Regenerate  the summary and save it in db.