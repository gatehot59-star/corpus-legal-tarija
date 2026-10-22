"""Explicit opt-in for Paddle's existing low-memory loader in isolated OCR workers.

Python imports this module only through the sidecar's configured PYTHONPATH.
No installed dependency or model file is modified.
"""
import os
import sys


def enable_low_memory(model_class):
    """Forward the original loader unchanged except for its allocation strategy."""
    original = model_class.from_pretrained.__func__

    def load(cls, *args, **kwargs):
        kwargs["low_cpu_mem_usage"] = True
        return original(cls, *args, **kwargs)

    model_class.from_pretrained = classmethod(load)


if os.environ.get("CORPUS_OCR_LOW_MEMORY") == "1" and "worker" in sys.argv:
    try:
        from paddlex.inference.models.doc_vlm.modeling import PaddleOCRVLForConditionalGeneration
        enable_low_memory(PaddleOCRVLForConditionalGeneration)
        print("corpus_loader: low_cpu_mem_usage=True", flush=True)
    except Exception:
        # Python normally ignores exceptions from sitecustomize. Fail closed instead.
        import traceback
        traceback.print_exc()
        os._exit(78)
