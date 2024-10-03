import google.generativeai as genai
import json
from quickrecap_app.config import GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)

def generate_questions_flashcard(text):
    print("Generating Flashcards..")
    prompt = f"""Utiliza el siguiente texto para generar 5 definiciones (termino + definicion) en el siguiente formato JSON:
       {{
         "flashcard": [
           {{
             "id": 1, #ID unico para cada termino-definicion
             "termino": "Aca el termino que vas a definir según el texto proporcionado",
             "definicion": aca ira la definicion del termino,
           }},
           // Agregar más terminos
         ]
       }}\n\nTexto:\n{text}"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    json_response = response.text.strip()
    
    if json_response.startswith('```json'):
        json_response = json_response.replace('```json', '').replace('```', '').strip()
    
    try:
        json_data = json.loads(json_response)
        return json_data
    except json.JSONDecodeError:
        print("Error al decodificar JSON:", json_response)
        return None

def generate_questions_quiz(text):
    print("Generating Quiz..")
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
    
    json_response = response.text.strip()
    
    if json_response.startswith('```json'):
        json_response = json_response.replace('```json', '').replace('```', '').strip()
    
    try:
        json_data = json.loads(json_response)
        return json_data
    except json.JSONDecodeError:
        print("Error al decodificar JSON:", json_response)
        return None