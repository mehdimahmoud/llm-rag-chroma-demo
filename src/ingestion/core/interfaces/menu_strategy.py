"""
Abstract interface for menu handling strategies.
"""
from abc import ABC, abstractmethod
from typing import List

from ...core.models.menu_context import MenuContext, MenuResult


class MenuStrategy(ABC):
    """Abstract interface for menu handling strategies."""

    @abstractmethod
    def handle(self, context: MenuContext) -> MenuResult:
        """
        Handle the menu logic and return selected files or navigation action.

        Args:
            context: Menu context with file sets and dependencies

        Returns:
            MenuResult with files to process or navigation action
        """
        pass

    @abstractmethod
    def get_menu_title(self) -> str:
        """Get the title for this menu."""
        pass

    @abstractmethod
    def get_menu_options(self) -> List[str]:
        """Get the list of menu options to display."""
        pass
