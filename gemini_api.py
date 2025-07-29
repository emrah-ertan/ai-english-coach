import os
import google.generativeai as genai
from dotenv import load_dotenv

# https://console.cloud.google.com/cloud-resource-manager?organizationId=0&inv=1&invt=Ab3rgg Google Projeler
# https://aistudio.google.com/app/apikey            Google Proje bazlı API KEY almak için
# https://ai.google.dev/gemini-api/docs/models      Gemini Kullanılabilecek modeller listesi


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)


model = genai.GenerativeModel("gemini-2.0-flash")

# levele göre soru üretme
def generate_question(level, asked_questions=None):
    if asked_questions is None or len(asked_questions) == 0:
        asked_questions_text = "Henüz soru sorulmadı."
    else:
        asked_questions_text = "\n".join(f"- {q}" for q in asked_questions)

    prompt = f"""
    You are an English teacher. Ask a {level}-level English question to a learner.
    Ask a question on different topic each time.
    Don't give the answer, just ask one question suitable for speaking practice.
    Do not write text outside the question you specify.

    Do NOT ask any question that is already in the list below:
    {asked_questions_text}
    """
    response = model.generate_content(prompt)
    if hasattr(response, "text"):
        return response.text.strip()
    else:
        return "Gemini yanıt vermedi."

#kullanıcı cevabını değerlendirir
def analyze_answer(user_answer, level):
    prompt = f"""
    You are an English teacher checking a {level}-level student's answer.

    Student's answer: "{user_answer}"

    1. Evaluate grammar and sentence structure. Also evaluate about semantic closeness of the answer and the question
    2. Highlight any spelling mistakes or missing parts.
    3. Give a feedback score from 1 to 10.
    4. Suggest a corrected version of the answer.
    5. Be kind and helpful.

    Return in a format like:
    - Hatalar (mistakes): ...
    - Puan (Score): ...
    - Öneri (suggestion): ...
    
    Write only the necessary parts.
    Give feedback in Turkish other than the examples you will give.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

#kelime çevirisi için fonksiyon
def check_translation(english_word, user_translation):
    prompt = f"""
You're an expert English-Turkish translator.
The English word is: "{english_word}"
The user's translation is: "{user_translation}"

Is this a correct Turkish translation?

Please be accurate. Do not tolerate similar-sounding words if the meaning is incorrect.

Respond ONLY in the following format:

- Is correct: Yes or No
- Correct translation: [write exact expected Turkish meaning]
- Feedback: [short, clear explanation in Turkish – especially why it's wrong if it's wrong]
- Score: [give a score between 1-10, where 10 means perfect translation, 1 means completely wrong]

Do not include any other text or intro.
Give your feedback in Turkish.
"""
    response = model.generate_content(prompt)
    text = response.text.strip()

    result = {
        "is_correct": None,
        "correct_translation": "",
        "feedback": "",
        "score": ""
    }

    for line in text.splitlines():
        if line.startswith("- Is correct:"):
            result["is_correct"] = line.split(":", 1)[1].strip()
        elif line.startswith("- Correct translation:"):
            result["correct_translation"] = line.split(":", 1)[1].strip()
        elif line.startswith("- Feedback:"):
            result["feedback"] = line.split(":", 1)[1].strip()
        elif line.startswith("- Score:"):
            result["score"] = line.split(":", 1)[1].strip()
            
    return result




from langchain.memory import ConversationBufferMemory

# Hafıza 
memory = ConversationBufferMemory(return_messages=True)

# free mode'da serbest sohbet etmek için 
def call_ai_model(user_input):
    try:
        history = memory.load_memory_variables({})["history"]
        prompt = f"""
Aşağıda bir kullanıcı ile AI arasında geçen önceki konuşmalar var.
Önceki konuşmalar:
{history}

Şimdi kullanıcı şu mesajı gönderdi:
{user_input}

Bu bağlama göre kullanıcıya doğal ve tutarlı bir yanıt ver.
Kullanıcı hangi dilde yazıyorsa sen de o dilde yanıt ver.
Dost canlısı ve ilgi çekici bir sohbet arkadaşısın. 
Doğal, canlı ve destekleyici bir şekilde yanıt verin.
Yanıtını liste maddelerini satır satır olacak şekilde yaz. 
"""
        response = model.generate_content(prompt).text.strip()
        memory.save_context({"input": user_input}, {"output": response})
        
        return response

    except Exception as e:
        return f"Hata: {e}"


# akademik
def evaluate_academic_english(user_input):
    prompt = f"""
You are an academic English writing assistant. A student has written the following paragraph. 
Please analyze the academic quality of the text, including vocabulary, structure, tone, grammar, and clarity. 
Give a detailed feedback and rate the academic level from 1 to 10 (not necessarily a float, you can give integers).

User Text: {user_input}

Respond ONLY in the following format:

- Feedback: [Give detailed academic feedback in English. Do NOT summarize the text.]
- Score: [give a score between 1-10, can be integer]
- Suggestion: [Offer a revised, improved version of the paragraph – only if there are improvements to suggest]
- True Version: [True version of user prompt to academic quality]
Do NOT include any other text or greeting or explanation outside this format.
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        result = {
            "feedback": "",
            "score": "",
            "suggestion": ""
        }

        for line in text.splitlines():
            if line.startswith("- Feedback:"):
                result["feedback"] = line.split(":", 1)[1].strip()
            elif line.startswith("- Score:"):
                result["score"] = line.split(":", 1)[1].strip()
            elif line.startswith("- Suggestion:"):
                result["suggestion"] = line.split(":", 1)[1].strip()
        
        return result["feedback"], result["score"]

    except Exception as e:
        return f"Hata: {e}", ""





















