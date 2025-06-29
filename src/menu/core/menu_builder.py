from typing import Optional, List

from ..commands.back_command import BackCommand
from ..commands.exit_command import ExitCommand
from ..commands.help_command import HelpCommand
from ..concrete.menu_command_item import MenuCommandItem
from ..concrete.menu_group import MenuGroup
from .enums import MenuAction, MenuChoice
from .menu_command import CommandContext, MenuCommand
from .menu_component import MenuComponent, MenuItem

"""
Menu builder using Builder pattern for constructing complex menus.
"""


class MenuBuilder:
    """Builder for constructing menu hierarchies."""

    def __init__(self):
        self._root: Optional[MenuGroup] = None
        self._current: Optional[MenuGroup] = None
        self._stack: List[MenuGroup] = []

    def start_menu(self, title: str, description: str = "") -> "MenuBuilder":
        """Start building a new menu."""
        menu = MenuGroup(title, description)

        if self._root is None:
            self._root = menu

        if self._current is not None:
            self._current.add_child(menu)
            self._stack.append(self._current)

        self._current = menu
        return self

    def add_command(
        self, command: MenuCommand, choice_id: str, title: str, description: str = ""
    ) -> "MenuBuilder":
        """Add a command to the current menu."""
        if self._current is None:
            raise ValueError("No menu has been started. Call start_menu() first.")
            
        # Create the command item
        command_item = MenuCommandItem(command, choice_id, title, description)

        # Create a menu item for the group
        menu_item = MenuItem(
            id=choice_id,
            title=title,
            description=description,
            enabled=True,
            visible=True,
        )

        # Add to the current menu group
        if hasattr(self._current, "add_menu_item"):
            self._current.add_menu_item(menu_item, command_item)
        else:
            # Fallback for non-group menus
            self._current.add_child(command_item)

        return self

    def add_back_command(self, title: str = "Back to main menu") -> "MenuBuilder":
        """Add a back command to the current menu."""
        back_cmd = BackCommand()
        self.add_command(back_cmd, MenuChoice.BACK.value, title)
        return self

    def add_exit_command(self, title: str = "Exit") -> "MenuBuilder":
        """Add an exit command to the current menu."""
        exit_cmd = ExitCommand()
        self.add_command(exit_cmd, MenuChoice.EXIT.value, title)
        return self

    def add_help_command(self, title: str = "Help") -> "MenuBuilder":
        """Add a help command to the current menu."""
        help_cmd = HelpCommand()
        self.add_command(help_cmd, MenuChoice.HELP.value, title)
        return self

    def end_menu(self) -> "MenuBuilder":
        """End the current menu and go back to parent."""
        if self._stack:
            self._current = self._stack.pop()
        return self

    def build(self) -> MenuGroup:
        """Build and return the complete menu hierarchy."""
        if self._root is None:
            raise ValueError("No menu has been started")
        return self._root

    def reset(self) -> "MenuBuilder":
        """Reset the builder to start fresh."""
        self._root = None
        self._current = None
        self._stack.clear()
        return self
