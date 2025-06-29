from ...menu.core.menu_command import CommandResult
from ..core.enums import CommandType, MenuAction
from ..core.menu_command import CommandContext, CommandResult, MenuCommand

"""
Exit command that terminates the application.
"""


class ExitCommand(MenuCommand):
    """Command to exit the application."""

    def __init__(self):
        super().__init__("exit", "Exit the application", CommandType.NAVIGATION)

    def execute(self, context: CommandContext) -> CommandResult:
        """Execute the exit command."""
        return CommandResult.exit_result("Exiting application")

    def can_execute(self, context: CommandContext) -> bool:
        """Exit command can always be executed."""
        return True
