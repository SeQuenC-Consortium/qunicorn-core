from dataclasses import dataclass
from typing import Optional

@dataclass
class JobDto:
    circuit: str
    provider: str
    token: str
    qpu: str
    credentials: dict
    shots: int
    circuit_format: str
    noise_model: str
    only_measurement_errors: bool
    parameters: float
    id: Optional[int] = 0
