from ...menu.core.menu_command import CommandResult
from ..core.enums import CommandType, MenuAction
from ..core.menu_command import CommandContext, CommandResult, MenuCommand

"""
Help command that displays help information.
"""


class HelpCommand(MenuCommand):
    """Command to display help information."""

    def __init__(self):
        super().__init__("help", "Display help information", CommandType.DISPLAY)

    def execute(self, context: CommandContext) -> CommandResult:
        """Execute the help command."""
        help_text = self._get_help_text(context)
        return CommandResult.continue_result(help_text)

    def can_execute(self, context: CommandContext) -> bool:
        """Help command can always be executed."""
        return True

    def _get_help_text(self, context: CommandContext) -> str:
        """Get help text based on context."""
        return """
Help Information:
- Use number keys to select menu options
- Type '0' to go back or exit
- Type 'h' for help
- Type 'c' to cancel current operation
        """.strip()
