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
        'sendAdvancePaymentInformation': [
            {'name': 'payment_info_json', 'label': 'Payment Info (JSON)', 'type': 'textarea', 'help_text': 'Paste valid JSON for AdvancePaymentInfo'},
        ],
        'sendBidSecurityInformation': [
            {'name': 'bid_info_json', 'label': 'Bid Info (JSON)', 'type': 'textarea', 'help_text': 'Paste valid JSON for BidSecurityInfo'},
        ],
        'getContractInformation': [
            {'name': 'contract_number', 'label': 'Contract Number', 'required': True},
            {'name': 'contract_serial_number', 'label': 'Contract Serial Number', 'required': True},
        ],
        'sendCreditLineFacility': [
            {'name': 'credit_info_json', 'label': 'Credit Info (JSON)', 'type': 'textarea', 'help_text': 'Paste valid JSON for CreditLineFacilityInfo'},
        ],
        'sendPerformSecurityInformation': [
             {'name': 'perform_info_json', 'label': 'Performance Info (JSON)', 'type': 'textarea', 'help_text': 'Paste valid JSON for PerformanceSecurityInfo'},
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

    def post(self, request, operation):
        # 1. Prepare Arguments
        kwargs = {
            'id_val': request.POST.get('id'),
            'password': request.POST.get('password'),
        }
        
        # 2. Map Operation Name to Python Method (Reusing logic from API view ideally)
        # Simple mapper again
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

        # 3. Extract Specific Fields
        fields = self.FIELD_CONFIG.get(operation, [])
        
        try:
            if operation == 'getTenderInformation':
                kwargs['ref_name'] = request.POST.get('ref_name')
                kwargs['ref_number'] = request.POST.get('ref_number')
            
            elif operation == 'getContractInformation':
                 kwargs['contract_number'] = request.POST.get('contract_number')
                 kwargs['serial_number'] = request.POST.get('contract_serial_number')

            elif any(k in operation for k in ['send', 'Payment', 'Security', 'Facility']):
                # These methods expect a Dictionary object
                # We look for specific json input or fallback
                # Determine correct field name from config or guess
                json_str = None
                arg_key = None
                
                if 'AdvancePayment' in operation: 
                    json_str = request.POST.get('payment_info_json')
                    arg_key = 'payment_info'
                elif 'BidSecurity' in operation: 
                    json_str = request.POST.get('bid_info_json')
                    arg_key = 'bid_info'
                elif 'CreditLine' in operation: 
                    json_str = request.POST.get('credit_info_json')
                    arg_key = 'credit_info'
                elif 'PerformSecurity' in operation: 
                    json_str = request.POST.get('perform_info_json')
                    arg_key = 'perform_info'

                if json_str and arg_key:
                    kwargs[arg_key] = json.loads(json_str) 

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
    fields = ['is_active', 'is_staff']
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

from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView

class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserCreationForm
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
