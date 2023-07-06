# basics
import argparse
import os
import sys
from pathlib import Path

PROJECT_DIR = Path.cwd()
sys.path.append(str(PROJECT_DIR))

import numpy as np
import pandas as pd

# utils
from reader import read_file_yaml
from sklearn import datasets
from sklearn.preprocessing import StandardScaler

# basics

file_path_parameters = PROJECT_DIR / "conf" / "parameters.yml"
np.random.seed(0)

# args
parser = argparse.ArgumentParser(description="Process config")
parser.add_argument(
    "integers",
    metavar="N_SAMPLE",
    type=int,
    nargs="?",
    default=[500],
    help="an integer for length of the dataset generated.",
)
parser.add_argument(
    "object",
    metavar="PATH",
    type=str,
    nargs="?",
    default=[file_path_parameters],
    help=f"file path to parameters configuration. (default: {file_path_parameters})",
)
parser.add_argument(
    "random_state",
    metavar="RANDOM_STATE",
    type=int,
    nargs="?",
    default=170,
    help="set random_state for data generation (default: 170)",
)
args = parser.parse_args()

# ============
# read parameters
parameters = read_file_yaml(file_path_parameters)

_params_dataset = {
    i_name: {
        "params": i_content,
    }
    for i_name, i_content in parameters["generation_params"].items()
}
# ============

# ============
# Generate datasets. We choose the size big enough to see the scalability
# of the algorithms, but not too big to avoid too long running times
# ============
content = {}
noisy_circles = datasets.make_circles(n_samples=args.integers, **_params_dataset["noisy_circles"]["params"])
noisy_moons = datasets.make_moons(n_samples=args.integers, **_params_dataset["noisy_moons"]["params"])
blobs = datasets.make_blobs(n_samples=args.integers, **_params_dataset["blobs"]["params"])
no_structure = np.random.rand(*_params_dataset["no_structure"]["params"]), None

# Anisotropicly distributed data
X, y, *others = datasets.make_blobs(n_samples=args.integers, random_state=args.random_state)
rotation = _params_dataset["aniso"]["params"]["rotation"]
X_aniso = np.dot(X, rotation)
aniso = (X_aniso, y)

# blobs with varied variances
varied = datasets.make_blobs(
    n_samples=args.integers, random_state=args.random_state, **_params_dataset["varied"]["params"]
)

# organize content
content = {
    "aniso": aniso,
    "noisy_circles": noisy_circles,
    "noisy_moons": noisy_moons,
    "blobs": blobs,
    "varied": varied,
    "no_structure": no_structure,
}

_datasets = {
    i_name: {
        "content": content[i_name],
    }
    for i_name, i_content in parameters["generation_params"].items()
}

dataset_std = []
data = {}
for i_name, args in _datasets.items():
    URL = PROJECT_DIR / "data" / i_name
    X, y = args["content"]
    X = StandardScaler().fit_transform(X)
    if not os.path.exists(URL):
        os.makedirs(URL)
    data[i_name] = pd.DataFrame(X)
    data[i_name]["labels"] = y
    data[i_name].to_csv(URL / Path(i_name + ".csv"), index=False)
