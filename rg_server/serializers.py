from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError
from django.utils.html import escape

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Escape user data
        attrs['username'] = escape(attrs['username'])

        # Custom validation
        if not attrs['username'].isalnum():
            raise ValidationError("The username can only contain letters and numbers.")
        if len(attrs['password']) < 6:
            raise ValidationError("The password must be at least 6 characters long.")

        # Call the parent class's validate method to authenticate the user
        data = super().validate(attrs)

        # Add additional information if necessary
        data['message'] = "Login successful. Tokens have been generated."

        return data
