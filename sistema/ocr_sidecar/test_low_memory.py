"""The allocation override must retain class binding, dtype and all other arguments."""
import unittest
from sitecustomize import enable_low_memory


class LoaderTests(unittest.TestCase):
    def test_only_allocation_strategy_changes(self):
        class Model:
            @classmethod
            def from_pretrained(cls, *args, **kwargs):
                return cls, args, kwargs
        enable_low_memory(Model)
        cls, args, kwargs = Model.from_pretrained("/model", dtype="float32", convert_from_hf=True)
        self.assertIs(cls, Model)
        self.assertEqual(args, ("/model",))
        self.assertEqual(kwargs, {"dtype": "float32", "convert_from_hf": True,
                                  "low_cpu_mem_usage": True})


if __name__ == "__main__":
    unittest.main()
