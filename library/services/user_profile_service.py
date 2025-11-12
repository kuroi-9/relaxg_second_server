from library.repositories.user_profile_repository import UserProfileRepository
from rg_server.models import CommonUser
from typing import Dict, Any

class UserProfileService:
    def __init__(self):
        self.user_profile_repository = UserProfileRepository()
        self.user_preferences: CommonUser | None = None

    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """
        Prototype: Retrieve user preferences for a given user.
        Pre-conditions:
        - 'user_id' is the ID of the user whose preferences are being retrieved.
        Post-conditions:
        - Returns a dictionary containing user preferences if found.
        - Raises ValueError if user profile is not found.
        """

        self.user_preferences = self.user_profile_repository.get_profile_by_user(user_id)
        if self.user_preferences:
            return {
                'username': self.user_preferences.username,
                'is_superuser': self.user_preferences.is_superuser,
                'is_staff': self.user_preferences.is_staff,
                'is_active': self.user_preferences.is_active,
                'date_joined': self.user_preferences.date_joined,
                'scan_directory': str(self.user_preferences.scan_directory),
            }
        else:
            raise ValueError(
                "User profile and its preferences not found, user_id: {}"
                .format(user_id)
            )

    def get_user_scan_directory(self, user_id) -> str | None:
        """
        Prototype: Retrieve the default scan directory for a user.
        Pre-conditions:
        - 'user_id' is the ID of the user whose scan directory is being retrieved.
        Post-conditions:
        - Returns the scan directory as a string if found.
        - Returns None if scan directory is not set.
        - Raises ValueError if user profile is not found.
        """

        self.user_preferences = self.user_profile_repository.get_profile_by_user(user_id)
        if self.user_preferences:
            if not self.user_preferences.scan_directory:
                return None
            else:
                return str(self.user_preferences.scan_directory)
        else:
            raise ValueError(
                "User profile and its preferences not found, user_id: {}"
                .format(user_id)
            )

    def update_user_scan_directory(self, user_id: int, scan_directory: str) -> bool:
        """
        Prototype: Update the default scan directory for a user.
        Pre-conditions:
        - 'user_id' is the ID of the user whose scan directory is being updated.
        - 'scan_directory' is the new directory path to set.
        Post-conditions:
        - Returns True if the update was successful.
        - Raises ValueError if user profile is not found.
        """

        user_profile = self.user_profile_repository.get_profile_by_user(user_id)
        if user_profile:
            new_scan_directory = self.user_profile_repository.set_default_scan_directory(user_id, scan_directory)
            return new_scan_directory == scan_directory
        else:
            raise ValueError(
                "User profile not found, user_id: {}"
                .format(user_id)
            )

    # TODO: Eventually implement Unit of Work pattern
    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """
        Prototype: Update user preferences for a given user.
        Pre-conditions:
        - 'user_id' is the ID of the user whose preferences are being updated.
        - 'preferences' is a dictionary containing the new preferences to set.
        Post-conditions:
        - Returns True if the update was successful.
        - Raises ValueError if the update fails.
        """

        try:
            return self.user_profile_repository.update_user_profile(user_id, preferences)
        except Exception as e:
            raise ValueError(
                "Failed to update user profile, user_id: {}, error: {}"
                .format(user_id, str(e))
            )
