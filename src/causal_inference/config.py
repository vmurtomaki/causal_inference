import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Execute environment variable injection
load_dotenv()


@dataclass(frozen=True)
class Config:
    """
    Centralized configuration mapping for the causal inference pipeline.
    Validates and types parameters injected from the environment.
    """

    data_path: str = os.getenv("DATA_PATH", "data/raw/oj_data.csv")
    n_folds: int = int(os.getenv("N_FOLDS", "5"))
    random_seed: int = int(os.getenv("RANDOM_SEED", "42"))


config = Config()
