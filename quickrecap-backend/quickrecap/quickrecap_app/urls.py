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
    path('user/addpoints/<int:pk>', UserUpdatePointsView.as_view(), name='user-points'),
    path('user/estadistics/<int:pk>', EstadisticasByUser.as_view(), name='user-estadistics'),

    path('file/search/<int:pk>', FileGetByUserView.as_view(), name='archivo-search'),
    path('file/create', FileCreateView.as_view(), name='archivo-create'),
    path('file/delete/<int:pk>', FileDeleteView.as_view(), name='archivo-delete'),
    
    path('activity/research', ActivitySearchView.as_view(), name='activity-search'),
    path('activity/search/<int:pk>', ActivitySearchByUserView.as_view(), name='activity-search-user'),
    path('activity/create', ActivityCreateView.as_view(), name='activity-create'),
    path('activity/update/<int:pk>', ActivityUpdateView.as_view(), name='activity-update'),
    path('activity/delete/<int:pk>', ActivityDeleteView.as_view(), name='activity-delete'),
    
    path('favorite/list', FavoritoListView.as_view(), name='favorite-list'),
    path('favorite/create', FavoritoCreateView.as_view(), name='favorite-create'),
    path('favorite/update/<int:pk>', ActivityFavoriteView.as_view(), name='favorite-update'),
    
    path('rated/create', RatedCreateView.as_view(), name='favorite-create'),
    
    path('home/list', EstadisticasView.as_view(), name='home-list'),
    
    path('historial/list/<int:pk>', HistorialListView.as_view(), name='historial-list'),
    path('historial/create', HistorialCreateView.as_view(), name='historial-create'),
]