from typing import Callable, Dict, Type, Any


class MessageBus:

    def __init__(self):
        self._command_handlers: Dict[Type, Callable] = {}
        self._query_handlers: Dict[Type, Callable] = {}

    def register_command_handler(self, command_type: Type, handler: Callable):
        self._command_handlers[command_type] = handler

    def register_query_handler(self, query_type: Type, handler: Callable):
        self._query_handlers[query_type] = handler

    def handle_command(self, command: Any, uow: Any) -> Any:
        handler = self._command_handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler registered for command {type(command).__name__}")
        return handler(command, uow)

    def handle_query(self, query: Any, uow: Any) -> Any:
        handler = self._query_handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler registered for query {type(query).__name__}")
        return handler(query, uow)