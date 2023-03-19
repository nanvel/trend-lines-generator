import pytest
from pathlib import Path

from pandas import read_csv


class Data:
    def __init__(self, root_path):
        self.root_path = root_path

    def load_df(self, path: str):
        df = read_csv(self.root_path / path)
        if "ts" in df.columns:
            df = df.astype({"ts": "datetime64[s]"}).set_index("ts")

        return df


@pytest.fixture(scope="session")
def data():
    return Data(root_path=Path(__file__).parent.resolve() / "data")
