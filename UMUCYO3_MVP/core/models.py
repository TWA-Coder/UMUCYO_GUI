from django.db import models
from django.contrib.auth.models import User

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class RoleOperation(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='operations')
    operation_name = models.CharField(max_length=255, help_text="Exact name of the SOAP operation")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('role', 'operation_name')

    def __str__(self):
        return f"{self.role.name} -> {self.operation_name}"

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

class SoapRequestLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    operation = models.CharField(max_length=255)
    request_payload = models.TextField(help_text="Raw XML or JSON request")
    response_payload = models.TextField(help_text="Raw XML or JSON response", null=True, blank=True)
    status = models.CharField(max_length=50) # e.g., 'SUCCESS', 'FAILED'
    duration = models.FloatField(help_text="Duration in seconds")
    timestamp = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.operation} - {self.status} at {self.timestamp}"
