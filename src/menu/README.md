# Generic Menu System

A reusable, domain-agnostic menu framework for building interactive CLI applications.

## Overview

The Generic Menu System provides a scalable, maintainable approach to building complex menu hierarchies using design patterns. It is designed to be **completely independent** of any specific domain and can be used to build menus for any CLI application.

## Core Architecture

### Design Patterns Used

- **Component Pattern** - Hierarchical menu structure
- **Command Pattern** - Encapsulated actions
- **Builder Pattern** - Complex menu construction
- **Orchestrator Pattern** - Menu navigation management

### Core Components

1. **MenuComponent** - Abstract base for all menu elements
2. **MenuCommand** - Commands that can be executed
3. **MenuBuilder** - Builder pattern for constructing menus
4. **MenuOrchestrator** - Generic menu navigation
5. **CommandResult** - Results from command execution

## Enum System

The menu system uses enums to replace hardcoded strings, making it more maintainable and type-safe.

### Core Enums

```python
from src.menu.core.enums import MenuAction, MenuChoice, CommandType, MenuStyle

# Menu actions
MenuAction.CONTINUE    # Continue with current menu
MenuAction.BACK        # Go back to previous menu
MenuAction.EXIT        # Exit the application
MenuAction.CUSTOM_ACTION # Custom domain-specific action

# Standard menu choices
MenuChoice.BACK        # "0" - Back/Exit
MenuChoice.HELP        # "h" - Help
MenuChoice.CANCEL      # "c" - Cancel

# Command types
CommandType.NAVIGATION # Navigation commands (back, exit)
CommandType.ACTION     # Action commands (process, create)
CommandType.DISPLAY    # Display commands (help, show)
CommandType.CUSTOM     # Custom commands

# Menu display styles
MenuStyle.SIMPLE       # Simple format
MenuStyle.DETAILED     # Detailed format with descriptions
MenuStyle.COMPACT      # Compact format
MenuStyle.VERBOSE      # Verbose format with icons
```

## File Structure

```
src/menu/
├── README.md              # This documentation
├── __init__.py           # Package initialization
├── core/                 # Core interfaces and base classes
│   ├── __init__.py
│   ├── menu_component.py # Abstract menu component
│   ├── menu_command.py   # Command interface
│   ├── menu_builder.py   # Builder pattern
│   └── enums.py         # Enum definitions
├── commands/             # Generic command implementations
│   ├── __init__.py
│   ├── back_command.py   # Back navigation
│   ├── exit_command.py   # Exit application
│   └── help_command.py   # Help information
├── concrete/             # Concrete implementations
│   ├── __init__.py
│   ├── menu_group.py     # Menu group component
│   └── menu_command_item.py # Command menu item
└── orchestrators/        # Menu orchestrators
    ├── __init__.py
    └── menu_orchestrator.py # Generic orchestrator
```

## Quick Start

### Basic Menu Creation

```python
from src.menu.core.menu_builder import MenuBuilder
from src.menu.commands.back_command import BackCommand
from src.menu.commands.exit_command import ExitCommand
from src.menu.core.enums import MenuChoice

# Create menu builder
builder = MenuBuilder()

# Build a simple menu
builder.start_menu("MAIN MENU", "Choose an option")
builder.add_command(MyCommand(), "1", "My Action", "Description")
builder.add_exit_command("Exit")  # Uses MenuChoice.EXIT.value internally

# Get the menu
menu = builder.build()
```

### Creating Custom Commands

```python
from src.menu.core.menu_command import MenuCommand, CommandContext, CommandResult
from src.menu.core.enums import CommandType, MenuAction

class MyCustomCommand(MenuCommand):
    def __init__(self):
        super().__init__("my_command", "Description of my command", CommandType.ACTION)
    
    def execute(self, context: CommandContext) -> CommandResult:
        # Your implementation here
        return CommandResult.continue_result("Command executed")
    
    def can_execute(self, context: CommandContext) -> bool:
        return True
```

### Using the Menu Orchestrator

```python
from src.menu.orchestrators.menu_orchestrator import MenuOrchestrator
from src.menu.core.enums import MenuAction

# Create orchestrator
orchestrator = MenuOrchestrator()

# Create context factory
def context_factory():
    return CommandContext(data={"my_data": "value"})

# Run the menu system
orchestrator.run(root_menu, context_factory)
```

## Core Interfaces

### MenuCommand

The base interface for all commands:

