"""
Abstract interface for user interaction.
"""
from abc import ABC, abstractmethod
from typing import Dict, List


class UserInterface(ABC):
    """Abstract interface for user interaction."""

    @abstractmethod
    def get_deletion_choice(self, existing_files: List[str]) -> str:
        """
        Get user choice for deletion operation.

        Args:
            existing_files: List of existing files

        Returns:
            User's choice
        """
        pass

    @abstractmethod
    def get_file_type_deletion_choice(self, grouped_files: Dict[str, List[str]]) -> str:
        """
        Get user choice for deleting all files of a specific type.

        Args:
            grouped_files: Dictionary mapping file types to lists of files

        Returns:
            File type to delete all files from
        """
        pass

    @abstractmethod
    def get_bulk_action_choice(self, existing_files: List[str]) -> str:
        """
        Get user choice for bulk action.

        Args:
            existing_files: List of existing files

        Returns:
            User's choice
        """
        pass

    @abstractmethod
    def get_user_choice(self, filename: str) -> str:
        """
        Get user choice for individual file.

        Args:
            filename: Name of the file

        Returns:
            User's choice
        """
        pass

    @abstractmethod
    def confirm_action(self, message: str) -> bool:
        """
        Confirm an action with the user.

        Args:
            message: Message to display

        Returns:
            True if user confirms
        """
        pass

    @abstractmethod
    def get_specific_file_choices(self, files: List[str], action: str) -> List[str]:
        """
        Get user choice for specific files to perform an action on.

        Args:
            files: List of files to choose from
            action: Action to perform (add, skip, delete)

        Returns:
            List of selected filenames
        """
        pass

    @abstractmethod
    def _group_files_by_type(self, existing_files: List[str]) -> Dict[str, List[str]]:
        """
        Group files by their file type.

        Args:
            existing_files: List of existing files

        Returns:
            Dictionary mapping file types to lists of files
        """
        pass
