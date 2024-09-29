from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    path('report/list', ReportGetView.as_view(), name='report-list'),
    path('report/create', ReportCreateView.as_view(), name='report-error'),
    
    path('user/list', UserGetView.as_view(), name='user-list'),
    path('user/update/<int:pk>', UserUpdateView.as_view(), name='edit-user'),
    
    path('archivo/search/<int:pk>', ArchivoGetByUser.as_view(), name='archivo-search'),
]