```python
class MenuCommand(ABC):
    def __init__(self, name: str, description: str = "", command_type: CommandType = CommandType.ACTION):
        self.name = name
        self.description = description
        self.command_type = command_type
    
    @abstractmethod
    def execute(self, context: CommandContext) -> Any:
        """Execute the command and return result."""
        pass
    
    @abstractmethod
    def can_execute(self, context: CommandContext) -> bool:
        """Check if command can be executed."""
        pass
```

### CommandContext

Generic context passed to all commands:

```python
@dataclass
class CommandContext:
    """Generic context data passed to commands."""
    data: Dict[str, Any] = None        # Domain-specific data
    user_interface: Any = None         # Generic UI interface
    logger: Any = None                 # Generic logging interface
```

### CommandResult

Results returned by commands using enums:

```python
class CommandResult:
    def __init__(self, success: bool, data: Any = None, message: str = "", action: MenuAction = MenuAction.CONTINUE):
        self.success = success
        self.data = data
        self.message = message
        self.action = action
    
    @classmethod
    def continue_result(cls, message: str = "") -> 'CommandResult':
        return cls(True, action=MenuAction.CONTINUE, message=message)
    
    @classmethod
    def back_result(cls, message: str = "") -> 'CommandResult':
        return cls(True, action=MenuAction.BACK, message=message)
    
    @classmethod
    def exit_result(cls, message: str = "") -> 'CommandResult':
        return cls(True, action=MenuAction.EXIT, message=message)
    
    @classmethod
    def custom_action_result(cls, action: str, data: Any = None, message: str = "") -> 'CommandResult':
        return cls(True, data=data, action=MenuAction.CUSTOM_ACTION, message=message)
```

## Built-in Commands

### Navigation Commands

- **BackCommand** - Go back to previous menu (uses `CommandType.NAVIGATION`)
- **ExitCommand** - Exit the application (uses `CommandType.NAVIGATION`)
- **HelpCommand** - Display help information (uses `CommandType.DISPLAY`)

These commands are automatically available in all menus.

## Implementing for a New Domain

### Step 1: Create Domain-Specific Enums

```python
# my_domain/enums.py
from enum import Enum

class MyDomainAction(Enum):
    CREATE_ITEM = "create_item"
    UPDATE_ITEM = "update_item"
    DELETE_ITEM = "delete_item"

class ItemStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
```

### Step 2: Create Domain-Specific Commands

```python
# my_domain/commands/my_commands.py
from src.menu.core.menu_command import MenuCommand, CommandContext, CommandResult
from src.menu.core.enums import CommandType, MenuAction
from ..enums import MyDomainAction

class CreateItemCommand(MenuCommand):
    def __init__(self):
        super().__init__("create_item", "Create a new item", CommandType.ACTION)
    
    def execute(self, context: CommandContext) -> CommandResult:
        # Extract domain-specific data
        item_data = context.data.get('item_data', {})
        
        # Perform domain-specific logic
        result = self.create_item(item_data)
        
        # Return domain-specific result using enums
        return CommandResult.custom_action_result(
            MyDomainAction.CREATE_ITEM.value, 
            result, 
            "Item created successfully"
        )
    
    def can_execute(self, context: CommandContext) -> bool:
        return context.data.get('can_create', False)
```

### Step 3: Create Domain-Specific Menu Builder

```python
# my_domain/builders/my_menu_builder.py
from src.menu.core.menu_builder import MenuBuilder
from src.menu.core.enums import MenuChoice
from ..commands.my_commands import CreateItemCommand

class MyDomainMenuBuilder(MenuBuilder):
    def build_main_menu(self):
        self.reset()
        self.start_menu("MY DOMAIN MENU", "Choose an option")
        
        self.add_command(
            CreateItemCommand(), "1", 
            "Create Item", 
            "Create a new item"
        )
        
        # Use enum for standard choices
        self.add_exit_command("Exit")  # Uses MenuChoice.EXIT.value
        return self.build()
```

### Step 4: Create Domain-Specific Orchestrator

