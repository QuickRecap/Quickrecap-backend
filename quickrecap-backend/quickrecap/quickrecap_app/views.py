import json

from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import NotFound

from django.contrib.auth import authenticate
from django.db.models import Q, F

from .serializers import *
from .models import *
from .utils.save_information import *
from .utils.pdf_processor import *
from .utils.gemini_api import *

# ---------- AUTHENTICATION ---------- #
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        actividades_completadas = Actividad.objects.filter(usuario=user.id, completado=True).count()
        actividades_generadas = Actividad.objects.filter(usuario=user.id).count()
        
        user_data = {
            'id': user.id,
            'profile_image': user.profile_image,
            'nombres': user.nombres,
            'apellidos': user.apellidos,
            'celular': user.celular,
            'genero': user.genero,
            'fecha_nacimiento': user.fecha_nacimiento,
            'email': user.email,
            'username': user.username,
            'puntos': user.puntos,
            'completadas': actividades_completadas,
            'generadas': actividades_generadas
        }
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data,
        })

class EstadisticasView(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        total_actividades = Actividad.objects.count()
        total_archivos = File.objects.count()
        total_usuarios = User.objects.count()
        
        data = {
            'total_actividades': total_actividades,
            'total_archivos': total_archivos,
            'total_usuarios': total_usuarios,
        }
        
        return Response(data)

class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = serializer.validated_data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except TokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        user_id = request.data.get('id')
        
        if not user_id:
            return Response({"id": "El ID del usuario es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar al usuario por el ID
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound("Usuario no encontrado.")

        # Validar los datos
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Verificar que la contraseña antigua sea correcta
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": "La contraseña actual es incorrecta."}, status=status.HTTP_400_BAD_REQUEST)

        # Cambiar la contraseña por la nueva
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"detail": "Contraseña cambiada exitosamente."}, status=status.HTTP_200_OK)

# ---------- REPORT ---------- #
class ReportCreateView(generics.CreateAPIView):
    queryset = ReporteError.objects.all()
    serializer_class = ReporteErrorSerializer
    
class ReportGetView(generics.ListAPIView):
    queryset = ReporteError.objects.all()
    serializer_class = ReportErrorListSerializer    

# ---------- USER ---------- #
class UserGetView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer

    def get_object(self):
        user_id = self.kwargs['pk']
        return User.objects.get(id=user_id)

class UserUpdatePointsView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdatePointsSerializer
    
    def get_object(self):
        user_id = self.kwargs['pk']
        return User.objects.get(id=user_id)
    
    def update(self, request, *args, **kwargs):
        actividad_id = request.data.get('actividad_id')
        partial = kwargs.pop('partial', False)
        
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        actividad = Actividad.objects.get(id=actividad_id)
        actividad.veces_jugado = F('veces_jugado') + 1
        actividad.save()

        if 'puntos' in request.data:
            new_points = request.data['puntos']
            instance.puntos = F('puntos') + new_points
            instance.save()
            instance.refresh_from_db()
            
            actividad = Actividad.objects.get(id=actividad_id)
            actividad.veces_jugado = F('veces_jugado') + 1
            actividad.save()
            actividad.refresh_from_db()
            
            serializer.data['puntos'] = instance.puntos
            serializer.data['veces_jugado'] = actividad.veces_jugado
        else:
            self.perform_update(serializer)
        return Response(serializer.data)

# ---------- ACTIVITIES ---------- #
def get_flashcards_data(actividad_flashcard_id):
    flashcards = Enunciado.objects.filter(actividad_id=actividad_flashcard_id)
    return [
        {'word': f.enunciado, 'definition': f.opcion_set.get(correcta=True).texto}
        for f in flashcards
    ]

def get_quiz_data(actividad_quiz_id):
    quiz = Actividad.objects.get(id=actividad_quiz_id)
    preguntas = Enunciado.objects.filter(actividad=quiz)
    return [
        {
            'question': pregunta.enunciado,
            'alternatives': [opcion.texto for opcion in pregunta.opcion_set.all()],
            'answer': [opcion.texto for opcion in pregunta.opcion_set.all()].index(pregunta.opcion_set.get(correcta=True).texto)
        }
        for pregunta in preguntas
    ]

def get_gaps_data(actividad_gaps_id):
    actividad = Actividad.objects.get(id=actividad_gaps_id)
    gap_enunciados = GapEnunciado.objects.filter(actividad=actividad)
    
    return [
        {
            'texto_completo': gap_enunciado.texto_completo,
            'texto_con_huecos': gap_enunciado.texto_con_huecos,
            'incorrectas': json.loads(gap_enunciado.alternativas_incorrectas),
            'respuestas': [
                {
                    'posicion': respuesta.posicion,
                    'opciones_correctas': respuesta.opciones_correctas.split(',')
                }
                for respuesta in gap_enunciado.gaprespuesta_set.all().order_by('posicion')
            ]
        }
        for gap_enunciado in gap_enunciados
    ]
    
def create_flashcard_activity(pdf_text, numero_preguntas, id):
    questions_flashcard = generate_questions_flashcard(pdf_text, numero_preguntas)
    createFlashcard(questions_flashcard, id)

class ActivityCreateView(generics.ListCreateAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActivityCreateSerializer

    def post(self, request):
        #Inicializar Datos
        data = request.data
        nombre_actividad = data.get('nombre')
        tipo_actividad = data.get('tipo_actividad').lower()
        numero_preguntas = data.get('numero_preguntas')
        tiempo_pregunta = data.get('tiempo_por_pregunta')
        
        #Obtener URL del PDF
        pdf_url = request.data.get('pdf_url')
        
        #Procesar PDF y convertir a JSON
        response = process_pdf_gemini(pdf_url)
        response_data = json.loads(response.content)
        pdf_text = response_data.get('pdf_text')
        
        # Crear la primera actividad según el tipo
        flashcard_activity = {
            'tipo_actividad': 'Flashcards',
            'tiempo_por_pregunta': data.get('tiempo_por_pregunta'),
            'numero_preguntas': data.get('numero_preguntas'),
            'usuario': data.get('usuario'),
            'nombre': data.get('nombre'),
        }
        
        #Serializar los resultados
        serializer_flashcard = self.get_serializer(data=flashcard_activity)
        serializer_flashcard.is_valid(raise_exception=True)
        actividad_flashcard = serializer_flashcard.save()
        
        # Update flashcard_id for Flashcard activity
        actividad_flashcard.flashcard_id = actividad_flashcard.id
        actividad_flashcard.save()
        
        #Crear actividad de flashcard
        create_flashcard_activity(pdf_text, numero_preguntas, actividad_flashcard.id)
        flashcards_data = get_flashcards_data(actividad_flashcard.id)
        
        id_quiz = actividad_flashcard.id
        
        #Actualizar response con la informacion de las flashcards
        response_data = {'flashcards': flashcards_data}
        
        if tipo_actividad.lower() == 'quiz':
            #Hacer una copia de request.data
            new_data = request.data.copy()
            
            # Añadir el parámetro 'flashcard_id' antes de serializar
            new_data['flashcard_id'] = actividad_flashcard.id
            actividad_flashcard.flashcard_id = None

            # Crear la actividad de quiz
            serializer_quiz = self.get_serializer(data=new_data)
            serializer_quiz.is_valid(raise_exception=True)
            actividad_quiz = serializer_quiz.save()
            actividad_flashcard.save()

            # Crear Quiz - 5.11seg
            questions_quiz = generate_questions_quiz(pdf_text, numero_preguntas)
            createQuiz(questions_quiz, actividad_quiz.id)
            
            #Obtener los datos del quiz creado
            quiz_data = get_quiz_data(actividad_quiz.id)
            id_quiz = actividad_quiz.id
            
            #Actualizar response con la informacion del quiz
            response_data['quiz'] = quiz_data
        
        if tipo_actividad.lower() == 'gaps':
            #Hacer una copia de request.data
            new_data = request.data.copy()
            
            # Añadir el parámetro 'flashcard_id' antes de serializar
            new_data['flashcard_id'] = actividad_flashcard.id
            actividad_flashcard.flashcard_id = None
            
            # Crear la actividad de gaps
            serializer_gaps = self.get_serializer(data=new_data)
            serializer_gaps.is_valid(raise_exception=True)
            actividad_gaps = serializer_gaps.save()
            actividad_gaps.save()
            actividad_flashcard.save()
            
            # Crear Gaps - #seg
            questions_quiz = generate_questions_gaps(pdf_text, numero_preguntas)
            createGaps(questions_quiz, actividad_gaps.id)
            
            #Obtener los datos del quiz creado
            quiz_data = get_gaps_data(actividad_gaps.id)
            id_quiz = actividad_gaps.id
            
            #Actualizar response con la informacion del quiz
            response_data['gaps'] = quiz_data
        
        if tipo_actividad.lower() == 'linkers':
            #Hacer una copia de request.data
            new_data = request.data.copy()
                  
            # Añadir el parámetro 'flashcard_id' antes de serializar
            new_data['flashcard_id'] = actividad_flashcard.id
            actividad_flashcard.flashcard_id = None
            
            # Crear la actividad de gaps
            serializer_gaps = self.get_serializer(data=new_data)
            serializer_gaps.is_valid(raise_exception=True)
            actividad_gaps = serializer_gaps.save()
            actividad_gaps.save()
            actividad_flashcard.save()
            
            #Guardado de actividad
            #--------- Logica para guardar la actividad ---------

            #Actualizar response con la informacion del quiz
            response_data['linkers'] = flashcards_data
        
        response_data['activity'] = {'id': id_quiz, 'nombre': nombre_actividad ,'numero_preguntas': numero_preguntas, 'tiempo_pregunta': tiempo_pregunta}
        return Response(response_data, status=status.HTTP_201_CREATED)

# -------- Crear Endpoint para retornar por tipo de actividad y por ID de actividad
#backend-quickrecap.com/activity/search?id=90
#backend-quickrecap.com/activity/search?tipo=Linkers order by veces jugado desc

class ActivitySearchByUserView(generics.ListAPIView):
    serializer_class = ActivityListSerializer

    def get_queryset(self):
        user_id = self.kwargs['pk']
        queryset = Actividad.objects.filter(usuario=user_id, flashcard_id__isnull=False)

        favorito = self.request.query_params.get('favorito', None)
        search = self.request.query_params.get('search', None)
        tipo = self.request.query_params.get('tipo', None)

        if favorito is not None:
            favorito_bool = favorito.lower() == 'true'
            queryset = queryset.filter(favorito=favorito_bool)
        
        if search is not None:
            queryset = queryset.filter(Q(nombre__icontains=search))
        
        if tipo is not None:
            if tipo == 'Todos':
                queryset = queryset
                return queryset
            else:
                queryset = queryset.filter(tipo_actividad=tipo)

        return queryset
    
class ActivityUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActivityListSerializer

    def get_object(self):
        actividad_id = self.kwargs['pk']
        return Actividad.objects.get(id=actividad_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
            
        return Response(serializer.data)

class ActivityDeleteView(generics.DestroyAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActivityListSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({"message": "Actividad eliminada correctamente"}, status=status.HTTP_204_NO_CONTENT)
        except Actividad.DoesNotExist:
            return Response({"error": "Actividad no encontrada"}, status=status.HTTP_404_NOT_FOUND)

# ---------- FAVORITOS ---------- #
class FavoritoListView(generics.ListAPIView):
    serializer_class = FavoritoListSerializer

    def get_queryset(self):
        queryset = Favoritos.objects.all()

        user_id = self.request.query_params.get('user', None)
        tipo = self.request.query_params.get('tipo', None)

        if user_id is not None:
            queryset = queryset.filter(user=user_id)
        
        if tipo is not None:
            if tipo == 'Todos':
                queryset = queryset
                return queryset
            else:
                queryset = queryset.filter(activity__tipo_actividad=tipo)

        return queryset

class FavoritoCreateView(generics.ListCreateAPIView):
    queryset = Favoritos.objects.all()
    serializer_class = FavoritoListSerializer

# ---------- RATED ---------- #
class RatedCreateView(generics.ListCreateAPIView):
    queryset = Rated.objects.all()
    serializer_class = RatedListSerializer
    
# ---------- ARCHIVO ---------- #
class FileGetByUserView(generics.ListAPIView):
    serializer_class = FileSerializer

    def get_queryset(self):
        user_id = self.kwargs['pk']
        return File.objects.filter(usuario=user_id)

class FileCreateView(generics.ListCreateAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    
class FileDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer