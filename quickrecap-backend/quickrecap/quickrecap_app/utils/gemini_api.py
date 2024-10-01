import google.generativeai as genai
from quickrecap_app.config import GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)

def generate_questions_from_gemini(text):
    prompt = f"""Utiliza el siguiente texto para generar 5 preguntas de opción múltiple en el siguiente formato JSON:
       {{
         "questions": [
           {{
             "question": "Pregunta aquí",
             "alternatives": ["Opción 1", "Opción 2", "Opción 3", "Opción 4"],
             "answer": 0
           }},
           // Agregar más preguntas
         ]
       }}\n\nTexto:\n{text}"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text.strip()