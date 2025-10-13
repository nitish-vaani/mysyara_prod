from datetime import datetime
import re

import pytz


def current_time(timezone: str = "GMT") -> str:
    try:
        tz = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        tz = pytz.timezone("GMT")

    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


def get_month_year_as_string():
    from datetime import datetime

    now_ = datetime.now()
    current_month = now_.strftime("%B")
    current_year = now_.year
    return f"{current_year}/{current_month}"

def get_month_year_from_datetime(dt_str):
    dt = datetime.fromisoformat(dt_str)
    return dt.year, dt.strftime("%B")

def get_call_duration(transcript: str) -> int:
    # Find all timestamps in the format [YYYY-MM-DD HH:MM:SS]
    timestamps = re.findall(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", transcript)

    if not timestamps or len(timestamps) < 2:
        return 0  # Not enough data to calculate duration

    # Convert first and last timestamp to datetime objects
    start_time = datetime.strptime(timestamps[0], "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(timestamps[-1], "%Y-%m-%d %H:%M:%S")

    # Calculate the duration in seconds
    duration_seconds = int((end_time - start_time).total_seconds())
    return duration_seconds

# def strip_data_func(transcript: str) -> str:
#     """
#     Strips the transcript of any timestamps and returns the cleaned text.
#     """
#     # Remove timestamps in the format [YYYY-MM-DD HH:MM:SS]
#     cleaned_transcript = re.sub(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]", "", transcript)
    
#     # Remove any extra whitespace and newlines
#     cleaned_transcript = re.sub(r"\\s+", " ", cleaned_transcript)
#     return cleaned_transcript.strip()

def strip_data_func(transcript: str) -> str:
    """
    Cleans the transcript by:
    - Removing timestamps like [YYYY-MM-DD HH:MM:SS]
    - Removing newlines after "AGENT:" and "USER:" while preserving breaks between turns
    - Normalizing spaces
    """
    # Step 1: Remove timestamps
    transcript = re.sub(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]", "", transcript)

    # Step 2: Collapse newlines *immediately after* AGENT: or USER:
    transcript = re.sub(r"(AGENT:|USER:)\s*\n+", r"\1 ", transcript)

    # Step 3: Remove extra whitespace
    transcript = re.sub(r"[ \t]+", " ", transcript)           # multiple spaces/tabs → single space
    transcript = re.sub(r"\n{3,}", "\n\n", transcript)         # more than 2 newlines → just 2

    return transcript.strip()



if __name__ == "__main__":
    # new_time = status_code = "2025-04-25 05:23:10.495827"
    # year, month = (get_month_year_from_datetime(new_time))
    # print(f"Year: {year}-{type(year)}, Month: {month}-{type(month)}")
    transcript = """
[2025-05-30 11:48:36] AGENT:
Hello?

[2025-05-30 11:48:40] USER:
Hello.

[2025-05-30 11:48:44] AGENT:
Namaste and welcome! This is your friendly Air India Virtual Booking Assistant. Am I speaking with Nitish today?

[2025-05-30 11:48:49] USER:
Yes.

[2025-05-30 11:48:52] AGENT:
Great! I’m here to help you book your flight quickly and easily. Is now a good time to chat?

[2025-05-30 11:48:57] USER:
Yes, go ahead.

[2025-05-30 11:48:58] AGENT:
Perfect! Do you prefer continuing in English or Hindi?

[2025-05-30 11:49:04] USER:
Let's do in हिंदी.

[2025-05-30 11:49:11] AGENT:
बिलकुल! मैम, ये एक सेवा कॉल है और quality और training के लिए रिकॉर्ड की जा सकती है। तो आइए शुरू करें—आप किस शहर से उड़ान भरना चाहते हैं?

[2025-05-30 11:49:19] USER:
मैं Mumbai से.

[2025-05-30 11:49:19] AGENT:
Noted. और आपको किस शहर जाना है?

[2025-05-30 11:49:26] USER:
मुझे जाना है कोलकाता.

[2025-05-30 11:49:27] AGENT:
बहुत बढ़िया! Mumbai से Kolkata के लिए हमारी नियमित फ्लाइट्स चलती...

[2025-05-30 11:49:35] USER:
इसमें एक MP 3 करके folder है उसमें उसमें सारा MP 3 से होगा. हां.

[2025-05-30 11:49:42] AGENT:
मुझे खेद है, मुझे इस विषय में जानकारी नहीं है, लेकिन क्या हम फ्लाइट बुकिंग पर वापस लौट सकते हैं? आपकी यात्रा की तारीख क्या है?

[2025-05-30 11:49:45] USER:
जी बताइए.

[2025-05-30 11:49:45] AGENT:
कृपया बताएं, आप किस तारीख को यात्रा...

[2025-05-30 11:49:49] USER:
हां यात्रा की तारीख है परसों की.

[2025-05-30 11:49:53] AGENT:
ठीक है, परसों के लिए यात्रा प्लान कर रहे हैं। आपके पास कोई खास समय है—सुबह, दोपहर, शाम या देर रात?

[2025-05-30 11:49:58] USER:
कभी भी चलेगा कभी भी चलेगा.

[2025-05-30 11:50:00] AGENT:
ठीक है, फ्लेक्सिबल टाइमिंग के साथ। क्या आप रिटर्न टिकट भी बुक करना चाहेंगे?

[2025-05-30 11:50:07] USER:
जी नहीं.

[2025-05-30 11:50:15] AGENT:
कोई बात नहीं, लेकिन मैं सुझाव देता हूँ कि आप AIR India के साथ रिटर्न टिकट भी बुक करें। इसमें आरामदायक यात्रा, बेहतर सेवा और किफायती कीमत का लाभ उठा सकते हैं। क्या मैं फिर भी रिटर्न विकल्प देखूँ?

[2025-05-30 11:50:22] USER:
अच्छा ठीक है मत देखिए आप.

[2025-05-30 11:50:24] AGENT:
बिलकुल सही! आपकी यात्रा में कुल कितने लोग होंगे, आपके अलावा?

[2025-05-30 11:50:30] USER:
मैं अकेले हूं.

[2025-05-30 11:50:48] AGENT:
ठीक है। आपके लिए दो फ्लाइट विकल्प हैं: - AI 100: Mumbai से सुबह 9 बजे उड़ान, Kolkata पहुँचती है 12 PM, किराया Rupees 6,000. - AI 105: Mumbai से दोपहर 1 बजे उड़ान, Kolkata पहुँचती है 4 PM, किराया Rupees 5,500. आप कौन-सी फ्लाइट लेना चाहेंगे?

[2025-05-30 11:51:00] USER:
कल की कर दीजिए.

[2025-05-30 11:51:07] AGENT:
ठीक है, AI 105 दोपहर 1 बजे की फ्लाइट बुक करता हूँ। अब, कृपया मुझे अपना पूरा नाम बताएं ताकि मैं आपके टिकट की जानकारी ले सकूं।

[2025-05-30 11:51:13] USER:
Sir पूरा नाम नितेश त्रिपाठी है.

[2025-05-30 11:51:17] AGENT:
धन्यवाद नितेश जी! क्या जिस नंबर पे हम बात कर रहे हैं वो बुकिंग के लिए उपयोग किया जा सकता है?

[2025-05-30 11:51:24] USER:
हां हां.

[2025-05-30 11:51:28] AGENT:
समझ लिया, तो आपकी संख्या है: नाइन फोर फाइव जीरो नाइन टू नाइन सेवन सेवन वन, सही है?

[2025-05-30 11:51:35] USER:
हां ठीक है. नहीं नहीं मेरा number दूसरा है.

[2025-05-30 11:51:37] AGENT:
ओह, सही है। कृपया अपना संपर्क नंबर बता दीजिए।

[2025-05-30 11:51:44] USER:
9 4 05:09 29771.

[2025-05-30 11:51:48] AGENT:
समझ गया, आपका नंबर है: नाइन फोर जीरो फाइव जीरो नाइन टू नाइन सेवन सेवन वन, सही है?

[2025-05-30 11:51:54] USER:
हां, ठीक है.

[2025-05-30 11:51:57] AGENT:
बहुत बढ़िया! अब कृपया टिकट भेजने के लिए अपना ईमेल आईडी बता दीजिए, अक्षर दर अक्षर।

[2025-05-30 11:52:12] USER:
NITESH TRIPATHI at the rate Gmail dot com.

[2025-05-30 11:52:17] AGENT:
धन्यवाद! तो आपका ईमेल आईडी है: N-I-T-E-S-H T-R-I-P-A-T-H-I at Gmail dot com, सही है?

[2025-05-30 11:52:23] USER:
जी सही.

[2025-05-30 11:52:27] AGENT:
सही है! क्या आप अपनी सीट चुनना चाहेंगे? हमारे पास विंडो, मिडिल, और आइसल सीट के ऑप्शन हैं।

[2025-05-30 11:52:32] USER:
नहीं नहीं.

[2025-05-30 11:52:37] AGENT:
कोई बात नहीं! क्या आप खाने का विकल्प चुनना चाहेंगे? हमारे पास वेजिटेरियन, नॉन-वेजिटेरियन, वेगन, जैन और डायबिटिक-फ्रेंडली ऑप्शन हैं।

[2025-05-30 11:52:44] USER:
Diabetes friendly कर दीजिए.

[2025-05-30 11:53:09] AGENT:
बिल्कुल! डायबिटिक-फ्रेंडली मील बुक कर दी गई है। अब, मैं आपकी बुकिंग का सारांश देता हूँ:  - मार्ग: Mumbai से Kolkata  - तिथि: कल की - फ्लाइट: AI 105 - सीट: कोई प्राथमिकता नहीं - मील: डायबिटिक-फ्रेंडली  - कुल किराया:    - एकतरफा यात्रा: छह हजार पांच सौ रुपए (इसमें फ्लाइट का किराया शामिल है: पांच हजार पांच सौ रुपए प्रति व्यक्ति, मील: चार सौ रुपए)  तो, कुल भुगतान योग्य राशि है: पांच हजार नौ सौ रुपए।  क्या मैं आपको भुगतान लिंक भेज दूँ?

[2025-05-30 11:53:18] USER:
कितना payment करना है?

[2025-05-30 11:53:22] AGENT:
आपको कुल पांच हजार नौ सौ रुपए का भुगतान करना है। क्या मैं आपको भुगतान लिंक भेज दूँ?

[2025-05-30 11:53:27] USER:
और यह यह flight flight किस date की है?

[2025-05-30 11:53:31] AGENT:
यह फ्लाइट कल, यानी इकतीस मई की है। अब क्या मैं आपको भुगतान लिंक भेज दूँ?

[2025-05-30 11:53:38] USER:
ठीक है भेज दीजिए.

[2025-05-30 11:53:39] AGENT:
बहुत बढ़िया! आपके मोबाइल नंबर पर भुगतान लिंक भेज...

[2025-05-30 11:53:46] USER:
Calulation भेज दिया उसको. अच्छा आपने आप कुछ तो चला आप आप human agent से बात करवा सकते हैं?

[2025-05-30 11:53:51] AGENT:
बिलकुल नितेश जी, मैं आपको एक विशेषज्ञ से जोड़ रहा हूँ जो आपकी सभी queries का उत्तर दे सके। कृपया थोड़ा इंतजार करें।

[2025-05-30 11:53:57] Function calls collected.

[2025-05-30 11:54:07] USER:
Hello?

[2025-05-30 11:54:07] Function calls collected.


    """
    final_transcript = strip_data_func(transcript)
    print(f"{final_transcript}")




# # Example Usage
# print(current_time("Asia/Kolkata"))
# print(current_time("America/New_York"))
# print(current_time("Invalid/Timezone"))
