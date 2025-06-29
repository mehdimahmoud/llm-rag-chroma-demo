import os
from enum import Enum, auto

"""
Enums for the generic menu system.
"""


class MenuAction(Enum):
    """Actions that can be performed by menu commands."""

    CONTINUE = "continue"
    BACK = "back"
    EXIT = "exit"
    CUSTOM_ACTION = "custom_action"


class MenuChoice(Enum):
    """Standard menu choice identifiers."""

    BACK = "0"
    EXIT = "0"  # Same as back for exit commands
    HELP = "h"
    CANCEL = "c"


class MenuStatus(Enum):
    """Status values for menu items."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    HIDDEN = "hidden"


class MenuType(Enum):
    """Types of menu components."""

    GROUP = "group"
    COMMAND = "command"
    SUBMENU = "submenu"
    SEPARATOR = "separator"


class CommandType(Enum):
    """Types of commands."""

    NAVIGATION = "navigation"
    ACTION = "action"
    DISPLAY = "display"
    CUSTOM = "custom"


class MenuStyle(Enum):
    """Display styles for menus."""

    SIMPLE = "simple"
    DETAILED = "detailed"
    COMPACT = "compact"
    VERBOSE = "verbose"


class InputType(Enum):
    """Types of user input expected."""

    CHOICE = "choice"
    TEXT = "text"
    NUMBER = "number"
    CONFIRMATION = "confirmation"
    MULTI_SELECT = "multi_select"
