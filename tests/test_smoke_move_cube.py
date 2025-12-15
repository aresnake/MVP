import os
from pathlib import Path

import pytest

from mvp.mcp_stdio import _resolve_blender_executable, run_blender_move_cube


def blender_available() -> bool:
    env = os.environ.get("BLENDER_EXE")
    if env and Path(env).is_file():
        return True
    return _resolve_blender_executable(None) is not None


@pytest.mark.skipif(not blender_available(), reason="Blender executable not found")
def test_move_cube_smoke():
    result = run_blender_move_cube(name="MVP_Test_Cube", delta=[0.0, 0.0, 0.1])
    assert isinstance(result, dict)
    assert result.get("ok") is True, result
    payload = result["result"]
    assert "position" in payload and len(payload["position"]) == 3
    assert "blender_version" in payload
