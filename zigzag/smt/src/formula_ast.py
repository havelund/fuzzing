from abc import ABC
from dataclasses import dataclass, is_dataclass, fields


@dataclass
class Formula(ABC):
    def pretty_print(self, indent: int = 0) -> None:
        """Generic method to pretty print the dataclass instance with tree-like indentation."""
        TAB = 2
        indent_str = "|  " * indent
        cls_name = self.__class__.__name__
        if is_dataclass(self) and fields(self):
            print(f"{indent_str}{cls_name}:")
        else:
            print(f"{indent_str}{cls_name}")
        if is_dataclass(self):
            for field in fields(self):
                value = getattr(self, field.name)
                if isinstance(value, Formula):
                    value.pretty_print(indent + TAB)
                else:
                    print(f"{indent_str}|  {field.name}: {value}")

