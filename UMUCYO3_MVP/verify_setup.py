import os
import django
import sys

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umucyo_mvp.settings')
django.setup()

try:
    from services.soap_client import SoapClient
    from core.models import SoapRequestLog, Role, UserRole
    print("Imports successful")
    
    # Check if WSDL exists
    if not os.path.exists('service.wsdl'):
        print("WARNING: service.wsdl not found in current directory")
    
    # Initialize client (will parse WSDL)
    client = SoapClient(wsdl_path='service.wsdl')
    print("Client initialized successfully")
    
    # Check models
    print(f"SoapRequestLog count: {SoapRequestLog.objects.count()}")
    
except Exception as e:
    print(f"Verification FAILED: {e}")
    sys.exit(1)
