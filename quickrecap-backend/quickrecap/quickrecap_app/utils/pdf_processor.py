import requests
import fitz
import os
import time
import json

from django.http import JsonResponse

def pdf_to_text(pdf_path):
    pdf_document = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    pdf_document.close()
    return text

def process_pdf_gemini(url):
        try:
            pdf_url = url

            #Validar su proporciono una URL
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

            # Extraer el texto del PDF
            pdf_text = pdf_to_text(temp_pdf_path)

            # Eliminar el archivo temporal
            os.remove(temp_pdf_path)

            # Retornar el texto extraído como parte de la respuesta JSON
            return JsonResponse({'pdf_text': pdf_text}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)