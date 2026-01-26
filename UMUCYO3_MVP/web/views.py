from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template.loader import render_to_string
import json
from zeep.helpers import serialize_object
from services.soap_client import SoapClient
from core.models import SoapRequestLog

class CustomLoginView(LoginView):
    template_name = 'web/login.html'

class DashboardView(LoginRequiredMixin, ListView):
    model = SoapRequestLog
    template_name = 'web/dashboard.html'
    context_object_name = 'logs'
    ordering = ['-timestamp']
    paginate_by = 20

class OperationListView(LoginRequiredMixin, TemplateView):
    template_name = 'web/operation_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['operations'] = [
            'getTenderInformation',
            'sendAdvancePaymentInformation',
            'sendBidSecurityInformation',
            'getContractInformation',
            'sendCreditLineFacility',
            'sendPerformSecurityInformation',
        ]
        return context

class OperationExecuteView(LoginRequiredMixin, View):
    template_name = 'web/operation_form.html'
    
    # Metadata for fields. In a real app, this could be introspected or config-driven.
    FIELD_CONFIG = {
        'getTenderInformation': [
            {'name': 'ref_name', 'label': 'Tender Ref Name', 'required': True},
            {'name': 'ref_number', 'label': 'Tender Ref Number', 'required': True},
        ],
        'getContractInformation': [
             {'name': 'contract_number', 'label': 'Contract Number', 'required': True},
             {'name': 'contract_serial_number', 'label': 'Contract Serial Number', 'required': True},
        ],
        'sendAdvancePaymentInformation': [
            # Top Level
            {'name': 'contractName', 'label': 'Contract Name'},
            {'name': 'contractNumber', 'label': 'Contract Number'},
            {'name': 'contractSerialNumber', 'label': 'Contract Serial Number'},
            {'name': 'contractDate', 'label': 'Contract Date (YYYY-MM-DD)'},
            # AdvancePaymentInfo
            {'name': 'advancePaymentInfo__accountNumber', 'label': 'Account Number'},
            {'name': 'advancePaymentInfo__address', 'label': 'Address'},
            {'name': 'advancePaymentInfo__amount', 'label': 'Amount'},
            {'name': 'advancePaymentInfo__amountCharacter', 'label': 'Amount (Words)'},
            {'name': 'advancePaymentInfo__expireDate', 'label': 'Expire Date (YYYY-MM-DD)'},
            {'name': 'advancePaymentInfo__guaranteeNumber', 'label': 'Guarantee Number'},
            {'name': 'advancePaymentInfo__issueDate', 'label': 'Issue Date (YYYY-MM-DD)'},
            {'name': 'advancePaymentInfo__name', 'label': 'Beneficiary Name'},
            {'name': 'advancePaymentInfo__position', 'label': 'Position'},
            {'name': 'advancePaymentInfo__startDate', 'label': 'Start Date (YYYY-MM-DD)'},
            {'name': 'advancePaymentInfo__status', 'label': 'Status'},
            {'name': 'advancePaymentInfo__unit', 'label': 'Currency Unit'},
            # IssueBankInfo
            {'name': 'issueBankInfo__bankName', 'label': 'Bank Name'},
            {'name': 'issueBankInfo__bankBranchName', 'label': 'Bank Branch Name'},
            {'name': 'issueBankInfo__bankTINNumber', 'label': 'Bank TIN'},
            {'name': 'issueBankInfo__branchAddress', 'label': 'Branch Address'},
            {'name': 'issueBankInfo__branchManagerName', 'label': 'Branch Manager Name'},
            {'name': 'issueBankInfo__securityRepresentiveName', 'label': 'Security Rep Name'},
            {'name': 'issueBankInfo__telNumber', 'label': 'Tel Number'},
            {'name': 'issueBankInfo__faxNumber', 'label': 'Update Fax Number'},
            {'name': 'issueBankInfo__email', 'label': 'Email'},
            {'name': 'issueBankInfo__comment', 'label': 'Comment'},
            # ProcuringEntityInfo
            {'name': 'procuringEnityInfo__pEName', 'label': 'PE Name'},
            {'name': 'procuringEnityInfo__pETINNumber', 'label': 'PE TIN'},
            {'name': 'procuringEnityInfo__addressPE', 'label': 'PE Address'},
            {'name': 'procuringEnityInfo__chargerNameInPE', 'label': 'PE Charger Name'},
            # SupplierInfo
            {'name': 'supplierInfo__supplierName', 'label': 'Supplier Name'},
            {'name': 'supplierInfo__supplierTINNumber', 'label': 'Supplier TIN'},
            {'name': 'supplierInfo__addressSupplier', 'label': 'Supplier Address'},
            {'name': 'supplierInfo__supplierRepresentiveName', 'label': 'Supplier Rep Name'},
        ],
        'sendBidSecurityInformation': [
            # BidSecurityInfo
            {'name': 'bidSecurityInfo__amount', 'label': 'Amount'},
            {'name': 'bidSecurityInfo__amountCharacter', 'label': 'Amount (Words)'},
            {'name': 'bidSecurityInfo__expireDate', 'label': 'Expire Date (YYYY-MM-DD)'},
            {'name': 'bidSecurityInfo__securityName', 'label': 'Security Name'},
            {'name': 'bidSecurityInfo__securityNumber', 'label': 'Security Number'},
            {'name': 'bidSecurityInfo__startDate', 'label': 'Start Date (YYYY-MM-DD)'},
            {'name': 'bidSecurityInfo__status', 'label': 'Status'},
            {'name': 'bidSecurityInfo__unit', 'label': 'Currency Unit'},
             # IssueBankInfo (Reused fields usually, but defined explicitly per op for clarity)
            {'name': 'issueBankInfo__bankName', 'label': 'Bank Name'},
            {'name': 'issueBankInfo__bankBranchName', 'label': 'Bank Branch Name'},
            {'name': 'issueBankInfo__bankTINNumber', 'label': 'Bank TIN'},
            {'name': 'issueBankInfo__branchAddress', 'label': 'Branch Address'},
            {'name': 'issueBankInfo__branchManagerName', 'label': 'Branch Manager Name'},
            {'name': 'issueBankInfo__securityRepresentiveName', 'label': 'Security Rep Name'},
            {'name': 'issueBankInfo__telNumber', 'label': 'Tel Number'},
            {'name': 'issueBankInfo__faxNumber', 'label': 'Fax Number'},
            {'name': 'issueBankInfo__email', 'label': 'Email'},
            {'name': 'issueBankInfo__comment', 'label': 'Comment'},
            # SupplierInfo
            {'name': 'supplierInfo__supplierName', 'label': 'Supplier Name'},
            {'name': 'supplierInfo__supplierTINNumber', 'label': 'Supplier TIN'},
            {'name': 'supplierInfo__addressSupplier', 'label': 'Supplier Address'},
            {'name': 'supplierInfo__supplierRepresentiveName', 'label': 'Supplier Rep Name'},
            # TenderNotificationInfo
            {'name': 'tenderNotificationInfo__tenderRefName', 'label': 'Tender Ref Name'},
            {'name': 'tenderNotificationInfo__tenderRefNumber', 'label': 'Tender Ref Number'},
            {'name': 'tenderNotificationInfo__tenderLotName', 'label': 'Tender Lot Name'},
            {'name': 'tenderNotificationInfo__tenderLotNumber', 'label': 'Tender Lot Number'},
        ],
        'sendCreditLineFacility': [
             # Top Level
            {'name': 'tenderRefName', 'label': 'Tender Ref Name'},
            {'name': 'tenderRefNumber', 'label': 'Tender Ref Number'},
            # CreditLineFacilityInfo
            {'name': 'creditLineFacilityInfo__accountNumber', 'label': 'Account Number'},
            {'name': 'creditLineFacilityInfo__amount', 'label': 'Amount'},
            {'name': 'creditLineFacilityInfo__amountCharacter', 'label': 'Amount (Words)'},
            {'name': 'creditLineFacilityInfo__creditLineNumber', 'label': 'Credit Line Number'},
            {'name': 'creditLineFacilityInfo__fromDate', 'label': 'From Date (YYYY-MM-DD)'},
            {'name': 'creditLineFacilityInfo__toDate', 'label': 'To Date (YYYY-MM-DD)'},
            {'name': 'creditLineFacilityInfo__unit', 'label': 'Currency Unit'},
             # IssueBankInfo
            {'name': 'issueBankInfo__bankName', 'label': 'Bank Name'},
            {'name': 'issueBankInfo__bankBranchName', 'label': 'Bank Branch Name'},
            {'name': 'issueBankInfo__bankTINNumber', 'label': 'Bank TIN'},
            {'name': 'issueBankInfo__branchAddress', 'label': 'Branch Address'},
            {'name': 'issueBankInfo__branchManagerName', 'label': 'Branch Manager Name'},
            {'name': 'issueBankInfo__securityRepresentiveName', 'label': 'Security Rep Name'},
            {'name': 'issueBankInfo__telNumber', 'label': 'Tel Number'},
            {'name': 'issueBankInfo__faxNumber', 'label': 'Fax Number'},
            {'name': 'issueBankInfo__email', 'label': 'Email'},
            {'name': 'issueBankInfo__comment', 'label': 'Comment'},
             # SupplierInfo
            {'name': 'supplierInfo__supplierName', 'label': 'Supplier Name'},
            {'name': 'supplierInfo__supplierTINNumber', 'label': 'Supplier TIN'},
            {'name': 'supplierInfo__addressSupplier', 'label': 'Supplier Address'},
            {'name': 'supplierInfo__supplierRepresentiveName', 'label': 'Supplier Rep Name'},
        ],
        'sendPerformSecurityInformation': [
            # PerformanceSecurityInfo
            {'name': 'performanceSecurityInfo__amount', 'label': 'Amount'},
            {'name': 'performanceSecurityInfo__amountCharacter', 'label': 'Amount (Words)'},
            {'name': 'performanceSecurityInfo__expireDate', 'label': 'Expire Date (YYYY-MM-DD)'},
            {'name': 'performanceSecurityInfo__securityName', 'label': 'Security Name'},
            {'name': 'performanceSecurityInfo__securityNumber', 'label': 'Security Number'},
            {'name': 'performanceSecurityInfo__startDate', 'label': 'Start Date (YYYY-MM-DD)'},
            {'name': 'performanceSecurityInfo__status', 'label': 'Status'},
            {'name': 'performanceSecurityInfo__unit', 'label': 'Currency Unit'},
             # IssueBankInfo
            {'name': 'issueBankInfo__bankName', 'label': 'Bank Name'},
            {'name': 'issueBankInfo__bankBranchName', 'label': 'Bank Branch Name'},
            {'name': 'issueBankInfo__bankTINNumber', 'label': 'Bank TIN'},
            {'name': 'issueBankInfo__branchAddress', 'label': 'Branch Address'},
            {'name': 'issueBankInfo__branchManagerName', 'label': 'Branch Manager Name'},
            {'name': 'issueBankInfo__securityRepresentiveName', 'label': 'Security Rep Name'},
            {'name': 'issueBankInfo__telNumber', 'label': 'Tel Number'},
            {'name': 'issueBankInfo__faxNumber', 'label': 'Fax Number'},
            {'name': 'issueBankInfo__email', 'label': 'Email'},
            {'name': 'issueBankInfo__comment', 'label': 'Comment'},
             # ContractInfo
            {'name': 'contractInfo__contractName', 'label': 'Contract Name'},
            {'name': 'contractInfo__contractNumber', 'label': 'Contract Number'},
            {'name': 'contractInfo__contractSerialNumber', 'label': 'Contract Serial Number'},
            {'name': 'contractInfo__contractDate', 'label': 'Contract Date (YYYY-MM-DD)'},
            {'name': 'contractInfo__address', 'label': 'Contract Address'},
            {'name': 'contractInfo__cellPhoneNumber', 'label': 'Contract Cell Phone'},
            {'name': 'contractInfo__eMailAddress', 'label': 'Contract Email'},
            {'name': 'contractInfo__pEName', 'label': 'Contract PE Name'},
            {'name': 'contractInfo__pETINNumber', 'label': 'Contract PE TIN'},
            {'name': 'contractInfo__supplierName', 'label': 'Contract Supplier Name'},
            {'name': 'contractInfo__supplierTINNumber', 'label': 'Contract Supplier TIN'},
            {'name': 'contractInfo__tenderRefName', 'label': 'Contract Tender Ref Name'},
            {'name': 'contractInfo__tenderRefNumber', 'label': 'Contract Tender Ref Number'},
            # Simplified LotInfo for ContractInfo - supporting one lot for MVP
            {'name': 'contractInfo__lotInfo__lotName', 'label': 'Lot Name'},
            {'name': 'contractInfo__lotInfo__lotNumber', 'label': 'Lot Number'},
        ]
    }

    def get(self, request, operation):
        fields = self.FIELD_CONFIG.get(operation, [
            {'name': 'payload_json', 'label': 'Payload (JSON)', 'type': 'textarea', 'required': True}
        ])
        return render(request, self.template_name, {
            'operation': operation,
            'fields': fields
        })

    def reconstruct_complex_objects(self, data, operation_config):
        """
        Reconstructs nested dictionaries from flat data based on FIELD_CONFIG naming convention (key__subkey).
        Handles basic nesting and simple list wrapping if keys imply index-like behavior (not yet implemented fully, using dict nesting).
        """
        result = {}
        # We explicitly process only fields defined in configuration to avoid polluting the payload with auth fields or others
        allowed_fields = [f['name'] for f in operation_config]
        
        for field in allowed_fields:
            value = data.get(field)
            # Filter out empty values to avoid sending empty strings for optional fields? 
            # WSDL usually prefers missing element or nillable. Zeep handles None as nillable if schema says so.
            # But empty string "" might be valid. Let's send what user typed if it's there.
            if value is None: 
                continue

            if '__' in field:
                parts = field.split('__')
                current = result
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                result[field] = value
        
        # Special handling: if we have lotInfo as a dict, but WSDL expects list, we might need to wrap it.
        # But 'zeep' usually auto-wraps dicts into lists if the element is maxOccurs > 1.
        # However, for nested matching, let's verify.
        # For this MVP, we rely on Zeep's dictionary mapping.
        
        return result

    def post(self, request, operation):
        # 1. Prepare Arguments
        # 1. Prepare Arguments
        # Hardcoded credentials as per final deployment requirements
        kwargs = {
            'id_val': 'UAP',
            'password': 'UAP!!009#',
        }
        
        # 2. Map Operation Name to Python Method
        method_map = {
            'getTenderInformation': 'get_tender_information',
            'sendAdvancePaymentInformation': 'send_advance_payment_information',
            'sendBidSecurityInformation': 'send_bid_security_information',
            'getContractInformation': 'get_contract_information',
            'sendCreditLineFacility': 'send_credit_line_facility',
            'sendPerformSecurityInformation': 'send_perform_security_information',
        }
        
        method_name = method_map.get(operation)
        if not method_name:
             return self.render_result(error=f"Unknown operation: {operation}")

        # 3. Extract Fields and Reconstruct Objects
        op_config = self.FIELD_CONFIG.get(operation, [])
        
        # We need to pass arguments expected by the SOAP method.
        # Reconstruct the complex object (the payload dict)
        # Note: Some methods take flattened args (getTenderInfo) and others take a dict (sendAdvance...).
        # We need to adapt.
        
        reconstructed_data = self.reconstruct_complex_objects(request.POST, op_config)
        
        try:
            if operation == 'getTenderInformation':
                # This one takes specific args in client method
                kwargs['ref_name'] = reconstructed_data.get('ref_name')
                kwargs['ref_number'] = reconstructed_data.get('ref_number')
            
            elif operation == 'getContractInformation':
                 kwargs['contract_number'] = reconstructed_data.get('contract_number')
                 kwargs['serial_number'] = reconstructed_data.get('contract_serial_number')

            elif operation == 'sendAdvancePaymentInformation':
                # Method expects payment_info dict
                # The reconstruct_complex_objects gave us a flat-ish dict structure but we need to ensure top-level args vs nested
                # our reconstructor made: {'contractName': ..., 'advancePaymentInfo': {...}}
                # The 'send_advance_payment_information' method signature in soap_client.py is:
                # def send_advance_payment_information(self, id_val, password, payment_info, user=None)
                # where payment_info is the AdvancePaymentInfoRequest dict.
                # So we pass the entire reconstructed data as 'payment_info'.
                kwargs['payment_info'] = reconstructed_data

            elif operation == 'sendBidSecurityInformation':
                kwargs['bid_info'] = reconstructed_data

            elif operation == 'sendCreditLineFacility':
                kwargs['credit_info'] = reconstructed_data
                
            elif operation == 'sendPerformSecurityInformation':
                kwargs['perform_info'] = reconstructed_data

            # 4. Execute
            client = SoapClient()
            method = getattr(client, method_name)
            result_obj = method(user=request.user, **kwargs)
            
            # Serialize
            result_json = json.dumps(serialize_object(result_obj), indent=2, default=str)
            return self.render_result(result=result_json)

        except Exception as e:
            return self.render_result(error=str(e))

    def render_result(self, result=None, error=None):
        return render(self.request, 'web/partials/operation_result.html', {
            'result': result,
            'error': error
        })

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'web/user_list.html'
    context_object_name = 'users'
    ordering = ['username']

    def get_queryset(self):
        # Only superusers should see this page typically, or check permissions
        if not self.request.user.is_superuser:
            return User.objects.none()
        return super().get_queryset()

