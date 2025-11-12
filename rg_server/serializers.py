from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from rg_server.models import CommonUser

class CommonUserSerializer(serializers.ModelSerializer):
    """
    Serialize User informations
    """

    class Meta:
        model = CommonUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'scan_directory')
        read_only_fields = ('username', 'email')

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = None
    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh_token')
        if attrs['refresh']:
            return super().validate(attrs)
        else:
            raise InvalidToken('No valid token found in cookie \'refresh_token\'')
