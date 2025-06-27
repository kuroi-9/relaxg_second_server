from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated # Importez cette classe de permission
from rest_framework import status

# --- Exemple de Vue Protégée ---
class ProtectedHelloView(APIView):
    # Ceci est la clé : seules les requêtes authentifiées seront autorisées
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Si la requête arrive ici, c'est que l'utilisateur est authentifié.
        # request.user contiendra l'instance de l'utilisateur authentifié.
        return Response({"message": f"Bonjour, {request.user.username} ! Vous êtes authentifié et avez accès à cette ressource protégée."})

    def post(self, request, *args, **kwargs):
        data = request.data.get('data_sent', 'aucune donnée')
        return Response({
            "message": f"Salut, {request.user.username}! Vous avez envoyé : {data}. C'est une ressource POST protégée.",
            "received_data": data
        }, status=status.HTTP_200_OK)


# --- Exemple de Vue NON Protégée (si vous en aviez besoin) ---
class PublicHelloView(APIView):
    # Pas de 'permission_classes' signifie que tout le monde peut y accéder par défaut
    # ou selon la DEFAULT_PERMISSION_CLASSES de settings.py.
    # Pour s'assurer qu'elle est publique même si DEFAULT_PERMISSION_CLASSES est IsAuthenticated:
    # permission_classes = [] # Liste vide pour supprimer toute permission par défaut
    # OU
    # permission_classes = [AllowAny] # Explicitement autoriser tout le monde
    def get(self, request, *args, **kwargs):
        return Response({"message": "Bonjour à tous ! Ceci est une ressource publique."})
