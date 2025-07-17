from django.test import TestCase
from unittest.mock import patch, MagicMock
from library.services.user_profile_service import UserProfileService
from rg_server.models import CommonUser
from django.conf import settings

class UserProfileServiceTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not settings.configured:
            settings.configure(
                BOOKS_DIR='/mock/books/dir',
                DEBUG=True,
                INSTALLED_APPS=[
                    'django.contrib.auth',
                    'django.contrib.contenttypes',
                    'library',
                ],
                DATABASES={
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': ':memory:',
                    }
                },
            )

    def setUp(self):
        # Patch the UserProfileRepository at the class level before initializing the service
        self.patcher = patch('library.services.user_profile_service.UserProfileRepository')
        self.MockUserProfileRepository = self.patcher.start()
        self.mock_repo_instance = self.MockUserProfileRepository.return_value

        self.service = UserProfileService() # Now this will use the mocked repository

        # Create a mock user for consistent testing
        self.mock_user_id = 1
        self.mock_user_data = {
            'username': 'testuser',
            'is_superuser': False,
            'is_staff': False,
            'is_active': True,
            'date_joined': '2023-01-01T12:00:00Z',
            'scan_directory': '/default/scan/dir',
        }
        self.mock_user_profile = MagicMock(spec=CommonUser)
        # Defining mock_user_profile properties by iterating the mock_user_data dictionary
        for key, value in self.mock_user_data.items():
            setattr(self.mock_user_profile, key, value)
        # Ensure scan_directory is treated as a string for return values
        self.mock_user_profile.scan_directory = '/default/scan/dir'

    def tearDown(self):
        self.patcher.stop() # Stop the patcher after each test


    def test_get_user_preferences_success(self):
        self.mock_repo_instance.get_profile_by_user.return_value = self.mock_user_profile

        preferences = self.service.get_user_preferences(self.mock_user_id)

        self.mock_repo_instance.get_profile_by_user.assert_called_once_with(self.mock_user_id)
        self.assertIsInstance(preferences, dict)
        self.assertEqual(preferences['username'], self.mock_user_data['username'])
        self.assertEqual(preferences['scan_directory'], self.mock_user_data['scan_directory'])
        self.assertEqual(preferences['is_superuser'], self.mock_user_data['is_superuser'])
        # Add more assertions for other fields if necessary

    def test_get_user_preferences_not_found(self):
        self.mock_repo_instance.get_profile_by_user.return_value = None

        with self.assertRaises(ValueError) as cm:
            self.service.get_user_preferences(self.mock_user_id)

        self.assertIn("User profile and its preferences not found", str(cm.exception))
        self.mock_repo_instance.get_profile_by_user.assert_called_once_with(self.mock_user_id)

    def test_get_user_scan_directory_success(self):
        self.mock_repo_instance.get_profile_by_user.return_value = self.mock_user_profile

        scan_directory = self.service.get_user_scan_directory(self.mock_user_id)

        self.mock_repo_instance.get_profile_by_user.assert_called_once_with(self.mock_user_id)
        self.assertEqual(scan_directory, self.mock_user_data['scan_directory'])

    def test_get_user_scan_directory_not_found(self):
        self.mock_repo_instance.get_profile_by_user.return_value = None

        with self.assertRaises(ValueError) as cm:
            self.service.get_user_scan_directory(self.mock_user_id)

        self.assertIn("User profile and its preferences not found", str(cm.exception))
        self.mock_repo_instance.get_profile_by_user.assert_called_once_with(self.mock_user_id)

    def test_update_user_scan_directory_success(self):
        self.mock_repo_instance.get_profile_by_user.return_value = self.mock_user_profile
        new_scan_dir = "/new/updated/scan/dir"
        self.mock_repo_instance.set_default_scan_directory.return_value = new_scan_dir

        result = self.service.update_user_scan_directory(self.mock_user_id, new_scan_dir)

        self.assertTrue(result)
        self.mock_repo_instance.get_profile_by_user.assert_called_once_with(self.mock_user_id)
        self.mock_repo_instance.set_default_scan_directory.assert_called_once_with(self.mock_user_id, new_scan_dir)

    def test_update_user_scan_directory_user_not_found(self):
        self.mock_repo_instance.get_profile_by_user.return_value = None
        new_scan_dir = "/new/updated/scan/dir"

        with self.assertRaises(ValueError) as cm:
            self.service.update_user_scan_directory(self.mock_user_id, new_scan_dir)

        self.assertIn("User profile not found", str(cm.exception))
        self.mock_repo_instance.get_profile_by_user.assert_called_once_with(self.mock_user_id)
        self.mock_repo_instance.set_default_scan_directory.assert_not_called()

    def test_update_user_preferences_success(self):
        preferences = {"scan_directory": "/another/new/dir"}
        self.mock_repo_instance.update_user_profile.return_value = True

        result = self.service.update_user_preferences(self.mock_user_id, preferences)

        self.assertTrue(result)
        self.mock_repo_instance.update_user_profile.assert_called_once_with(self.mock_user_id, preferences)

    def test_update_user_preferences_failure(self):
        preferences = {"scan_directory": "/another/new/dir"}
        # The ValueError from repository.update_user_profile should not rely on 'id' being in preferences
        self.mock_repo_instance.update_user_profile.side_effect = ValueError("Repository update failed")

        with self.assertRaises(ValueError) as cm:
            self.service.update_user_preferences(self.mock_user_id, preferences)

        self.assertIn("Failed to update user profile", str(cm.exception))
        self.mock_repo_instance.update_user_profile.assert_called_once_with(self.mock_user_id, preferences)
