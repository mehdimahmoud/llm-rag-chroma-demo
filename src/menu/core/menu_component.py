from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Any

from .enums import MenuAction, MenuChoice
from .menu_command import CommandContext, MenuCommand

"""
Base menu component interface using Component pattern.
"""


@dataclass
class MenuItem:
    """Represents a single menu item."""

    id: str
    title: str
    description: str = ""
    enabled: bool = True
    visible: bool = True


class MenuComponent(ABC):
    """Abstract base class for all menu components."""

    def __init__(self, title: str, description: str = ""):
        self.title = title
        self.description = description
        self._children: List["MenuComponent"] = []

    def add_child(self, child: "MenuComponent") -> None:
        """Add a child component."""
        self._children.append(child)

    def remove_child(self, child: "MenuComponent") -> None:
        """Remove a child component."""
        if child in self._children:
            self._children.remove(child)

    def get_children(self) -> List["MenuComponent"]:
        """Get all child components."""
        return self._children.copy()

    @abstractmethod
    def display(self) -> None:
        """Display the menu component."""
        pass

    @abstractmethod
    def handle_input(self, choice: str, context=None) -> Any:
        """Handle user input."""
        pass
