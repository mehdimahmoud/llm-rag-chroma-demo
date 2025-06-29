from enum import Enum, auto

"""
Enums for the ingestion domain.
"""


class IngestionAction(Enum):
    """Actions specific to document ingestion."""

    PROCESS_FILES = "process_files"
    ADD_FILES = "add_files"
    REPLACE_FILES = "replace_files"
    DELETE_FILES = "delete_files"
    CLEAR_DATABASE = "clear_database"
    SKIP_FILES = "skip_files"
    SHOW_COMPARISON = "show_comparison"
    PREVIEW_PLAN = "preview_plan"
    CUSTOM_SELECTION = "custom_selection"


class FileCategory(Enum):
    """Categories for file classification."""

    NEW_FILES = "new_files"  # Files only in local folder
    EXISTING_FILES = "existing_files"  # Files in both local and database
    ORPHANED_FILES = "orphaned_files"  # Files only in database


class FileOperation(Enum):
    """Types of file operations."""

    ADD = "add"
    REPLACE = "replace"
    DELETE = "delete"
    KEEP = "keep"
    SKIP = "skip"


class BulkOperation(Enum):
    """Types of bulk operations."""

    PROCESS_ALL = "process_all"
    CLEAR_AND_ADD_ALL = "clear_and_add_all"
    SKIP_ALL = "skip_all"
    ADD_BY_TYPE = "add_by_type"
    DELETE_BY_TYPE = "delete_by_type"


class MenuSection(Enum):
    """Sections of the ingestion menu."""

    NEW_FILES = "new_files"
    EXISTING_FILES = "existing_files"
    ORPHANED_FILES = "orphaned_files"
    BULK_OPERATIONS = "bulk_operations"
    ADVANCED_OPTIONS = "advanced_options"
    CLEAR_DATABASE = "clear_database"
    ADD_FILES_BY_TYPE = "add_files_by_type"
    ADD_SPECIFIC_FILE = "add_specific_file"


class ConfirmationType(Enum):
    """Types of user confirmations."""

    ADD_FILES = "add_files"
    REPLACE_FILES = "replace_files"
    DELETE_FILES = "delete_files"
    CLEAR_DATABASE = "clear_database"
    PROCESS_FILES = "process_files"
    SKIP_FILES = "skip_files"


class FileType(Enum):
    """Supported file types."""

    PDF = "pd"
    TXT = "txt"
    DOCX = "docx"
    MD = "md"
    ALL = "all"


class ProcessingStatus(Enum):
    """Status of file processing."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class FileActionChoice(Enum):
    """Choices for file actions."""

    ADD = "add"
    SKIP = "skip"
    DELETE = "delete"
    REPLACE = "replace"
    KEEP = "keep"


class BulkActionChoice(Enum):
    """Choices for bulk actions."""

    ADD_ALL = "add_all"
    ADD_SPECIFIC = "add_specific"
    ADD_ALL_BY_TYPE = "add_all_by_type"
    SKIP_ALL = "skip_all"
    SKIP_SPECIFIC = "skip_specific"
    SKIP_ALL_BY_TYPE = "skip_all_by_type"
    DELETE_ALL = "delete_all"
    DELETE_SPECIFIC = "delete_specific"
    DELETE_ALL_BY_TYPE = "delete_all_by_type"


class MainMenuChoice(Enum):
    """Main menu choices."""

    EXIT = "0"
    PROCESS_NEW_FILES = "1"
    HANDLE_FILES_IN_BOTH_PLACES = "2"
    HANDLE_FILES_ONLY_IN_DB = "3"
    BULK_OPERATIONS = "4"
    ADVANCED_OPTIONS = "5"
    CLEAR_DATABASE = "6"
    ADD_FILES_BY_TYPE = "7"
    ADD_SPECIFIC_FILE = "8"


class NewFilesMenuChoice(Enum):
    """New files menu choices."""

    BACK = "0"
    ADD_ALL = "1"
    ADD_SPECIFIC = "2"
    ADD_BY_TYPE = "3"
    SKIP_ALL = "4"


class FilesInBothPlacesMenuChoice(Enum):
    """Files in both places menu choices."""

    BACK = "0"
    REPLACE_ALL = "1"
    REPLACE_SPECIFIC = "2"
    REPLACE_BY_TYPE = "3"
    KEEP_ALL = "4"
    KEEP_SPECIFIC = "5"
    KEEP_BY_TYPE = "6"


class FilesOnlyInDbMenuChoice(Enum):
    """Files only in database menu choices."""

    BACK = "0"
    DELETE_ALL = "1"
    DELETE_SPECIFIC = "2"
    DELETE_BY_TYPE = "3"
    KEEP_ALL = "4"


class BulkOperationsMenuChoice(Enum):
    """Bulk operations menu choices."""

    BACK = "0"
    PROCESS_ALL = "1"
    CLEAR_AND_REBUILD = "2"
    SKIP_ALL = "3"


class AdvancedOptionsMenuChoice(Enum):
    """Advanced options menu choices."""

    BACK = "0"
    SHOW_DETAILED_COMPARISON = "1"
    PREVIEW_PROCESSING_PLAN = "2"
    CUSTOM_SELECTION = "3"
