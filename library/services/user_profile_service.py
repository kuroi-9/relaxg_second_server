from library.repositories.user_profile_repository import UserProfileRepository
from rg_server.models import CommonUser
from typing import Dict, Any

class UserProfileService:
    def __init__(self):
        self.user_profile_repository = UserProfileRepository()
        self.user_preferences: CommonUser | None = None

    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """
        Retrieve user preferences.

        Args:
            user_id (int): The ID of the user.

        Returns:
            dict: A dictionary containing user preferences.
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
        """Retrieve the default scan directory for a user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            str | None: The default scan directory or None if not set.
        """

        self.user_preferences = self.user_profile_repository.get_profile_by_user(user_id)
        if self.user_preferences:
            return str(self.user_preferences.scan_directory)
        else:
            raise ValueError(
                "User profile and its preferences not found, user_id: {}"
                .format(user_id)
            )

    def update_user_scan_directory(self, user_id: int, scan_directory: str) -> bool:
        """
        Update the default scan directory for a user.

        Args:
            user_id (int): The ID of the user.
            scan_directory (str): The new default scan directory.
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
        Update the preferences for a user.

        Args:
            user_id (int): The ID of the user.
            preferences (Dict[str, Any]): The new preferences.
        """

        try:
            return self.user_profile_repository.update_user_profile(user_id, preferences)
        except Exception as e:
            raise ValueError(
                "Failed to update user profile, user_id: {}, error: {}"
                .format(user_id, str(e))
            )
