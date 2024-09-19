from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('report-error/', ReporteErrorView.as_view(), name='report-error'),
    path('edit-user/<int:pk>/', UserUpdateView.as_view(), name='edit-user')
]