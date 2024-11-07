from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    celular = models.CharField(max_length=15, null=True, blank=True)
    genero = models.CharField(max_length=10, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    puntos = models.IntegerField(default=0)
    
    profile_image = models.CharField(max_length=255, null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombres', 'apellidos']
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
    )

    def __str__(self):
        return self.nombres + self.apellidos

class ReporteError(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class Actividad(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_actividad = models.CharField(max_length=10, choices=[
        ('Flashcards', 'Flashcards'),
        ('Linkers', 'Linkers'),
        ('Gaps', 'Gaps'),
        ('Quiz', 'Quiz')
    ])
    tiempo_por_pregunta = models.IntegerField()
    numero_preguntas = models.IntegerField()
    veces_jugado = models.IntegerField(default=0)
    puntuacion_maxima = models.IntegerField(default=0)
    completado = models.BooleanField(default=False)
    privado = models.BooleanField(default=False)
    nombre = models.CharField(max_length=100)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    flashcard_id = models.IntegerField(null=True, blank=True)

class Favoritos(models.Model):
    id = models.AutoField(primary_key=True)
    activity = models.ForeignKey(Actividad, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Rated(models.Model):
    id = models.AutoField(primary_key=True)
    activity = models.ForeignKey(Actividad, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rate = models.IntegerField()
    commentary = models.TextField(null=True, blank=True)

class Historial(models.Model):
    id = models.AutoField(primary_key=True)
    activity = models.ForeignKey(Actividad, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    numero_preguntas = models.IntegerField()
    respuestas_correctas = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

class Enunciado(models.Model):
    id = models.AutoField(primary_key=True)
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE)
    enunciado = models.TextField()
    
class Opcion(models.Model):
    id = models.AutoField(primary_key=True)
    enun_id = models.ForeignKey(Enunciado, on_delete=models.CASCADE)
    texto = models.TextField()
    correcta = models.BooleanField(default=False)
    
# -------------- GAPS ACTIVITY -------------- #
class GapEnunciado(models.Model):
    id = models.AutoField(primary_key=True)
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE)
    texto_completo = models.TextField()
    texto_con_huecos = models.TextField()
    alternativas_incorrectas = models.TextField()

class GapRespuesta(models.Model):
    id = models.AutoField(primary_key=True)
    gap_enunciado = models.ForeignKey(GapEnunciado, on_delete=models.CASCADE)
    opciones_correctas = models.TextField()
    posicion = models.IntegerField()

class File(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    url = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)