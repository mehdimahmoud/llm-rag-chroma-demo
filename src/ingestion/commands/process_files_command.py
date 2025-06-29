"""
Command for processing new files in the ingestion system.
"""
import os

from ...menu.core.enums import MenuChoice
from ...menu.core.menu_command import CommandContext, CommandResult, MenuCommand
from ..core.enums import (
    BulkActionChoice,
    FileActionChoice,
    FileCategory,
    IngestionAction,
)
from ..core.interfaces import (
    DocumentLoader,
    EmbeddingGenerator,
    TextChunker,
    VectorStore,
)
from ..core.models.menu_context import MenuContext
from ..models.document import DocumentChunk
from ..services.text_extractor_factory import TextExtractorFactory


class ProcessNewFilesCommand(MenuCommand):
    """Command to process new files (files only in local folder)."""

    def __init__(self):
        super().__init__(
            "process_new_files", "Process files that exist only in local folder"
        )

    def execute(self, context: CommandContext) -> CommandResult:
        """Execute the process new files command."""
        # Extract ingestion-specific data from generic context
        files_only_local = context.data.get(FileCategory.NEW_FILES.value, set())
        user_interface = context.user_interface
        logger = context.logger

        if not files_only_local:
            return CommandResult.continue_result("No new files to process")

        # Display new files submenu
        print("\n" + "=" * 50)
        print("PROCESS NEW FILES MENU")
        print("=" * 50)

        print(f"\nFound {len(files_only_local)} new files:")
        for i, filename in enumerate(sorted(files_only_local), 1):
            print(f"  {i}. {filename}")

        print("\nOptions:")
        print("1. Add all new files")
        print("2. Add specific new files")
        print("3. Add new files by type")
        print("4. Skip all new files")
        print("0. Back to main menu")

        while True:
            try:
                choice = input("\nEnter your choice (0-4): ").strip()

                if choice == "0":
                    return CommandResult.continue_result("Returning to main menu")
                elif choice == "1":
                    if user_interface and user_interface.confirm_action(
                        f"Add all {len(files_only_local)} new files to database?"
                    ):
                        return CommandResult.custom_action_result(
                            IngestionAction.ADD_FILES.value,
                            {
                                "action_type": IngestionAction.ADD_FILES.value,
                                "files": files_only_local,
                            },
                            f"Adding {len(files_only_local)} new files",
                        )
                    else:
                        return CommandResult.continue_result("File addition cancelled")
                elif choice == "2":
                    # Display files for selection
                    print("\nSelect files to add:")
                    sorted_files = sorted(files_only_local)
                    for i, filename in enumerate(sorted_files, 1):
                        print(f"  {i}. {filename}")

                    print("\nEnter file numbers separated by commas (e.g., 1,3,5)")
                    print("Or enter 'all' to select all files")

                    file_choice = input("Your selection: ").strip().lower()

                    if file_choice == "all":
                        selected_files = files_only_local
                    else:
                        try:
                            indices = [
                                int(x.strip()) - 1 for x in file_choice.split(",")
                            ]
                            selected_files = set()
                            for idx in indices:
                                if 0 <= idx < len(sorted_files):
                                    selected_files.add(sorted_files[idx])
                                else:
                                    return CommandResult.continue_result(
                                        f"Invalid file number: {idx + 1}"
                                    )
                        except ValueError:
                            return CommandResult.continue_result(
                                "Invalid input - please enter numbers separated by commas"
                            )

                    if (
                        selected_files
                        and user_interface
                        and user_interface.confirm_action(
                            f"Add {len(selected_files)} selected files to database?"
                        )
                    ):
                        return CommandResult.custom_action_result(
                            IngestionAction.ADD_FILES.value,
                            {
                                "action_type": IngestionAction.ADD_FILES.value,
                                "files": selected_files,
                            },
                            f"Adding {len(selected_files)} selected files",
                        )
                    return CommandResult.continue_result("File addition cancelled")
                elif choice == "3":
                    # Group files by type
                    files_by_type = {}
                    for filename in files_only_local:
                        file_ext = (
                            filename.lower().split(".")[-1]
                            if "." in filename
                            else "unknown"
                        )
                        if file_ext not in files_by_type:
                            files_by_type[file_ext] = []
                        files_by_type[file_ext].append(filename)

                    print("\nAvailable file types:")
                    for i, (file_type, files) in enumerate(
                        sorted(files_by_type.items()), 1
                    ):
                        print(f"  {i}. {file_type.upper()} ({len(files)} files)")
                    print("  0. Back to main menu")

                    type_choice = input(
                        f"Enter your choice (0-{len(files_by_type)}): "
                    ).strip()

                    if type_choice == "0":
                        continue

                    try:
                        choice_idx = int(type_choice) - 1
                        if 0 <= choice_idx < len(files_by_type):
                            selected_type = list(sorted(files_by_type.keys()))[
                                choice_idx
                            ]
                            selected_files = set(files_by_type[selected_type])

                            if user_interface and user_interface.confirm_action(
                                f"Add all {len(selected_files)} {selected_type.upper()} files to database?"
                            ):
                                return CommandResult.custom_action_result(
                                    IngestionAction.ADD_FILES.value,
                                    {
                                        "action_type": IngestionAction.ADD_FILES.value,
                                        "files": set(selected_files),
                                    },
                                    f"Adding {len(selected_files)} {selected_type.upper()} files",
                                )
                            else:
                                return CommandResult.continue_result(
                                    "File addition cancelled"
                                )
                        else:
                            print(
                                f"Invalid choice. Please enter 0-{len(files_by_type)}."
                            )
                    except ValueError:
                        print("Invalid choice - please enter a number")
                elif choice == "4":
                    logger.info("User chose to skip all new files")
                    return CommandResult.continue_result("Skipped all new files")
                else:
                    print("Invalid choice. Please enter 0, 1, 2, 3, or 4.")
            except (ValueError, KeyboardInterrupt):
                print("\nOperation cancelled.")
                return CommandResult.continue_result("Operation cancelled")

    def can_execute(self, context: CommandContext) -> bool:
        """Check if there are new files to process."""
        files_only_local = context.data.get(FileCategory.NEW_FILES.value, set())
        return len(files_only_local) > 0


