from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def valid_frame() -> pd.DataFrame:
    return pd.read_csv(Path(__file__).parents[1] / "data" / "flights_sample.csv")


@pytest.fixture
def csv_factory(tmp_path: Path):
    def write(frame: pd.DataFrame, name: str = "input.csv") -> Path:
        path = tmp_path / name
        frame.to_csv(path, index=False)
        return path
    return write