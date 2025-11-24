from .hf_loader import extract_dataitem_file_to_hf_dir


def extract_dataitem_to_sagemaker_model_dir(
    model_path: str,
    target_dir: str = "/opt/ml/model"
):
    """Unpack an ANS-104 artifact into SageMaker's model directory."""

    return extract_dataitem_file_to_hf_dir(model_path, target_dir)
