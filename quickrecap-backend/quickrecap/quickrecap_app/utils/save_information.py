import json

from rest_framework import status
from rest_framework.response import Response
from quickrecap_app.models import *

#-------------- FLASHCARD --------------#
def createFlashcard(json_data, actividad_id):
    print("Creating Flashcard..")
    try:
        data = json_data
        actividad = Actividad.objects.get(pk=actividad_id)
        
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

#-------------- QUIZ --------------#
def createQuiz(json_data, actividad_id):
    print("Creating Quiz..")
    try:
        data = json_data
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

#-------------- GAPS --------------#
def createGaps(json_data, actividad_id):
    print("Creating Gaps...")
    try:
        data = json_data
        actividad = Actividad.objects.get(pk=actividad_id)

        for gap_data in data['gaps']:
            gap_enunciado = GapEnunciado.objects.create(
                actividad=actividad,
                texto_completo=gap_data['texto_completo'],
                texto_con_huecos=gap_data['texto_con_huecos'],
                alternativas_incorrectas=json.dumps(gap_data['incorrectas'])
            )

            for respuesta_data in gap_data['respuestas']:
                gap_respuesta = GapRespuesta.objects.create(
                    gap_enunciado=gap_enunciado,
                    posicion=respuesta_data['posicion'],
                    opciones_correctas=','.join(respuesta_data['opciones_correctas'])
                )
                
    except Exception as e:
        print(f"Error al guardar la información: {e}")
        raise Exception("Error al procesar las oraciones con huecos")

    return Response(status=status.HTTP_200_OK)