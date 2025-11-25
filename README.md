## Install

```bash
pip install xans104
```

## Quick Start

```python
from xans104 import load_model

MODEL_DATAITEM = "gESMyqhLntTn6zvldcUcSf0JfFpGDrQX6JKDKhKVf7k"
tokenizer, model, local_dir = load_model(MODEL_DATAITEM)
outputs = model.generate(**tokenizer("slop it", return_tensors="pt"))
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

`load_model` streams the `.ans104` blob from
`https://gateway.s3-node-1.load.network`, extracts it into a temporary
directory and returns `(tokenizer, model, path)` so you can call HF APIs without
handling files yourself.

## Upload a HuggingFace repo to Load S3

```python
from xans104 import create_model_dataitem

dataitem_id = create_model_dataitem(
    "sshleifer/tiny-gpt2",
    token="LOAD_API_TOKEN",
    tags={"key-1": "value-1"},
)
print(dataitem_id)
```

`create_model_dataitem` downloads the HF snapshot, tars it, sends it to
`load-s3-agent`, and returns the `dataitem_id` ready for inference.


## License
This repository is licensed under the [MIT License](./LICENSE)
