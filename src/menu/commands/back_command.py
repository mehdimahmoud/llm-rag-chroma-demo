from ...menu.core.menu_command import CommandResult
from ..core.enums import CommandType, MenuAction
from ..core.menu_command import CommandContext, CommandResult, MenuCommand

"""
Back command that returns to the previous menu.
"""


class BackCommand(MenuCommand):
    """Command to go back to the previous menu."""

    def __init__(self):
        super().__init__("back", "Return to the previous menu", CommandType.NAVIGATION)

    def execute(self, context: CommandContext) -> CommandResult:
        """Execute the back command."""
        return CommandResult.back_result("Returning to previous menu")

    def can_execute(self, context: CommandContext) -> bool:
        """Back command can always be executed."""
        return True
