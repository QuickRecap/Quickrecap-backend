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
    
    path('file/search/<int:pk>', FileGetByUserView.as_view(), name='archivo-search'),
    path('file/create', FileCreateView.as_view(), name='archivo-create'),
    path('file/delete/<int:pk>', FileDeleteView.as_view(), name='archivo-delete'),
    
    path('activity/search/<int:pk>', ActivitySearchByUserView.as_view(), name='activity-search'),
    path('activity/create', ActivityCreateView.as_view(), name='activity-create'),
    path('activity/update/<int:pk>', ActivityUpdateView.as_view(), name='activity-update'),
]