from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from core.models import UserRole, Role

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['email', 'is_active', 'is_staff']
    template_name = 'web/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['email'].required = True
        return form
    template_name = 'web/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def form_valid(self, form):
        # Handle Roles
        # Simple implementation: expect role_ids in POST
        response = super().form_valid(form)
        
        # Update roles
        # Clear existing
        UserRole.objects.filter(user=self.object).delete()
        
        role_ids = self.request.POST.getlist('roles')
        for rid in set(role_ids):
            if rid:
                UserRole.objects.create(user=self.object, role_id=rid)
        
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_roles'] = Role.objects.all()
        context['user_role_ids'] = list(UserRole.objects.filter(user=self.object).values_list('role_id', flat=True))
        return context

from .forms_custom import CustomUserCreationForm
from django.views.generic.edit import CreateView

class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'web/user_create.html'
    success_url = reverse_lazy('user_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class TestSingleSoapView(View):
    def get(self, request):
        step = "Init"
        try:
            client = SoapClient()
            step = "Call"
            result = client.get_tender_information(
                id_val="TEST_USER_ID",
                password="TEST_PASSWORD",
                ref_name="TEST_REF",
                ref_number="12345",
                user=request.user if request.user.is_authenticated else None
            )
            return HttpResponse(f"<h1>SOAP Success</h1><pre>{result}</pre>")
        except Exception as e:
            return HttpResponse(f"<h1>SOAP Failed at {step}</h1><pre>{e}</pre>")
