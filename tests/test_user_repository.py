import pytest

# Deprecated centralized tests; using neighbor `{file}_test.py` alongside modules.
pytest.skip("Deprecated: replaced by neighbor tests under api/use_cases/user", allow_module_level=True)
