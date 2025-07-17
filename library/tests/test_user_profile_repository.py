from django.test import TestCase
from rg_server.models import CommonUser
from library.repositories.user_profile_repository import UserProfileRepository

class UserProfileRepositoryTest(TestCase):
    def setUp(self):
        self.repository = UserProfileRepository()
        self.user = CommonUser.objects.create(
            id=2,
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='password123',
            is_active=True,
            is_staff=False,
            is_superuser=False,
            scan_directory='/default/dir/test/'
        )


    def tearDown(self) -> None:
        CommonUser.objects.all().delete();

    def test_get_profile_by_user(self):
        user_profile = self.repository.get_profile_by_user(self.user.id)
        self.assertIsInstance(user_profile, CommonUser)
        self.assertEqual(user_profile, self.user)

    def test_set_default_scan_directory_success(self):
        new_scan_dir = "/new/scan/directory"
        returned_path = self.repository.set_default_scan_directory(self.user.id, new_scan_dir)
        self.user.refresh_from_db() # Refresh the user instance to get updated data
        self.assertEqual(returned_path, new_scan_dir)
        self.assertEqual(self.user.scan_directory, new_scan_dir)

    def test_set_default_scan_directory_user_not_found(self):
        non_existent_user_id = 999
        with self.assertRaises(ValueError) as cm:
            self.repository.set_default_scan_directory(non_existent_user_id, "/some/path")
        self.assertIn("User profile not found", str(cm.exception))

    def test_update_user_profile_success(self):
        preferences = {"scan_directory": "/updated/scan/directory"}
        success = self.repository.update_user_profile(self.user.id, preferences)
        self.assertTrue(success)
        self.user.refresh_from_db() # Refresh the user instance to get updated data
        self.assertEqual(self.user.scan_directory, preferences["scan_directory"])

    def test_update_user_profile_user_not_found(self):
        non_existent_user_id = 999
        preferences = {"id": non_existent_user_id, "scan_directory": "/some/path"}
        with self.assertRaises(ValueError) as cm:
            self.repository.update_user_profile(non_existent_user_id, preferences)
        self.assertIn("User profile not found", str(cm.exception))

    def test_set_default_scan_directory(self) -> None:
        old_scan_directory = '/set/new/scan_directory'
        new_scan_directory_returned = self.repository.set_default_scan_directory(
            self.user.id, old_scan_directory)
        self.assertEqual(old_scan_directory, new_scan_directory_returned)
