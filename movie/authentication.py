import hashlib
import logging
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from movie.models import GlobalApiKey, Client

logger = logging.getLogger(__name__)

class PlatformApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        logger.debug(f"Tous les en-têtes reçus par la plateforme : {request.headers}")
        logger.debug(f"En-têtes META pour la plateforme : {request.META}")

        api_key = request.headers.get('API-Key-Plat') or request.META.get('HTTP_API_KEY_PLAT')

        if not api_key:
            logger.debug("Aucune clé API fournie pour la plateforme.")
            return None

        hashed_key = hashlib.sha256(api_key.encode('utf-8')).hexdigest()
        logger.debug(f"Clé API brute hachée pour la plateforme : {hashed_key}")

        try:
            valid_key = GlobalApiKey.objects.get(key=hashed_key, is_active=True)
            logger.debug(f"Clé API valide pour la plateforme : {api_key}")
        except GlobalApiKey.DoesNotExist:
            logger.debug(f"Clé API invalide ou inactive pour la plateforme : {api_key}")
            raise AuthenticationFailed('Clé API invalide ou inactive pour la plateforme.')

        return (None, None)


class ClientApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        logger.debug(f"Tous les en-têtes reçus par le client : {request.headers}")

        api_key = request.headers.get('apikey') or request.META.get('HTTP_APIKEY')

        if not api_key:
            logger.debug("Aucune clé API fournie pour le client.")
            raise AuthenticationFailed('Clé API non fournie pour le client.')

        logger.debug(f"Clé API brute reçue pour le client : {api_key}")

        hashed_key = hashlib.sha256(api_key.encode('utf-8')).hexdigest()
        logger.debug(f"Clé API brute hachée pour le client : {hashed_key}")

        try:
            client = Client.objects.get(api_key=hashed_key, is_active=True)
            logger.debug(f"Clé API valide pour le client : {api_key}")
        except Client.DoesNotExist:
            logger.debug(f"Clé API du client invalide ou inactive : {api_key}")
            raise AuthenticationFailed('Clé API invalide ou inactive pour le client.')

        if client.count <= 0:
            logger.debug(f"Le client {client.email} a épuisé ses requêtes. Désactivation de la clé.")
            client.is_active = False
            client.save()
            raise AuthenticationFailed('Votre compte a épuisé son nombre de requêtes.')

        logger.debug(f"Le client {client.email} a encore {client.count} requêtes disponibles.")

        client.count -= 1
        client.save()

        logger.debug(f"Le compteur de requêtes du client {client.email} a été décrémenté à {client.count}.")

        return (None, None)