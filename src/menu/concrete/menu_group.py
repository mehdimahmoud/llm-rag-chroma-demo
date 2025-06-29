"""
Concrete implementation of menu groups.
"""
from typing import Any, Dict, List

from ..core.enums import MenuAction, MenuChoice, MenuStatus, MenuStyle, MenuType
from ..core.menu_component import MenuComponent, MenuItem


class MenuGroup(MenuComponent):
    """A menu group that can contain other menu components."""

    def __init__(
        self, title: str, description: str = "", style: MenuStyle = MenuStyle.SIMPLE
    ):
        super().__init__(title, description)
        self._menu_items: List[MenuItem] = []
        self._choice_map: Dict[str, MenuComponent] = {}
        self.style = style

    def add_menu_item(self, item: MenuItem, component: MenuComponent) -> None:
        """Add a menu item with its associated component."""
        self._menu_items.append(item)
        self._choice_map[item.id] = component
        self.add_child(component)

    def display(self) -> None:
        """Display the menu group."""
        if self.style == MenuStyle.SIMPLE:
            self._display_simple()
        elif self.style == MenuStyle.DETAILED:
            self._display_detailed()
        elif self.style == MenuStyle.COMPACT:
            self._display_compact()
        else:
            self._display_verbose()

    def _display_simple(self) -> None:
        """Display menu in simple format."""
        print(f"\n{self.title}")
        print("-" * len(self.title))

        for item in self._menu_items:
            if item.visible:
                status = "" if item.enabled else " (disabled)"
                print(f"{item.id}. {item.title}{status}")

    def _display_detailed(self) -> None:
        """Display menu in detailed format."""
        print("\n" + "=" * 50)
        print(self.title)
        print("=" * 50)

        if self.description:
            print(f"\n{self.description}")

        for item in self._menu_items:
            if item.visible:
                status = "" if item.enabled else " (disabled)"
                print(f"{item.id}. {item.title}{status}")
                if item.description:
                    print(f"   {item.description}")

        print("\n" + "=" * 50)

    def _display_compact(self) -> None:
        """Display menu in compact format."""
        print(f"{self.title}: ", end="")
        choices = [
            f"{item.id}.{item.title}"
            for item in self._menu_items
            if item.visible and item.enabled
        ]
        print(" | ".join(choices))

    def _display_verbose(self) -> None:
        """Display menu in verbose format."""
        print("\n" + "=" * 60)
        print(f"📋 {self.title}")
        print("=" * 60)

        if self.description:
            print(f"\n📝 {self.description}")

        print("\n🎯 Available Options:")
        for item in self._menu_items:
            if item.visible:
                status_icon = "✅" if item.enabled else "❌"
                print(f"  {status_icon} {item.id}. {item.title}")
                if item.description:
                    print(f"     💡 {item.description}")

        print("\n" + "=" * 60)

    def handle_input(self, choice: str, context=None) -> Any:
        """Handle user input and delegate to appropriate component."""
        if choice not in self._choice_map:
            raise ValueError(f"Invalid choice: {choice}")

        component = self._choice_map[choice]
        return component.handle_input(choice, context)

    def get_valid_choices(self) -> List[str]:
        """Get list of valid choice IDs."""
        return [item.id for item in self._menu_items if item.visible and item.enabled]

    def get_menu_items(self) -> List[MenuItem]:
        """Get all menu items."""
        return self._menu_items.copy()

    def set_style(self, style: MenuStyle) -> None:
        """Set the display style for this menu group."""
        self.style = style
