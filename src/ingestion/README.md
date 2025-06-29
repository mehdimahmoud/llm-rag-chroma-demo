# Document Ingestion System

This document describes the document ingestion system and how it uses the generic menu framework.

## Overview

The document ingestion system is responsible for processing documents (PDFs, text files) and storing them in a vector database for RAG (Retrieval-Augmented Generation) applications. It uses the **Generic Menu System** to provide an interactive user interface.

## Architecture

### How It Uses the Generic Menu System

The ingestion system implements the generic menu framework by:

1. **Creating domain-specific commands** that inherit from `MenuCommand`
2. **Building ingestion-specific menus** using `MenuBuilder`
3. **Providing ingestion context** to the generic orchestrator

### File Structure

```
src/ingestion/
├── README.md                    # This documentation
├── commands/                    # Ingestion-specific commands
│   ├── process_files_command.py # File processing commands
│   └── ...
├── builders/                    # Ingestion menu builders
│   ├── ingestion_menu_builder.py # Builds ingestion menus
│   └── ...
├── orchestrators/               # Ingestion orchestrators
│   ├── ingestion_menu_orchestrator.py # Uses generic menu system
│   └── ...
├── services/                    # Core ingestion services
│   ├── document_loader.py       # Document loading
│   ├── text_extractor_factory.py # Text extraction
│   ├── text_chunker.py          # Text chunking
│   ├── embedding_generator.py   # Embedding generation
│   └── ...
├── core/                        # Core interfaces
│   ├── interfaces/              # Abstract interfaces
│   ├── models/                  # Data models
│   └── enums/                   # Enumerations
└── models/                      # Domain models
    ├── document.py              # Document models
    └── enums.py                 # File types, etc.
```

## Ingestion Commands

### File Processing Commands

- **ProcessNewFilesCommand** - Handle files that exist only in local folder
- **HandleExistingFilesCommand** - Handle files that exist in both local folder and database
- **HandleOrphanedFilesCommand** - Handle files that exist only in database

### Database Operations

- **ClearDatabaseCommand** - Clear all or specific files from database
- **AddFilesByTypeCommand** - Add files by type from local folder
- **AddSpecificFileCommand** - Add a specific file from local folder

### Example Command Implementation

```python
class ProcessNewFilesCommand(MenuCommand):
    def __init__(self):
        super().__init__("process_new_files", "Process files that exist only in local folder")
    
    def execute(self, context: CommandContext) -> CommandResult:
        # Extract ingestion-specific data
        files_only_local = context.data.get('files_only_local', set())
        
        if not files_only_local:
            return CommandResult.continue_result("No new files to process")
        
        # Return ingestion-specific action
        return CommandResult.custom_action_result(
            "process_files", 
            files_only_local, 
            f"Processing {len(files_only_local)} new files"
        )
    
    def can_execute(self, context: CommandContext) -> bool:
        files_only_local = context.data.get('files_only_local', set())
        return len(files_only_local) > 0
```

## Ingestion Menu Builder

The ingestion system creates its menus using the generic `MenuBuilder`:

```python
class IngestionMenuBuilder(MenuBuilder):
    def build_main_menu(self) -> MenuComponent:
        self.reset()
        self.start_menu("DOCUMENT INGESTION MENU", "Main menu for document ingestion operations")
        
        # Add ingestion-specific commands
        self.add_command(
            ProcessNewFilesCommand(), "1", 
            "Process new files", 
            "Add files that exist only in local folder"
        )
        
        self.add_command(
            HandleExistingFilesCommand(), "2", 
            "Handle existing files", 
            "Manage files that exist in both local folder and database"
        )
        
        # Add generic navigation
        self.add_exit_command("Exit (cancel all operations)")
        
        return self.build()
```

## Ingestion Context

The ingestion system provides domain-specific context to the generic menu system:

```python
def _create_ingestion_context(self) -> CommandContext:
    """Create ingestion-specific command context."""
    context = CommandContext()
    
    # Add ingestion-specific data
    context.data = {
        'files_only_local': self.get_files_only_local(),
        'files_both': self.get_files_both(),
        'files_only_db': self.get_files_only_db(),
        'total_files_in_db': self.get_total_files_in_db(),
        'total_files_in_local': self.get_total_files_in_local()
    }
    
    # Add dependencies
    context.user_interface = self.user_interface
    context.logger = self.logger
    
    return context
```

## Ingestion Orchestrator

The ingestion system uses the generic `MenuOrchestrator` with domain-specific configuration:

```python
class IngestionMenuOrchestrator(IngestionOrchestrator):
    def __init__(self, user_interface, vector_store, logger=None):
        self.user_interface = user_interface
        self.vector_store = vector_store
        self.logger = logger
        self.menu_builder = IngestionMenuBuilder()
        self.menu_orchestrator = MenuOrchestrator(user_interface, logger)
    
    def ingest_documents(self, config: IngestionConfig) -> IngestionResult:
        # Build ingestion-specific menu
        main_menu = self.menu_builder.build_main_menu()
        
        # Create ingestion-specific context factory
        def context_factory():
            return self._create_ingestion_context()
        
        # Use generic orchestrator with ingestion context
        self.menu_orchestrator.run(main_menu, context_factory)
        
        # Return ingestion result
        return self._create_ingestion_result()
```

## File Categorization

The ingestion system categorizes files into three groups:

1. **Files only in local folder** - New files to be added
2. **Files in both places** - Existing files that may need updating
3. **Files only in database** - Orphaned files that may need deletion

This categorization is passed to the generic menu system through the context.

## Supported File Types

- **PDF files** - Processed using PDF text extraction
- **Text files** - Processed directly
- **Extensible** - New file types can be added

## Integration with Generic Menu System

The ingestion system demonstrates how to properly use the generic menu framework:

1. **Inherit from generic interfaces** - All commands inherit from `MenuCommand`
2. **Use generic builders** - Menu construction uses `MenuBuilder`
3. **Provide domain context** - Ingestion-specific data passed through `CommandContext`
4. **Use generic orchestrator** - Navigation handled by `MenuOrchestrator`

## Testing

### Testing Ingestion Commands

```python
def test_process_new_files_command():
    command = ProcessNewFilesCommand()
    context = CommandContext(data={'files_only_local': {'file1.pdf'}})
    result = command.execute(context)
    assert result.action == "process_files"
    assert result.data == {'file1.pdf'}
```

### Testing Ingestion Menu Builder

```python
def test_ingestion_menu_builder():
    builder = IngestionMenuBuilder()
    menu = builder.build_main_menu()
    assert menu is not None
    # Test menu structure
```

## Conclusion

The ingestion system serves as an excellent example of how to properly implement the generic menu framework for a specific domain. It demonstrates clean separation of concerns, proper inheritance, and effective use of the generic interfaces. 