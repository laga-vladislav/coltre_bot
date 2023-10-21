import dataclasses


@dataclasses.dataclass
class Exercise:
    id: int
    name: str
    norm: int
    unit: str
