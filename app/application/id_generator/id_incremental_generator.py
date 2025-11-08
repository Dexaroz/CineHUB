
class IncrementalIDGenerator:

    def __init__(self):
        self._current_id = 0

    def generate(self) -> int:
        self._current_id += 1
        return self._current_id

    def set_current(self, id_value: int):
        self._current_id = id_value

    def get_current(self) -> int:
        return self._current_id

id_generator = IncrementalIDGenerator()