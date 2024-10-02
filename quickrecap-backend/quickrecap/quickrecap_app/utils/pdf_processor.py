import requests
import fitz
import os
import time
import json

from django.http import JsonResponse
from .gemini_api import generate_questions_quiz, generate_questions_flashcard

def pdf_to_text(pdf_path):
    pdf_document = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    pdf_document.close()
    return text

def process_pdf_gemini(url, categoria):
    #if request.method == 'POST':
        start_time = time.time()
        try:
            #data = json.loads(request.body)
            pdf_url = url

            if not pdf_url:
                return JsonResponse({'error': 'No se proporcionó la URL del PDF'}, status=400)

            # Descargar el archivo PDF desde Firebase
            response = requests.get(pdf_url)
            if response.status_code != 200:
                return JsonResponse({'error': 'No se pudo descargar el archivo PDF'}, status=500)
            
            # Guardar el PDF en un archivo temporal
            temp_pdf_path = 'temp.pdf'
            with open(temp_pdf_path, 'wb') as f:
                f.write(response.content)

            # Obtener el tamaño del archivo PDF en kilobytes
            pdf_size_kb = os.path.getsize(temp_pdf_path) / 1024

            # Extraer el texto del PDF
            pdf_text = pdf_to_text(temp_pdf_path)

            # Generar preguntas basadas en el texto
            questions_string = generate_questions_flashcard(pdf_text)
            #questions_string = generate_questions_from_gemini(pdf_text)

            # Eliminar el archivo temporal
            os.remove(temp_pdf_path)

            # Intentar convertir la cadena de respuesta en un JSON
            try:
                if questions_string.startswith('```json'):
                    questions_string = questions_string.replace('```json', '').replace('```', '').strip()

                questions = json.loads(questions_string)

            except json.JSONDecodeError:
                return JsonResponse({'error': 'Error al procesar la respuesta de Gemini como JSON'}, status=500)

            # Calcular el tiempo transcurrido
            elapsed_time = time.time() - start_time
            print(f"Tiempo de generación Gemini: {elapsed_time:.2f} segundos | PDF: {pdf_size_kb:.2f} KB")
            print(questions)
            return JsonResponse(questions)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)