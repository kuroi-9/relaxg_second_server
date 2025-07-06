from library.models import UserProfile
from django.contrib.auth import get_user_model
from typing import Any

User = get_user_model()

class UserProfileRepository:
    # Prototype: Retrieves the user profile by user object.
    # Pre-conditions: 'user' is an instance of the Django user.
    # Post-conditions: Returns the associated UserProfile instance or None if not found.
    def get_profile_by_user(self, user: User) -> UserProfile | None:
        pass

    # Prototype: Creates or updates the default scan directory for a user.
    # Pre-conditions: 'user' is an instance of the Django user, 'directory_path' is the path to set.
    # Post-conditions: Creates or updates the UserProfile and returns the set path.
    def set_default_scan_directory(self, user: User, directory_path: str) -> str:
        pass

    # Prototype: Retrieves the default scan directory for a user.
    # Pre-conditions: 'user' is an instance of the Django user.
    # Post-conditions: Returns the default directory path or None if not set.
    def get_default_scan_directory(self, user: User) -> str | None:
        pass
