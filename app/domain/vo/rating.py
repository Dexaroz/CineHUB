from dataclasses import dataclass

@dataclass(frozen=True)
class Rating:
    value: int

    def __post_init__(self):
        if not (0 <= self.value <= 10):
            raise ValueError("Rating must be between 0 and 10")