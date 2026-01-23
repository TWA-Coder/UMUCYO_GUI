from rest_framework import viewsets, status, views
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions

from django.contrib.auth.models import User
from core.models import Role, SoapRequestLog
from api.serializers import UserSerializer, RoleSerializer, SoapRequestLogSerializer, SoapExecuteSerializer
from services.soap_client import SoapClient

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class LogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SoapRequestLog.objects.all().order_by('-timestamp')
    serializer_class = SoapRequestLogSerializer

class SoapViewSet(viewsets.ViewSet):
    """
    Gateway to SOAP Operations.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """List available SOAP operations."""
        # Hardcoded list or introspection of SoapClient
        operations = [
            'getTenderInformation',
            'sendAdvancePaymentInformation',
            'sendBidSecurityInformation',
            'getContractInformation',
            'sendCreditLineFacility',
            'sendPerformSecurityInformation',
        ]
        return Response({'operations': operations})

    @action(detail=False, methods=['post'], url_path='execute/(?P<operation>[^/.]+)')
    def execute_operation(self, request, operation=None):
        """
        Execute a SOAP operation.
        URL: /api/soap/execute/<operationName>/
        Body: JSON payload (id, password, other args...)
        """
        # 1. Map URL operation name to Python method name
        # Convention: camelCase matches direct method calls in our client wrapper?
        # Our SoapClient methods are snake_case: get_tender_information
        # But decorators track camelCase: getTenderInformation
        # Let's map manually or strict snake_case.
        
        # Simple mapper for safety
        method_map = {
            'getTenderInformation': 'get_tender_information',
            'sendAdvancePaymentInformation': 'send_advance_payment_information',
            'sendBidSecurityInformation': 'send_bid_security_information',
            'getContractInformation': 'get_contract_information',
            'sendCreditLineFacility': 'send_credit_line_facility',
            'sendPerformSecurityInformation': 'send_perform_security_information',
        }
        
        if operation not in method_map:
            return Response({'error': f"Unknown operation '{operation}'"}, status=status.HTTP_400_BAD_REQUEST)
        
        method_name = method_map[operation]
        
        # 2. Instantiate Client
        client = SoapClient()
        
        # 3. Call Method
        try:
            # We pass request.data as kwargs directly?
            # Our Client methods have specific signatures e.g. (id_val, password, ref_name...)
            # The client expects `user` in kwargs for permission check.
            
            kwargs = request.data.copy()
            # Rename 'id' to 'id_val' if present in data, to match python arg
            if 'id' in kwargs:
                kwargs['id_val'] = kwargs.pop('id')
            
            # Pass user
            method = getattr(client, method_name)
            result = method(user=request.user, **kwargs)
            
            # Result might be a Zeep object, need serialization
            from zeep.helpers import serialize_object
            return Response(serialize_object(result))
            
        except TypeError as e:
            return Response({'error': f"Invalid arguments: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # PermissionError or SOAP Fault
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
