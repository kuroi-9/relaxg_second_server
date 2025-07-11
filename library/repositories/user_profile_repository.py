from library.models import UserProfile
from django.contrib.auth import get_user_model

class UserProfileRepository:
    def __init__(self):
        self.User = get_user_model() # TOFIX: Not specified as a type

    # Prototype: Retrieves the user profile by user object.
    # Pre-conditions: 'user' is an instance of the Django user.
    # Post-conditions: Returns the associated UserProfile instance or None if not found.
    def get_profile_by_user(self, user) -> UserProfile | None:
        pass

    # Prototype: Creates or updates the default scan directory for a user.
    # Pre-conditions: 'user' is an instance of the Django user, 'directory_path' is the path to set.
    # Post-conditions: Creates or updates the UserProfile and returns the set path.
    def set_default_scan_directory(self, user, directory_path: str) -> str:
        pass

    # Prototype: Retrieves the default scan directory for a user.
    # Pre-conditions: 'user' is an instance of the Django user.
    # Post-conditions: Returns the default directory path or None if not set.
    def get_default_scan_directory(self, user) -> str | None:
        pass
