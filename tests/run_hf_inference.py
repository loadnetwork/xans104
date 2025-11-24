"""Smoke test: download a llm_model.ans104 by ID and run a short HF generation."""

from __future__ import annotations

from xans104 import load_model

DEFAULT_PROMPT = "slop"
DEFAULT_MODEL = "gESMyqhLntTn6zvldcUcSf0JfFpGDrQX6JKDKhKVf7k" # tiny-gpt2
DEFAULT_MAX_NEW_TOKENS = 20


def main():
    tokenizer, model, model_dir = load_model(DEFAULT_MODEL)

    inputs = tokenizer(DEFAULT_PROMPT, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=DEFAULT_MAX_NEW_TOKENS)
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))
    print(f"model files available at: {model_dir}")


if __name__ == "__main__":
    main()
