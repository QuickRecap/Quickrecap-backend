import google.generativeai as genai
import json
from quickrecap_app.config import GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)

#-------------- FLASHCARDS --------------#
def generate_questions_flashcard(text, numero_preguntas):
    print("Generating Flashcards..")
    prompt = f"""Utiliza el siguiente texto para generar {numero_preguntas} definiciones (termino + definicion) en el siguiente formato JSON (todas las preguntas deben ser formuladas en español, en caso el texto venga en otro idioma se debera traducir con precision y exactitud al idioma español):
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
        json_data = json.loads(json_response, strict=False)
        return json_data
    except json.JSONDecodeError:
        print("Error al decodificar JSON:", json_response)
        return None

#-------------- QUIZ --------------#
def generate_questions_quiz(text, numero_preguntas):
    print("Generating Quiz..")
    prompt = f"""Utiliza el siguiente texto para generar {numero_preguntas} preguntas de opción múltiple en el siguiente formato JSON (todas las preguntas deben ser formuladas en español, en caso el texto venga en otro idioma se debera traducir con precision y exactitud al idioma español):
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
        json_data = json.loads(json_response, strict=False)
        return json_data
    except json.JSONDecodeError:
        print("Error al decodificar JSON:", json_response)
        return None

#-------------- GAPS --------------#
def generate_questions_gaps(text, numero_preguntas):
    print("Generating Gaps...")
    prompt = f"""Utiliza el siguiente texto de EJEMPLO para generar {numero_preguntas} oraciones con huecos para completar en el siguiente formato JSON. Sigue estas reglas estrictamente:

1. Cada oración debe tener entre 2 (mínimo) y 4 (máximo) huecos.
2. NO generes oraciones que contengan enumeraciones o listas de elementos.
3. Cada hueco debe tener una única respuesta correcta.
4. Cada respuesta correcta debe ser UNA SOLA PALABRA, sin palabras compuestas.
5. Usa el símbolo '&' para representar los huecos en el texto.
6. Ninguna respuesta puede repetirse con otra previamente asignada.
7. Todas las preguntas deben ser formuladas en español, en caso el texto venga en otro idioma se debera traducir con precision y exactitud al idioma español.

Formato JSON requerido:

{{
  "gaps": [
    {{
      "texto_completo": "Oracion completa aqui",
      "texto_con_huecos": "Oracion con huecos (&)",
      "incorrectas": ["incorrecta1", "incorrecta2"]
      "respuestas": [
        {{
          "opciones_correctas": ["alternativa"]
          "posicion": 0
        }},
        {{
          "opciones_correctas": ["alternativa"],
          "posicion": 1
        }},
        {{
          "opciones_correctas": ["alternativa"],
          "posicion": 2
        }},
        {{
          "opciones_correctas": ["alternativa"],
          "posicion": 3
        }}
      ]
    }}
  ]
}}

Genera {numero_preguntas} oraciones siguiendo este formato y las reglas especificadas, basándote en el siguiente texto de ejemplo:\n\n{text}"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    json_response = response.text.strip()
    
    if json_response.startswith('```json'):
        json_response = json_response.replace('```json', '').replace('```', '').strip()
    
    try:
        json_data = json.loads(json_response, strict=False)
        return json_data
    except json.JSONDecodeError:
        print("Error al decodificar JSON:", json_response)
        return None