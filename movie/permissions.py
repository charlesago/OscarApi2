import hashlib

from django.http import JsonResponse
from rest_framework.permissions import BasePermission

from movie.models import GlobalApiKey, Client

import logging

logger = logging.getLogger(__name__)

def require_api_key(view_func):
    def wrapped_view(request, *args, **kwargs):
        raw_api_key = request.headers.get('API-Key')

        if not raw_api_key:
            return JsonResponse({'error': 'Clé API manquante.'}, status=401)

        hashed_key = GlobalApiKey.hash_key(raw_api_key)

        try:
            valid_key = GlobalApiKey.objects.get(key=hashed_key, is_active=True)
        except GlobalApiKey.DoesNotExist:
            return JsonResponse({'error': 'Clé API invalide ou inactive.'}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapped_view


class IsAuthenticatedAndEnabled(BasePermission):

    def has_permission(self, request, view):
        logger.debug("Vérification des permissions pour l'accès via clé API.")

        api_key_platform = request.headers.get('API-Key-Plat')
        if api_key_platform:
            logger.debug(f"Clé API brute reçue pour la plateforme : {api_key_platform}")
            hashed_key = hashlib.sha256(api_key_platform.encode('utf-8')).hexdigest()
            if GlobalApiKey.objects.filter(key=hashed_key, is_active=True).exists():
                logger.debug("Clé API valide pour la plateforme.")
                return True

        api_key_client = request.headers.get('apikey')
        if api_key_client:
            logger.debug(f"Clé API brute reçue pour le client : {api_key_client}")
            hashed_key = hashlib.sha256(api_key_client.encode('utf-8')).hexdigest()
            if Client.objects.filter(api_key=hashed_key, is_active=True).exists():
                logger.debug("Clé API valide pour le client.")
                return True

        logger.debug("Aucune méthode d'authentification valide trouvée.")
        return False
