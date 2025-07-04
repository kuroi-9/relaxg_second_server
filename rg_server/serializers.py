from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model();

class UserSerializer(serializers.ModelSerializer):
    """
    Serialize User informations
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('username', 'email')
