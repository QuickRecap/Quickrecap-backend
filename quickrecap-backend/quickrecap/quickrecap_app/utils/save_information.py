import json

from rest_framework import status
from rest_framework.response import Response
from quickrecap_app.models import *

def createFlashcard(json_data, actividad_id):
    try:
        data = json.loads(json_data)
        actividad = Actividad.objects.get(pk=actividad_id)
        
        print("DATA:", data)
        
        for flashcard in data['flashcard']:
            pregunta = Enunciado.objects.create(
                actividad=actividad,
                enunciado=flashcard['termino']
            )

            Opcion.objects.create(
                enun_id=pregunta,
                texto=flashcard['definicion'],
                correcta=True
            )
                
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error al guardar la información: {e}")
        raise Exception("Error al procesar las preguntas")
    
    return Response(status=status.HTTP_200_OK)

def createQuiz(json_data, actividad_id):
    try:
        data = json.loads(json_data)
        actividad = Actividad.objects.get(pk=actividad_id)

        for question_data in data['questions']:
            pregunta = Enunciado.objects.create(actividad=actividad, enunciado=question_data['question'])

            for i, opcion_texto in enumerate(question_data['alternatives']):
                correcta = (i == question_data['answer'])
                Opcion.objects.create(enun_id=pregunta, texto=opcion_texto, correcta=correcta)

    except (json.JSONDecodeError, Exception) as e:
        print(f"Error al guardar la información: {e}")
        raise Exception("Error al procesar las preguntas")

    return Response(status=status.HTTP_200_OK)