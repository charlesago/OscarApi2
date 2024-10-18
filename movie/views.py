import hashlib

from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from rest_framework import viewsets, generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movie, Author, Genre, CustomUser, Client, GlobalApiKey
from .permissions import IsAuthenticatedAndEnabled, require_api_key
from .serializers import MovieSerializer, AuthorSerializer, RegisterSerializer, GenreSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser, login_url='/login/')
def manage_api_key(request):
    raw_key = None
    message = None

    if request.method == 'POST':
        name = request.POST.get('name')

        if 'send_email' in request.POST:
            raw_key = GlobalApiKey.generate_raw_key()
            hashed_key = GlobalApiKey.hash_key(raw_key)

            new_api_key = GlobalApiKey.objects.create(
                key=hashed_key,
                name=name,
                is_active=True
            )

            send_mail(
                'Votre Clé API',
                f'Voici votre clé API : {raw_key}\n Pour {name}  \n Utilisez-la pour accéder aux services.',
                'charles.agostinelli26@gmail.com',
                [request.user.email],
                fail_silently=False,
            )
            message = f"La clé API brute a été envoyée à {request.user.email}."

    return render(request, '../templates/manage_api_key.html', {'message': message})

@require_api_key
def protected_api_view(request):
    data = {
        'message': 'Vous avez accédé à une API protégée avec une clé API valide.'
    }
    return JsonResponse(data)

class CreateClientView(APIView):
    permission_classes = [IsAuthenticatedAndEnabled]

    def post(self, request):
        client_id = request.data.get('client_id')
        email = request.data.get('email')
        raw_api_key = request.data.get('api_key')  # Clé API brute
        count = request.data.get('count', 1000)
        uuid = request.data.get('uuid')

        # Vérifier si le client existe déjà
        if Client.objects.filter(client_id=client_id).exists():
            return Response({"error": "Client déjà enregistré"}, status=status.HTTP_400_BAD_REQUEST)

        # Hacher la clé API brute avant de l'enregistrer
        hashed_api_key = hashlib.sha256(raw_api_key.encode('utf-8')).hexdigest()

        # Créer un nouveau client avec la clé API hachée
        new_client = Client(client_id=client_id, email=email, api_key=hashed_api_key, count=count, uuid=uuid)
        new_client.save()

        return Response({
            "message": "Client créé avec succès",
            "client_id": new_client.client_id,
            "email": new_client.email,
            "api_key": hashed_api_key,  # Renvoie la clé hachée
            "count": new_client.count,
            "uuid": new_client.uuid
        }, status=status.HTTP_201_CREATED)
class GetClientCountByUUIDView(APIView):
    permission_classes = [IsAuthenticatedAndEnabled]
    def get(self, request, uuid):
        client = get_object_or_404(Client, uuid=uuid)

        return Response({'count': client.count}, status=status.HTTP_200_OK)


class DeleteClientByUUIDView(APIView):

    def delete(self, request, uuid):
        # Cherche le client par son UUID
        client = get_object_or_404(Client, uuid=uuid)

        # Supprime le client
        client.delete()

        # Renvoie une réponse avec un statut HTTP 200
        return Response({'message': 'Client supprimé avec succès.'}, status=status.HTTP_200_OK)


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticatedAndEnabled]
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class documentation(TemplateView):
     template_name = "../templates/documentation.html"

class MovieUpdateView(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticatedAndEnabled]
    def perform_update(self, serializer):
        movie = self.get_object()
        if movie.creator != self.request.user:
            raise PermissionDenied("Vous n'avez pas la permission d'éditer ce film")
        serializer.save()


class MovieDeleteView(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticatedAndEnabled]
    def perform_destroy(self, serializer):
        movie = self.get_object()
        if movie.creator != self.request.user:
            raise PermissionDenied("Vous n'avez pas la permission de supprimer ce film")
        serializer.save()


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticatedAndEnabled]

class AutorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedAndEnabled]


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class LoginView(generics.GenericAPIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid Credentials'}, status=400)