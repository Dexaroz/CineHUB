from typing import TypeVar, Dict, Type, Any, Callable

C = TypeVar("C")
Q = TypeVar("Q")
R = TypeVar("R")

class CommandBus:
    def __init__(self) -> None:
        self._handlers: Dict[Type[Any], Callable[[Any], Any]] = {}

    def register(self, command_type: Type[C], handler: Callable[[C], Any]) -> None:
        self._handlers[command_type] = handler

    def handle(self, command: C) -> Any:
        handler = self._handlers.get(type(command))
        if not handler:
            raise RuntimeError(f"No handler for command {type(command).__name__}")
        return handler(command)

class QueryBus:
    def __init__(self) -> None:
        self._handlers: Dict[Type[Any], Callable[[Any], Any]] = {}

    def register(self, query_type: Type[Q], handler: Callable[[Q], R]) -> None:
        self._handlers[query_type] = handler

    def ask(self, query: Q) -> R:
        handler = self._handlers.get(type(query))
        if not handler:
            raise RuntimeError(f"No handler for query {type(query).__name__}")
        return handler(query)
