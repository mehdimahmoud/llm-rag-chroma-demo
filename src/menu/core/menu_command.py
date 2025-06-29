"""
Command pattern implementation for menu actions.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict

from .enums import CommandType, MenuAction


@dataclass
class CommandContext:
    """Generic context data passed to commands."""

    # Generic data that any command might need
    data: Dict[str, Any] = None
    user_interface: Any = None
    logger: Any = None
    vector_store: Any = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


class MenuCommand(ABC):
    """Abstract command interface for menu actions."""

    def __init__(
        self,
        name: str,
        description: str = "",
        command_type: CommandType = CommandType.ACTION,
    ):
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

    def get_help_text(self) -> str:
        """Get help text for this command."""
        return f"{self.name}: {self.description}"


class CommandResult:
    """Result from command execution."""

    def __init__(
        self,
        success: bool,
        data: Any = None,
        message: str = "",
        action: MenuAction = MenuAction.CONTINUE,
    ):
        self.success = success
        self.data = data
        self.message = message
        self.action = action

    @classmethod
    def continue_result(cls, message: str = "") -> "CommandResult":
        return cls(True, action=MenuAction.CONTINUE, message=message)

    @classmethod
    def back_result(cls, message: str = "") -> "CommandResult":
        return cls(True, action=MenuAction.BACK, message=message)

    @classmethod
    def exit_result(cls, message: str = "") -> "CommandResult":
        return cls(True, action=MenuAction.EXIT, message=message)

    @classmethod
    def custom_action_result(
        cls, action: str, data: Any = None, message: str = ""
    ) -> "CommandResult":
        return cls(True, data=data, action=MenuAction.CUSTOM_ACTION, message=message)
