"""
Concrete menu command item that wraps a command.
"""
from typing import Any, Optional

from ..core.menu_command import CommandContext, MenuCommand
from ..core.menu_component import MenuComponent


class MenuCommandItem(MenuComponent):
    """A menu item that wraps a command."""

    def __init__(
        self, command: MenuCommand, choice_id: str, title: str, description: str = ""
    ):
        super().__init__(title, description)
        self.command = command
        self.choice_id = choice_id

    def display(self) -> None:
        """Display the command item."""
        # Command items don't display themselves - they're displayed by their parent
        pass

    def handle_input(
        self, choice: str, context: Optional[CommandContext] = None
    ) -> Any:
        """Handle input by executing the command."""
        if choice == self.choice_id:
            # Use the provided context or create a generic one if none provided
            if context is None:
                context = CommandContext()
            return self.command.execute(context)
        else:
            raise ValueError(f"Invalid choice: {choice}")

    def can_execute(self, context: CommandContext) -> bool:
        """Check if the command can be executed."""
        return self.command.can_execute(context)
