import dataclasses


@dataclasses.dataclass
class TrainingLevel:
    id: int
    training_level_name: str
    description: str
    multiplier: float
