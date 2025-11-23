import os
from .hf_loader import extract_dataitem_to_hf_dir


def extract_dataitem_to_sagemaker_model_dir(
    model_path: str,
    target_dir: str = "/opt/ml/model"
):
    with open(model_path, "rb") as f:
        blob = f.read()

    extract_dataitem_to_hf_dir(blob, target_dir)
    return target_dir
