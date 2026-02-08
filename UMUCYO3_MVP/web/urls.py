from django.urls import path, include
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, DashboardView, OperationListView, OperationExecuteView, UserListView, UserUpdateView, UserCreateView, TestSingleSoapView, ExportReadLogsExcelView

urlpatterns = [
    path('test-soap/', TestSingleSoapView.as_view(), name='test_soap'),
    path('accounts/', include('django.contrib.auth.urls')), # Password reset views are here
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/export-excel/', ExportReadLogsExcelView.as_view(), name='dashboard_export_excel'),
    path('operations/', OperationListView.as_view(), name='operation_list'),
    path('operations/<str:operation>/', OperationExecuteView.as_view(), name='operation_execute'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
]
