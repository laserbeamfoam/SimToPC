from dataclasses import dataclass

@dataclass(frozen=True)
class MeasureConfig:
    y_begin: float
    y_end: float
    x_min: float
    x_max: float
    cell_size: float
    min_points_per_zrow: int = 4
