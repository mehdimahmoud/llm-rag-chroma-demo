import os
import structlog

from typing import Any, Optional

from ...menu.core.enums import InputType
from ...menu.core.menu_command import CommandResult
from ...menu.concrete.menu_group import MenuGroup
from ..core.enums import MenuAction, MenuChoice, MenuStatus
from ..core.menu_command import CommandContext, MenuCommand
from ..core.menu_component import MenuComponent
from ..core.menu_registry import MenuRegistry

"""
Orchestrator for menu system operations.
"""


class MenuOrchestrator:
    """Generic orchestrator for menu navigation."""

    def __init__(self, user_interface=None, _logger=None):
        self.user_interface = user_interface
        self.logger = structlog.get_logger(__name__)

    def run(self, root_menu: MenuGroup, context_factory=None) -> None:
        """
        Run the menu system starting from the root menu.

        Args:
            root_menu: The root menu component
            context_factory: Optional factory function to create command context
        """
        self.logger.info("Starting menu orchestrator")

        current_menu = root_menu

        while True:
            try:
                # Create context if factory is provided
                context = None
                if context_factory:
                    context = context_factory()

                # Display current menu
                current_menu.display()

                # Get user choice
                choice = self._get_user_choice(current_menu)

                # Handle the choice
                result = current_menu.handle_input(choice, context)

                # Process the result
                if self._process_result(result, context):
                    break

            except KeyboardInterrupt:
                self.logger.info("User interrupted the process")
                break
            except Exception as e:
                self.logger.error("Error in menu orchestrator: {e}")
                break

    def _get_user_choice(self, menu: MenuGroup) -> str:
        """Get user choice from the menu."""
        if hasattr(menu, "get_valid_choices"):
            valid_choices = menu.get_valid_choices()
            while True:
                choice = input(f"Enter your choice {valid_choices}: ").strip()
                if choice in valid_choices:
                    return choice
                print("Invalid choice. Please enter one of: {valid_choices}")
        else:
            return input("Enter your choice: ").strip()

    def _process_result(self, result, context: Optional[CommandContext]) -> bool:
        """Process the result from menu handling."""
        if isinstance(result, CommandResult):
            if result.action == MenuAction.EXIT:
                self.logger.info("User chose to exit")
                return True
            elif result.action == MenuAction.BACK:
                self.logger.info("Going back to previous menu")
                return False
            elif result.action == MenuAction.CONTINUE:
                self.logger.info(result.message)
                return False
            elif result.action == MenuAction.CUSTOM_ACTION:
                # Handle custom actions
                self.logger.info("Custom action: {result.message}")
                return False
        else:
            self.logger.info("Menu result: {result}")
            return False

        return False

    def get_input(self, prompt: str, input_type: InputType = InputType.CHOICE) -> Any:
        """Get user input with type validation."""
        if input_type == InputType.CONFIRMATION:
            return self._get_confirmation(prompt)
        elif input_type == InputType.NUMBER:
            return self._get_number(prompt)
        elif input_type == InputType.MULTI_SELECT:
            return self._get_multi_select(prompt)
        else:
            return input(prompt).strip()

    def _get_confirmation(self, prompt: str) -> bool:
        """Get user confirmation."""
        while True:
            response = input("{prompt} (y/n): ").strip().lower()
            if response in ["y", "yes"]:
                return True
            elif response in ["n", "no"]:
                return False
            print("Please enter 'y' or 'n'")

    def _get_number(self, prompt: str) -> int:
        """Get numeric input from user."""
        while True:
            try:
                return int(input(prompt).strip())
            except ValueError:
                print("Please enter a valid number")

    def _get_multi_select(self, prompt: str) -> list:
        """Get multiple selections from user."""
        response = input("{prompt} (comma-separated): ").strip()
        return [item.strip() for item in response.split(",") if item.strip()]
