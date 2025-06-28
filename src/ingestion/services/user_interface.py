"""
User interface service for handling user interactions and prompts.
"""
import logging
from typing import List, Dict
from collections import defaultdict

from ..core.interfaces.user_interface import UserInterface
from ..models.enums import (
    DeletionChoice, DeletionChoiceNumeric,
    BulkActionChoice, BulkActionChoiceNumeric,
    FileActionChoice, FileActionChoiceNumeric,
    FileType
)


logger = logging.getLogger(__name__)


class ConsoleUserInterface(UserInterface):
    """Console-based user interface for handling user interactions."""
    
    def _group_files_by_type(self, existing_files: List[str]) -> Dict[str, List[str]]:
        """
        Group files by their file type.
        
        Args:
            existing_files: List of existing files
            
        Returns:
            Dictionary mapping file types to lists of files
        """
        grouped_files = defaultdict(list)
        for filename in existing_files:
            # Extract file extension
            file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
            file_type = f".{file_extension}"
            
            # Map to FileType enum if supported
            try:
                file_type_enum = FileType.from_string(file_type)
                grouped_files[file_type_enum.value].append(filename)
            except ValueError:
                # If not in our enum, use the raw extension
                grouped_files[file_type].append(filename)
        
        return dict(grouped_files)
    
    def get_deletion_choice(self, existing_files: List[str]) -> str:
        """
        Get user choice for deletion operation.
        
        Args:
            existing_files: List of existing files
            
        Returns:
            User's choice
        """
        print(f"\nFound {len(existing_files)} existing files in the database:")
        
        # Group files by type
        grouped_files = self._group_files_by_type(existing_files)
        
        # Display files grouped by type
        for file_type, files in sorted(grouped_files.items()):
            print(f"\n{file_type.upper()} files ({len(files)}):")
            for i, filename in enumerate(files, 1):
                print(f"  {i}. {filename}")
        
        while True:
            print("\nChoose deletion option:")
            print("  1. Delete all files")
            print("  2. Delete all files of a specific type")
            print("  3. Choose specific files to delete")
            print("  4. Skip deletion")
            
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == DeletionChoiceNumeric.ALL.value:
                logger.debug("User chose deletion option: all")
                return DeletionChoice.ALL.value
            elif choice == DeletionChoiceNumeric.ALL_BY_TYPE.value:
                logger.debug("User chose deletion option: all_by_type")
                return DeletionChoice.ALL_BY_TYPE.value
            elif choice == DeletionChoiceNumeric.SPECIFIC.value:
                logger.debug("User chose deletion option: specific")
                return DeletionChoice.SPECIFIC.value
            elif choice == DeletionChoiceNumeric.SKIP.value:
                logger.debug("User chose deletion option: skip")
                return DeletionChoice.SKIP.value
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
    
    def get_file_type_deletion_choice(self, grouped_files: Dict[str, List[str]]) -> str:
        """
        Get user choice for deleting all files of a specific type.
        
        Args:
            grouped_files: Dictionary mapping file types to lists of files
            
        Returns:
            File type to delete all files from
        """
        print("\nChoose file type to delete all files from:")
        
        # Create a numbered list of file types
        file_types = list(grouped_files.keys())
        for i, file_type in enumerate(file_types, 1):
            file_count = len(grouped_files[file_type])
            print(f"  {i}. {file_type.upper()} ({file_count} files)")
        
        while True:
            try:
                choice = input(f"Enter your choice (1-{len(file_types)}): ").strip()
                index = int(choice) - 1
                
                if 0 <= index < len(file_types):
                    selected_type = file_types[index]
                    logger.debug(f"User chose to delete all {selected_type} files")
                    return selected_type
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(file_types)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    def get_bulk_action_choice(self, existing_files: List[str]) -> str:
        """
        Get user choice for bulk action.
        
        Args:
            existing_files: List of existing files
            
        Returns:
            User's choice
        """
        print(f"\nFound {len(existing_files)} existing files in the database:")
        for i, filename in enumerate(existing_files, 1):
            print(f"  {i}. {filename}")
        
        while True:
            print("\nChoose bulk action:")
            print("  1. Add all new files")
            print("  2. Choose specific files to add")
            print("  3. Skip all files")
            
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == BulkActionChoiceNumeric.ADD_ALL.value:
                logger.debug("User chose bulk action: add_all")
                return BulkActionChoice.ADD_ALL.value
            elif choice == BulkActionChoiceNumeric.ADD_SPECIFIC.value:
                logger.debug("User chose bulk action: add_specific")
                return BulkActionChoice.ADD_SPECIFIC.value
            elif choice == BulkActionChoiceNumeric.SKIP_ALL.value:
                logger.debug("User chose bulk action: skip_all")
                return BulkActionChoice.SKIP_ALL.value
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
    
    def get_user_choice(self, filename: str) -> str:
        """
        Get user choice for individual file.
        
        Args:
            filename: Name of the file
            
        Returns:
            User's choice
        """
        while True:
            print(f"\nFile: {filename}")
            print("  1. Add this file")
            print("  2. Skip this file")
            
            choice = input("Enter your choice (1-2): ").strip()
            
            if choice == FileActionChoiceNumeric.ADD.value:
                logger.debug(f"User chose 'add' for file: {filename}")
                return FileActionChoice.ADD.value
            elif choice == FileActionChoiceNumeric.SKIP.value:
                logger.debug(f"User chose 'skip' for file: {filename}")
                return FileActionChoice.SKIP.value
            else:
                print("Invalid choice. Please enter 1 or 2.")
    
    def confirm_action(self, message: str) -> bool:
        """
        Confirm an action with the user.
        
        Args:
            message: Message to display
            
        Returns:
            True if user confirms
        """
        while True:
            response = input(f"{message} (y/n): ").strip().lower()
            
            if response in ['y', 'yes']:
                logger.debug(f"User confirmed: {message}")
                return True
            elif response in ['n', 'no']:
                logger.debug(f"User declined: {message}")
                return False
            else:
                print("Please enter 'y' or 'n'.") 