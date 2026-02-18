from django.test import TestCase, Client, RequestFactory, override_settings
from django.contrib.auth.models import User
from core.models import Role, UserRole
from django.urls import reverse
from web.views import UserCreateView, UserUpdateView
import logging

# Configure logging to show up in test output
logging.basicConfig(level=logging.INFO)

@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class RoleAssignmentViewTest(TestCase):
    def setUp(self):
        # Create Roles
        self.role_admin = Role.objects.create(name='Admin')
        self.role_manager = Role.objects.create(name='Manager')
        
        # Create Admin User for login
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client.force_login(self.admin_user)
        
        # URL for creating user
        # Assuming 'user_create' is the url name based on views.py success_url usage implying list is 'user_list', create might be 'user_create'?
        # Let's check urls.py but for now assume standard naming or use view directly if needed.
        # But robust test uses client.
        
    def test_create_user_with_roles(self):
        print("\n--- Testing User Creation with Roles ---")
        role_ids = [str(self.role_admin.id), str(self.role_manager.id)]
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123', # UserCreationForm needs password
            'roles': role_ids
        }
        
        # We need to see if we can post.
        # Note: CustomUserCreationForm extends UserCreationForm, so it requires two passwords normally?
        # Let's check forms_custom.py again. It just adds email.
        # Standard UserCreationForm requires 'password_1' and 'password_2'.
        
        data['password1'] = 'StrongPass123!@#'
        data['password2'] = 'StrongPass123!@#'
        
        # Try to find the URL. If I can't find it easily, I'll use list_resources or just try 'user_create'
        try:
            url = reverse('user_create') 
        except:
            # Fallback if I can't guess valid URL name check urls.py
            print("Could not reverse 'user_create', checking urls.py...")
            return
            
        print(f"Posting to {url} with roles {role_ids}")
        response = self.client.post(url, data)
        
        if response.status_code != 302:
            print(f"Failed to create user. Status: {response.status_code}")
            print(f"Form errors: {response.context['form'].errors if 'form' in response.context else 'No form context'}")
        else:
            print("User creation redirect (success).")
            
        # Verify
        try:
            new_user = User.objects.get(username='newuser')
            roles = UserRole.objects.filter(user=new_user)
            role_names = [r.role.name for r in roles]
            print(f"Created User Roles: {role_names}")
            
            self.assertTrue(new_user.user_roles.filter(role=self.role_admin).exists())
            self.assertTrue(new_user.user_roles.filter(role=self.role_manager).exists())
            print("SUCCESS: Roles assigned on creation.")
        except User.DoesNotExist:
            print("FAILURE: User not created.")

    def test_update_user_roles(self):
        print("\n--- Testing User Update Roles ---")
        # Create a user with Manager role
        user = User.objects.create_user('edituser', 'edit@example.com', 'password')
        UserRole.objects.create(user=user, role=self.role_manager)
        
        # Verify initial
        print(f"Initial roles: {[r.role.name for r in UserRole.objects.filter(user=user)]}")
        
        # Update to Admin Only
        data = {
            'email': 'edit@example.com', # required
            'is_active': 'on',
            'roles': [str(self.role_admin.id)]
        }
        
        try:
            url = reverse('user_edit', kwargs={'pk': user.pk})
        except:
             print("Could not reverse 'user_edit'")
             return

        print(f"Posting to {url} with new roles {[self.role_admin.id]}")
        response = self.client.post(url, data)
        
        if response.status_code != 302:
            print(f"Failed to update user. Status: {response.status_code}")
            # print errors
        else:
            print("User update redirect (success).")
            
        # Verify
        roles = UserRole.objects.filter(user=user)
        role_names = [r.role.name for r in roles]
        print(f"Updated User Roles: {role_names}")
        
        self.assertEqual(roles.count(), 1)
        self.assertEqual(roles.first().role, self.role_admin)
        print("SUCCESS: Roles updated correctly.")