class AddAllNewFilesCommand(MenuCommand):
    """Command to add all new files."""

    def __init__(self):
        super().__init__("add_all_new", "Add all new files to database")

    def execute(self, context: CommandContext) -> CommandResult:
        """Execute the add all new files command."""
        files_only_local = context.data.get(FileCategory.NEW_FILES.value, set())
        user_interface = context.user_interface

        if not files_only_local:
            return CommandResult.continue_result("No new files to add")

        if user_interface and user_interface.confirm_action(
            f"Add all {len(files_only_local)} new files to database?"
        ):
            return CommandResult.custom_action_result(
                IngestionAction.ADD_FILES.value,
                {
                    "action_type": IngestionAction.ADD_FILES.value,
                    "files": files_only_local,
                },
                f"Adding {len(files_only_local)} new files",
            )
        else:
            return CommandResult.continue_result("File addition cancelled")

    def can_execute(self, context: CommandContext) -> bool:
        """Check if there are new files to add."""
        files_only_local = context.data.get(FileCategory.NEW_FILES.value, set())
        return len(files_only_local) > 0


class AddSpecificFileCommand(MenuCommand):
    """Command to add a specific file."""

    def __init__(self):
        super().__init__("add_specific_file", "Add a specific file to database")

    def execute(self, context: CommandContext) -> CommandResult:
        """Execute the add specific file command."""
        # Implementation would go here
        return CommandResult.continue_result("Add specific file command executed")

    def can_execute(self, context: CommandContext) -> bool:
        """Check if the command can be executed."""
        return True


class AddFilesByTypeCommand(MenuCommand):
    """Command to add files by type."""

    def __init__(self):
        super().__init__("add_files_by_type", "Add files by type to database")

    def execute(self, context: CommandContext) -> CommandResult:
        """Execute the add files by type command."""
        # Implementation would go here
        return CommandResult.continue_result("Add files by type command executed")

    def can_execute(self, context: CommandContext) -> bool:
        """Check if the command can be executed."""
        return True


class ClearDatabaseCommand(MenuCommand):
    """Command to clear the database."""

    def __init__(self):
        super().__init__("clear_database", "Clear all or specific files from database")

    def execute(self, context: CommandContext) -> CommandResult:
        """Execute the clear database command."""
        # Implementation would go here
        return CommandResult.continue_result("Clear database command executed")

    def can_execute(self, context: CommandContext) -> bool:
        """Check if the command can be executed."""
        return True


class HandleExistingFilesCommand(MenuCommand):
    """Command to handle existing files."""

    def __init__(self):
        super().__init__(
            "handle_existing_files",
            "Manage files that exist in both local folder and database",
        )

    def execute(self, context: CommandContext) -> CommandResult:
        """Execute the handle existing files command."""
        # Implementation would go here
        return CommandResult.continue_result("Handle existing files command executed")

    def can_execute(self, context: CommandContext) -> bool:
        """Check if the command can be executed."""
        return True


class HandleOrphanedFilesCommand(MenuCommand):
    """Command to handle orphaned files."""

    def __init__(self):
        super().__init__(
            "handle_orphaned_files", "Manage files that exist only in database"
        )

    def execute(self, context: CommandContext) -> CommandResult:
        """Execute the handle orphaned files command."""
        # Implementation would go here
        return CommandResult.continue_result("Handle orphaned files command executed")

    def can_execute(self, context: CommandContext) -> bool:
        """Check if the command can be executed."""
        return True
