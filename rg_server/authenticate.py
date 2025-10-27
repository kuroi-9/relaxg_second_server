from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from rest_framework import exceptions

from rg_server.models import CommonUser


class EmailAuthBackend:
    def authenticate(self, request, username=None, password=None):
        user = CommonUser.objects.get(email=username)
        if not user.is_active:
            raise exceptions.AuthenticationFailed("User account is disabled.")

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return CommonUser.objects.get(pk=user_id)
        except CommonUser.DoesNotExist:
            return None


class JWTCookieAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header:
            raw_token = self.get_raw_token(header)
        else:
            # If no header, try to get the token from the cookie
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])

        if raw_token is None:
            return None  # No token found, authentication fails here

        # If no raw_token is found, return None
        if raw_token is None:
            return None  # No token found, authentication fails here

        # If a raw_token is found, validate it
        try:
            validated_token = self.get_validated_token(raw_token)
        except Exception as e:
            # Handle invalid or expired tokens
            # You can log the error or propagate it if you want a different behavior for invalid tokens
            # By default, JWTAuthentication raises exceptions like InvalidToken, TokenExpired, etc.
            # that DRF transforms into 401.
            print(f"Token validation failed: {e}")
            raise exceptions.AuthenticationFailed(
                "Invalid token."
            )  # Or let the exception propagate

        # If the token is validated, retrieve the user
        user = self.get_user(validated_token)
        return user, validated_token
