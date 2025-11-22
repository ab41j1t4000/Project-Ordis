from typing import Callable, Dict, Any

ToolFn = Callable[[Dict[str, Any]], Dict[str, Any]]

class ToolRouter:
    """
    Week-1 stub. No smart selection.
    Just a registry so the kernel can call tools later.
    """
    def __init__(self):
        self.tools: Dict[str, ToolFn] = {}

    def register(self, name: str, fn: ToolFn):
        self.tools[name] = fn

    def call(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not registered")
        return self.tools[name](args)