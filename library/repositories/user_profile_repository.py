from rg_server.models import CommonUser
from django.contrib.auth import get_user_model
from typing import Dict, Any

class UserProfileRepository:
    def __init__(self):
        self.CommonUser = get_user_model()

    def get_profile_by_user(self, user_id) -> CommonUser | None:
        """
        Prototype: Retrieves the user profile by user object.
        Pre-conditions: 'user_id' is an instance of the Django user.
        Post-conditions: Returns the associated UserProfile instance or None if not found.
        """

        return self.CommonUser._default_manager.filter(id=user_id).first()

    def set_default_scan_directory(self, user_id, directory_path: Any) -> str:
        """
        Prototype: Creates or updates the default scan directory for a user.
        Pre-conditions:
        - 'user_id' is an instance of the Django user.
        - 'directory_path' is the path to set.
        Post-conditions: Creates or updates the UserProfile and returns the set path.
        """

        user_profile = self.get_profile_by_user(user_id)
        if user_profile:
            user_profile.scan_directory = directory_path
            user_profile.save()
            return str(user_profile.scan_directory)
        else:
            raise ValueError(
                "User profile not found, user_id: {}"
                .format(user_id)
            )

    def update_user_profile(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """
        Prototype: Updates the user profile with the provided preferences.
        Pre-conditions:
        - 'user_id' is the ID of the user.
        - 'preferences' is a dictionary containing the updated preferences.
        Post-conditions: Updates the UserProfile and returns True if successful.
        """

        try:
            user_profile = self.get_profile_by_user(user_id)
            if user_profile:
                user_profile.scan_directory = preferences.get('scan_directory', user_profile.scan_directory)
                user_profile.save()
            else:
                raise ValueError(
                    "User profile not found, user_id: {}"
                    .format(user_id)
                )
        except Exception as e:
            raise ValueError(
                "Failed to update user profile, user_id: {}, error: {}"
                .format(preferences['id'], str(e))
            )

        return True