```python
# my_domain/orchestrators/my_menu_orchestrator.py
from src.menu.orchestrators.menu_orchestrator import MenuOrchestrator
from src.menu.core.menu_command import CommandContext
from src.menu.core.enums import MenuAction
from ..builders.my_menu_builder import MyDomainMenuBuilder
from ..enums import ItemStatus

class MyDomainMenuOrchestrator:
    def __init__(self, user_interface, logger=None):
        self.user_interface = user_interface
        self.logger = logger
        self.menu_builder = MyDomainMenuBuilder()
        self.menu_orchestrator = MenuOrchestrator(user_interface, logger)
    
    def run(self):
        # Build domain-specific menu
        main_menu = self.menu_builder.build_main_menu()
        
        # Create domain-specific context factory
        def context_factory():
            return self._create_domain_context()
        
        # Use generic orchestrator with domain context
        self.menu_orchestrator.run(main_menu, context_factory)
    
    def _create_domain_context(self) -> CommandContext:
        """Create domain-specific command context."""
        context = CommandContext()
        context.data = {
            'item_data': self.get_item_data(),
            'can_create': self.can_create_items(),
            'item_status': ItemStatus.ACTIVE.value  # Using enum
        }
        context.user_interface = self.user_interface
        context.logger = self.logger
        return context
```

## Testing

### Testing Generic Commands

```python
from src.menu.core.enums import MenuAction

def test_back_command():
    command = BackCommand()
    context = CommandContext()
    result = command.execute(context)
    assert result.action == MenuAction.BACK
```

### Testing Domain Commands

```python
from src.menu.core.enums import MenuAction

def test_create_item_command():
    command = CreateItemCommand()
    context = CommandContext(data={'item_data': {'name': 'test'}, 'can_create': True})
    result = command.execute(context)
    assert result.action == MenuAction.CUSTOM_ACTION
    assert result.data is not None
```

### Testing Menu Orchestrator

```python
from src.menu.core.enums import MenuAction

def test_menu_orchestrator():
    orchestrator = MenuOrchestrator()
    menu = create_test_menu()
    
    # Mock user input
    with patch('builtins.input', return_value=MenuChoice.EXIT.value):
        orchestrator.run(menu)
```

## Best Practices

### 1. Use Enums Instead of Strings
```python
# ✅ Good - Using enums
return CommandResult.back_result("Going back")

# ❌ Bad - Using hardcoded strings
return CommandResult(True, action="back", message="Going back")
```

### 2. Define Domain-Specific Enums
```python
# ✅ Good - Domain-specific actions
class MyDomainAction(Enum):
    CREATE_ITEM = "create_item"
    UPDATE_ITEM = "update_item"

# ❌ Bad - Using generic strings
return CommandResult.custom_action_result("create_item", data)
```

### 3. Use Enum Values in Context Data
```python
# ✅ Good - Using enum values
context.data = {
    'status': ItemStatus.ACTIVE.value,
    'action': MyDomainAction.CREATE_ITEM.value
}

# ❌ Bad - Using hardcoded strings
context.data = {
    'status': 'active',
    'action': 'create_item'
}
```

### 4. Test with Enum Values
```python
# ✅ Good - Testing with enums
assert result.action == MenuAction.BACK
assert context.data['status'] == ItemStatus.ACTIVE.value

# ❌ Bad - Testing with strings
assert result.action == "back"
assert context.data['status'] == "active"
```

## Extending the Framework

### Adding New Generic Commands

```python
# src/menu/commands/help_command.py
from src.menu.core.enums import CommandType, MenuAction

class HelpCommand(MenuCommand):
    def __init__(self):
        super().__init__("help", "Display help information", CommandType.DISPLAY)
    
    def execute(self, context: CommandContext) -> CommandResult:
        return CommandResult.continue_result("Help information")
    
    def can_execute(self, context: CommandContext) -> bool:
        return True
```

### Adding New Menu Components

```python
# src/menu/concrete/menu_submenu.py
from src.menu.core.enums import MenuType

class MenuSubmenu(MenuComponent):
    def __init__(self, title: str, description: str = ""):
        super().__init__(title, description)
        self.menu_type = MenuType.SUBMENU
    
    def display(self) -> None:
        # Custom display logic
        pass
    
    def handle_input(self, choice: str) -> Any:
        # Custom input handling
        pass
```

## Future Enhancements

1. **Plugin System** - Dynamic command loading
2. **Menu Templates** - Reusable menu patterns
3. **Command Chaining** - Sequential command execution
4. **Menu Validation** - Input validation framework
5. **Internationalization** - Multi-language support

## Conclusion

The Generic Menu System provides a robust foundation for building complex, scalable menu interfaces. Its domain-agnostic design and enum-based approach ensure reusability across different applications while maintaining clean, testable, and maintainable code. 