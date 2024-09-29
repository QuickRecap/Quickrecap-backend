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
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=10, choices=[
        ('Flashcards', 'Flashcards'),
        ('Linkers', 'Linkers'),
        ('Gaps', 'Gaps'),
        ('Quiz', 'Quiz')
    ])
    actividad_preguntas = models.JSONField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    privado = models.BooleanField(default=False)
    tiempo_por_pregunta = models.IntegerField()
    numero_preguntas = models.IntegerField()
    veces_jugado = models.IntegerField(default=0)
    favorito = models.BooleanField(default=False)
    puntuacion_maxima = models.IntegerField(default=0)
    completado = models.BooleanField(default=False)

class Pregunta(models.Model):
    id = models.AutoField(primary_key=True)
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='preguntas')
    enunciado = models.TextField()
    opciones = models.JSONField()
    respuesta_correcta = models.IntegerField()

class Archivo(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    url = models.URLField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)