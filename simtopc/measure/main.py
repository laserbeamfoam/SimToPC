from __future__ import annotations
from pathlib import Path
from simtopc.config import load_config
from simtopc.measure_config import MeasureConfig
from simtopc.measure.impl import run_measure_cases


def run(config_path: str | Path) -> None:
    config_path = Path(config_path).resolve()
    cfg_all = load_config(str(config_path))

    m = cfg_all.measure
    measure_cfg = MeasureConfig(
        y_begin=float(m["y_begin"]),
        y_end=float(m["y_end"]),
        x_min=float(m["x_min"]),
        x_max=float(m["x_max"]),
        cell_size=float(m["cell_size"]),
        min_points_per_zrow=int(m.get("min_points_per_zrow", 4)),
    )

    run_measure_cases(cfg_all=cfg_all, measure_cfg=measure_cfg, config_path=config_path)
