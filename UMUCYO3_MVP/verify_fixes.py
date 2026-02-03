import os
import django
from django.conf import settings
from django.template.loader import render_to_string

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umucyo_mvp.settings')
django.setup()

def verify_soap_setting():
    print("--- Verifying SOAP Setting ---")
    mock_status = getattr(settings, 'MOCK_SOAP_API', None)
    print(f"MOCK_SOAP_API: {mock_status}")
    if mock_status is False:
        print("PASS: Mock mode is disabled.")
    else:
        print("FAIL: Mock mode is NOT disabled (Expected False).")

def verify_password_reset_template():
    print("\n--- Verifying Password Reset Template ---")
    try:
        context = {
            'protocol': 'http',
            'domain': 'example.com',
            'uid': 'uid',
            'token': 'token',
            'user': type('User', (object,), {'get_username': lambda: 'testuser'})(),
            'site_name': 'Umucyo MVP'
        }
        content = render_to_string('registration/password_reset_email.html', context)
        if "testuser" in content and "http://example.com" in content:
             print("PASS: Template rendered successfully.")
        else:
             print("FAIL: Template rendered but content missing expected values.")
    except Exception as e:
        print(f"FAIL: Template rendering raised error: {e}")

def verify_view_imports():
    print("\n--- Verifying View Logic Imports ---")
    try:
        from web.views import UserUpdateView
        print("PASS: UserUpdateView imported successfully (Syntax Check).")
    except Exception as e:
        print(f"FAIL: Could not import UserUpdateView: {e}")

if __name__ == "__main__":
    verify_soap_setting()
    verify_password_reset_template()
    verify_view_imports()
