import requests
import PyPDF2 as ac
import os
import time
import json

from django.http import JsonResponse

import io  # Asegúrate de importar io

def pdf_to_text(pdf_bytes):
    print("Iniciando pdf_to_text")
    try:
        print("Creando objeto PdfReader desde bytes")
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_reader = ac.PdfReader(pdf_file)
        text = ''
        print("Extrayendo texto de cada página")
        for page in pdf_reader.pages:
            text += page.extract_text()
        print("Texto extraído:", text)
        return text
    except Exception as e:
        print("Error extrayendo texto del PDF:")
        print(f"Error: {e}")
        return ''

def process_pdf_gemini(url):
    try:
        pdf_url = url
        print("Iniciando process_pdf_gemini")
        print("URL del PDF:", pdf_url)
        
        # Validar si se proporcionó una URL
        if not pdf_url:
            print("No se proporcionó la URL del PDF")
            return JsonResponse({'error': 'No se proporcionó la URL del PDF'}, status=400)

        # Descargar el archivo PDF desde Firebase
        print("Descargando archivo PDF")
        response = requests.get(pdf_url)
        if response.status_code != 200:
            print("Error al descargar el archivo PDF")
            return JsonResponse({'error': 'No se pudo descargar el archivo PDF'}, status=500)
        
        print("Pase las validaciones")
        
        # Pasar directamente el contenido en bytes a pdf_to_text
        pdf_text = pdf_to_text(response.content)

        print("Texto extraído:", pdf_text)
        
        # Retornar el texto extraído como parte de la respuesta JSON
        return JsonResponse({'pdf_text': pdf_text}, status=200)

    except json.JSONDecodeError:
        print("Error: JSON inválido")
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        print("Error general:", str(e))
        return JsonResponse({'error': str(e)}, status=500)