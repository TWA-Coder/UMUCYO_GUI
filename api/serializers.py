from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import Role, SoapRequestLog

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class SoapRequestLogSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = SoapRequestLog
        fields = '__all__'

class SoapExecuteSerializer(serializers.Serializer):
    """
    Generic serializer to validate inputs for SOAP operations.
    Inputs match the Kwargs expected by SoapClient methods.
    """
    id = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    # Flexible kwargs for other parameters
    payload = serializers.DictField(required=False, help_text="Additional parameters matching the method signature")

    def validate(self, attrs):
        # Additional validation if needed
        return attrs
