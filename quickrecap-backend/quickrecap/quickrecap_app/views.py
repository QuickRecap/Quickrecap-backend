import json

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import NotFound

from django.contrib.auth import authenticate

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
        }
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data
        })

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
    serializer_class = UserSerializer

    def get_object(self):
        user_id = self.kwargs['pk']
        return User.objects.get(id=user_id)

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
            'nombre': data.get('nombre')
        }
        
        #Serializar los resultados
        serializer_flashcard = self.get_serializer(data=flashcard_activity)
        serializer_flashcard.is_valid(raise_exception=True)
        actividad_flashcard = serializer_flashcard.save()
        
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
            
            # Crear la actividad de quiz
            serializer_quiz = self.get_serializer(data=new_data)
            serializer_quiz.is_valid(raise_exception=True)
            actividad_quiz = serializer_quiz.save()

            # Crear Quiz - 5.11seg
            questions_quiz = generate_questions_quiz(pdf_text, numero_preguntas)
            createQuiz(questions_quiz, actividad_quiz.id)
            
            #Obtener los datos del quiz creado
            quiz_data = get_quiz_data(actividad_quiz.id)
            
            id_quiz = actividad_quiz.id
            
            #Actualizar response con la informacion del quiz
            response_data['quiz'] = quiz_data

        response_data['activity'] = {'id': id_quiz, 'nombre': nombre_actividad ,'numero_preguntas': numero_preguntas, 'tiempo_pregunta': tiempo_pregunta}
        return Response(response_data, status=status.HTTP_201_CREATED)

class ActivitySearchByUserView(generics.ListAPIView):
    serializer_class = ActivityListSerializer

    def get_queryset(self):
        user_id = self.kwargs['pk']
        return Actividad.objects.filter(usuario=user_id)
    
class ActivityUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActivityListSerializer

    def get_object(self):
        actividad_id = self.kwargs['pk']
        return Actividad.objects.get(id=actividad_id)
    
# ---------- PREGUNTA ----------- #

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