from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated # Import this permission class
from rest_framework import status

# --- Example of a Protected View ---
class ProtectedHelloView(APIView):
    # This is the key: only authenticated requests will be allowed
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # If the request reaches here, the user is authenticated.
        # request.user will contain the instance of the authenticated user.
        return Response({"message": f"Hello, {request.user.username}! You are authenticated and have access to this protected resource."})

    def post(self, request, *args, **kwargs):
        data = request.data.get('data_sent', 'no data')
        return Response({
            "message": f"Hi, {request.user.username}! You sent: {data}. This is a protected POST resource.",
            "received_data": data
        }, status=status.HTTP_200_OK)


# --- Example of a NON-Protected View (if needed) ---
class PublicHelloView(APIView):
    # No 'permission_classes' means everyone can access it by default
    # or according to the DEFAULT_PERMISSION_CLASSES in settings.py.
    # To ensure it is public even if DEFAULT_PERMISSION_CLASSES is IsAuthenticated:
    # permission_classes = [] # Empty list to remove any default permissions
    # OR
    # permission_classes = [AllowAny] # Explicitly allow everyone
    def get(self, request, *args, **kwargs):
        return Response({"message": "Hello everyone! This is a public resource."})
