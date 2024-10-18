from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MovieViewSet, AutorViewSet, RegisterView, LoginView, GenreViewSet, MovieDeleteView, MovieUpdateView, \
    documentation, manage_api_key, protected_api_view, CreateClientView, GetClientCountByUUIDView, \
    DeleteClientByUUIDView

router = DefaultRouter()
router.register(r'movie', MovieViewSet)

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('documentation', documentation.as_view(), name='documentation'),
    path('manage-api-key', manage_api_key, name='manage_api_key'),
    path('protected-api/', protected_api_view, name='protected_api'),
    path('create-client', CreateClientView.as_view(), name='create-client'),
    path('client-count/<uuid:uuid>', GetClientCountByUUIDView.as_view(), name='get-client-count'),
    path('delete-client/<str:uuid>', DeleteClientByUUIDView.as_view(), name='delete-client'),


    path('movies/get', MovieViewSet.as_view({"get": "list"})),
    path('movie/create', MovieViewSet.as_view({'post': 'create'})),
    path('movie/get/<int:pk>', MovieViewSet.as_view({'get': 'retrieve'})),
    path('movie/edit/<int:pk>', MovieUpdateView.as_view({"put": "update"})),
    path('movie/delete/<int:pk>', MovieDeleteView.as_view({"delete": "destroy"})),

    path('genres/get', GenreViewSet.as_view({"get": "list"})),
    path('genre/create', GenreViewSet.as_view({"post": "create"})),
    path('genre/get/<int:pk>', GenreViewSet.as_view({"get": "retrieve"})),
    path('genre/delete/<int:pk>', GenreViewSet.as_view({"delete": "destroy"})),


    path('authors/get', AutorViewSet.as_view({'get': 'list'})),
    path('author/create', AutorViewSet.as_view({'post': 'create'})),
    path('author/get/<int:pk>', AutorViewSet.as_view({'get': 'retrieve'}) ),
    path('author/delete/<int:pk>', AutorViewSet.as_view({'delete': 'destroy'})),
]