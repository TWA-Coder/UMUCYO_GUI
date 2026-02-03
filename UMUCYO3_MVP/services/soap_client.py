import logging
import json
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime
import time

from django.conf import settings
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder

import zeep
from zeep import Client, Settings, xsd
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin
from zeep.helpers import serialize_object
from requests import Session
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from core.models import SoapRequestLog
from services.decorators import require_soap_permission

# Configuration (Could be moved to settings.py)
WSDL_PATH = getattr(settings, 'SOAP_WSDL_PATH', 'service.wsdl')
SOAP_TIMEOUT = getattr(settings, 'SOAP_TIMEOUT', 30)
SOAP_RETRIES = getattr(settings, 'SOAP_RETRIES', 3)

logger = logging.getLogger(__name__)

# --- Data Structures ---

@dataclass
class TenderInfo:
    ref_name: str
    ref_number: str
    pe_name: Optional[str] = None
    deadline_date: Optional[str] = None
    # Add other fields as needed

@dataclass
class OperationResult:
    result_code: str
    result_message: str
    raw_response: Optional[Dict[str, Any]] = None

# --- Client ---

class SoapClient:
    def __init__(self, wsdl_path: str = WSDL_PATH):
        self.wsdl_path = wsdl_path
        self.history = HistoryPlugin()
        self.client = self._init_client()

    def _init_client(self) -> Client:
        session = Session()
        retry = Retry(
            total=SOAP_RETRIES,
            read=SOAP_RETRIES,
            connect=SOAP_RETRIES,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 504)
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        transport = Transport(session=session, timeout=SOAP_TIMEOUT)
        settings = Settings(strict=False, xml_huge_tree=True)
        
        client = Client(self.wsdl_path, transport=transport, settings=settings, plugins=[self.history])
        
        # --- HARDCODE IP FIX ---
        # Force use of IP address to bypass DNS failure on Render
        new_address = 'http://197.243.17.15:8084/roneps-hub/services/GuaranteeDocumentService.GuaranteeDocumentServiceHttpSoap11Endpoint/'
        if client.service:
             # Zeep service objects proxy the binding. We need to set the address on the binding.
             # This is a bit internal to Zeep but effective.
             # Standard way: client.create_service(binding_name, address)
             pass 

        # A more robust way in Zeep involves creating a new service proxy with the specific address
        # But since we use the default service, we can just patch the transport/wsdl or create service explicitly.
        
        # Let's use the create_service method if we know the binding name from WSDL.
        # From previous file view: Binding name is 'GuaranteeDocumentServiceSoap11Binding'
        # PortType is GuaranteeDocumentServicePortType.
        # Service name is GuaranteeDocumentService.
        
        binding_name = '{http://security.service.hub.roneps.minecofin.rw}GuaranteeDocumentServiceSoap11Binding'
        service_name = '{http://security.service.hub.roneps.minecofin.rw}GuaranteeDocumentService'
        
        # However, the simplest way often acts on the default service. 
        # let's try to overwrite the location which Zeep uses.
        for service in client.wsdl.services.values():
            for port in service.ports.values():
                if 'umucyo.gov.rw' in port.binding_options.get('address', ''):
                    port.binding_options['address'] = port.binding_options['address'].replace('umucyo.gov.rw', '197.243.17.15')
                    
        return client

    def _log_request(self, operation: str, request_data: Dict, start_time: float, result=None, error=None, user=None):
        duration = time.time() - start_time
        status = 'SUCCESS' if not error else 'FAILED'
        
        # Serialize payloads
        # Serialize payloads
        try:
            req_payload = json.dumps(serialize_object(request_data), cls=DjangoJSONEncoder)
        except Exception:
            req_payload = str(request_data)
        
        # Capture RAW XML if available
        try:
            if self.history.last_sent:
                req_payload = str(self.history.last_sent['envelope'])
        except Exception:
            pass

        try:
            res_payload = json.dumps(serialize_object(result), cls=DjangoJSONEncoder) if result else None
        except Exception:
            res_payload = str(result)
            
        # Capture RAW XML Response if available
        try:
            if self.history.last_received:
                res_payload = str(self.history.last_received['envelope'])
        except Exception:
             pass

        error_msg = str(error) if error else None

        # We assume usage inside a request context usually, implying request.user might be available differently.
        # But this is a backend service. User need to be passed or context var used.
        # For MVP, we stick to system logging or pass user in 'auth' dict if needed.
        # Here we just log.
        
        try:
            SoapRequestLog.objects.create(
                user=user,
                operation=operation,
                request_payload=req_payload,
                response_payload=res_payload,
                status=status,
                duration=duration,
                error_message=error_msg
            )
        except Exception as e:
            logger.error(f"Failed to write SOAP log: {e}")

    def call_operation(self, operation_name: str, user=None, **kwargs) -> Any:
        # --- MOCK OVERRIDE ---
        # Allow 'getTenderInformation' to pass through for testing
        if getattr(settings, 'MOCK_SOAP_API', True):
            start_time = time.time()
            mock_response = {
                "status": "MOCK_SUCCESS",
                "message": f"Operation '{operation_name}' mocked successfully.",
                "data": {
                    "mock_id": "12345",
                    "timestamp": datetime.now().isoformat(),
                    "input_received": kwargs
                }
            }
            # Log the mock request so dashboard visibility is maintained
            self._log_request(operation_name, kwargs, start_time, result=mock_response, user=user)
            return mock_response
        # ---------------------

        service_method = getattr(self.client.service, operation_name)
        start_time = time.time()
        try:
            response = service_method(**kwargs)
            self._log_request(operation_name, kwargs, start_time, result=response, user=user)
            return response
        except Exception as e:
            self._log_request(operation_name, kwargs, start_time, error=e, user=user)
            logger.error(f"SOAP Error in {operation_name}: {e}")
            # Guardrail: Return safe error dict instead of crashing
            return {
                "success": False,
                "error": str(e),
                "user_message": "External SOAP Service is currently unavailable. Please try again later."
            }

    # --- Operations ---

    @require_soap_permission('getTenderInformation')
    def get_tender_information(self, id_val: str, password: str, ref_name: str, ref_number: str, user=None):
        payload = {
            'tenderInfoRequest': {
                'id': id_val,
                'password': password,
                'tenderRefName': ref_name,
                'tenderRefNumber': ref_number
            }
        }
        # Zeep unwraps the first element usually, but let's see WSDL.
        # getTenderInformation wrapper takes 'tenderInfoRequest'.
        return self.call_operation('getTenderInformation', user=user, **payload)

    @require_soap_permission('sendAdvancePaymentInformation')
    def send_advance_payment_information(self, id_val: str, password: str, payment_info: Dict, user=None):
        """
        payment_info structure should match AdvancePaymentInfoRequest schema.
        We expect caller to structure the dict or we can build helpers.
        For MVP, we pass the dict constructed by caller but ensure auth is injected.
        """
        payment_info['id'] = id_val
        payment_info['password'] = password
        payload = {'advancePaymentInfoRequest': payment_info}
        return self.call_operation('sendAdvancePaymentInformation', user=user, **payload)

    @require_soap_permission('sendBidSecurityInformation')
    def send_bid_security_information(self, id_val: str, password: str, bid_info: Dict, user=None):
        bid_info['id'] = id_val
        bid_info['password'] = password
        payload = {'bidSecurityInfoRequest': bid_info}
        return self.call_operation('sendBidSecurityInformation', user=user, **payload)

    @require_soap_permission('getContractInformation')
    def get_contract_information(self, id_val: str, password: str, contract_number: str, serial_number: str, user=None):
        data = {
            'id': id_val,
            'password': password,
            'contractNumber': contract_number,
            'contractSerialNumber': serial_number
        }
        payload = {'contractInfoRequest': data}
        return self.call_operation('getContractInformation', user=user, **payload)

    @require_soap_permission('sendCreditLineFacility')
    def send_credit_line_facility(self, id_val: str, password: str, credit_info: Dict, user=None):
        credit_info['id'] = id_val
        credit_info['password'] = password
        payload = {'creditLineFacilityRequest': credit_info}
        return self.call_operation('sendCreditLineFacility', user=user, **payload)

    @require_soap_permission('sendPerformSecurityInformation')
    def send_perform_security_information(self, id_val: str, password: str, perform_info: Dict, user=None):
        perform_info['id'] = id_val
        perform_info['password'] = password
        payload = {'performanceSecurityInfoRequest': perform_info}
        return self.call_operation('sendPerformSecurityInformation', user=user, **payload)
