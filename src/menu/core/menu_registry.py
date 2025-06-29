from typing import Dict, Type, Callable, List

from .menu_builder import MenuBuilder
from .menu_command import MenuCommand
from .menu_component import MenuComponent

"""
Menu registry for managing menu definitions and dynamic registration.
"""


class MenuRegistry:
    """Registry for managing menu definitions."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._menus: Dict[str, Type[MenuComponent]] = {}
            self._commands: Dict[str, Type[MenuCommand]] = {}
            self._builders: Dict[str, Callable[[], MenuComponent]] = {}
            self._initialized = True

    def register_menu(self, name: str, menu_class: Type[MenuComponent]) -> None:
        """Register a menu class."""
        self._menus[name] = menu_class

    def register_command(self, name: str, command_class: Type[MenuCommand]) -> None:
        """Register a command class."""
        self._commands[name] = command_class

    def register_builder(
        self, name: str, builder_func: Callable[[], MenuComponent]
    ) -> None:
        """Register a menu builder function."""
        self._builders[name] = builder_func

    def get_menu(self, name: str) -> Type[MenuComponent]:
        """Get a menu class by name."""
        if name not in self._menus:
            raise ValueError("Menu '{name}' not found in registry")
        return self._menus[name]

    def get_command(self, name: str) -> Type[MenuCommand]:
        """Get a command class by name."""
        if name not in self._commands:
            raise ValueError("Command '{name}' not found in registry")
        return self._commands[name]

    def build_menu(self, name: str) -> MenuComponent:
        """Build a menu using its registered builder."""
        if name not in self._builders:
            raise ValueError("Menu builder '{name}' not found in registry")
        return self._builders[name]()

    def list_menus(self) -> List[str]:
        """List all registered menu names."""
        return list(self._menus.keys())

    def list_commands(self) -> List[str]:
        """List all registered command names."""
        return list(self._commands.keys())

    def list_builders(self) -> List[str]:
        """List all registered builder names."""
        return list(self._builders.keys())
