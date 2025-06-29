"""
Builder for the ingestion menu using the generic menu system.
"""
from ...menu.core.menu_builder import MenuBuilder
from ...menu.core.menu_component import MenuComponent
from ...menu.concrete.menu_group import MenuGroup
from ...menu.core.menu_registry import MenuRegistry
from ..commands.process_files_command import (
    AddFilesByTypeCommand,
    AddSpecificFileCommand,
    ClearDatabaseCommand,
    HandleExistingFilesCommand,
    HandleOrphanedFilesCommand,
    ProcessNewFilesCommand,
)


class IngestionMenuBuilder(MenuBuilder):
    """Builder for the ingestion menu using the generic menu system."""

    def build_main_menu(self) -> MenuGroup:
        """Build the main ingestion menu structure."""
        self.reset()

        # Start main menu
        self.start_menu(
            "DOCUMENT INGESTION MENU", "Main menu for document ingestion operations"
        )

        # Add menu items
        self.add_command(
            ProcessNewFilesCommand(),
            "1",
            "Process new files",
            "Add files that exist only in local folder",
        )

        self.add_command(
            HandleExistingFilesCommand(),
            "2",
            "Handle existing files",
            "Manage files that exist in both local folder and database",
        )

        self.add_command(
            HandleOrphanedFilesCommand(),
            "3",
            "Handle orphaned files",
            "Manage files that exist only in database",
        )

        self.add_command(
            ClearDatabaseCommand(),
            "4",
            "Clear database",
            "Clear all or specific files from database",
        )

        self.add_command(
            AddFilesByTypeCommand(),
            "5",
            "Add files by type",
            "Add files by type from local folder",
        )

        self.add_command(
            AddSpecificFileCommand(),
            "6",
            "Add specific file",
            "Add a specific file from local folder",
        )

        # Add exit command
        self.add_exit_command("Exit (cancel all operations)")

        return self.build()
