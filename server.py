"""P3-SAM mesh segmentation. RFD 0041.

An HTTP server in a plain Docker image (RFD 0036). Segments a mesh into parts;
returns the stable label array plus split-mesh GLBs.

License: review pending, not MIT (RFD 0041's record is wrong -- see README).
Upstream: Tencent-Hunyuan/Hunyuan3D-Part, P3-SAM/. `_run_upstream()`'s exact
call is NOT yet verified against that repo (unlike TRELLIS.2's, which is) --
this is a best-effort shape from the DETAILS.md interface table, flagged
honestly rather than presented as checked.
"""

import base64
import json
import os
import tempfile
import urllib.request
from pathlib import Path

SRC = os.environ.get("P3SAM_SRC", "/src/Hunyuan3D-Part/P3-SAM")
WEIGHTS = os.environ.get("P3SAM_WEIGHTS", "/weights/p3sam")

STUB = os.environ.get("WEFTSPUN_STUB") == "1"

_READY = {"loaded": False}


class InputError(ValueError):
    """The request is wrong. This is the caller's fault, and not ours."""


def _fetch(value: str, work: Path, name: str) -> Path:
    target = work / name
    if value.startswith(("http://", "https://")):
        urllib.request.urlretrieve(value, target)
        return target
    if value.startswith("data:"):
        value = value.split(",", 1)[1]
    target.write_bytes(base64.b64decode(value))
    return target


def _validate(job_input: dict) -> dict:
    if not job_input.get("mesh"):
        raise InputError("mesh is required: a URL, a data URI, or base64 GLB bytes")

    max_parts = int(job_input.get("max_parts", 32))
    if not 1 <= max_parts <= 256:
        raise InputError("max_parts must be between 1 and 256")

    return {
        "mesh": job_input["mesh"],
        "segment_every_part": bool(job_input.get("segment_every_part", False)),
        "max_parts": max_parts,
        "seed": int(job_input.get("seed", -1)),
    }


def _run_upstream(mesh_path: Path, work: Path, args: dict) -> tuple[Path, list[Path]]:
    """NOT YET VERIFIED against the real P3-SAM API -- see README's Status
    section. `model.py` in Tencent-Hunyuan/Hunyuan3D-Part/P3-SAM/ is the
    likely entry point; this needs confirming against it, not this comment,
    before the worker stage is trusted."""
    raise NotImplementedError(
        "P3-SAM's real Python entry point is not yet confirmed -- "
        "see Tencent-Hunyuan/Hunyuan3D-Part/P3-SAM/model.py and wire this in "
        "for real before removing this guard."
    )


def _encode(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def predict(job_input: dict) -> dict:
    args = _validate(job_input)
    work = Path(tempfile.mkdtemp())
    mesh_path = _fetch(args["mesh"], work, "input.glb")

    if STUB:
        labels_path = work / "labels.json"
        labels_path.write_text(json.dumps({"labels": [0, 0, 1, 1, 2]}))
        parts = []
        for i in range(min(3, args["max_parts"])):
            p = work / f"part_{i}.glb"
            p.write_bytes(bytes([0x67, 0x6C, 0x54, 0x46, 0x02]) + b"stub")
            parts.append(p)
    else:
        labels_path, parts = _run_upstream(mesh_path, work, args)

    return {
        "labels": _encode(labels_path),
        "parts": [_encode(p) for p in parts],
        "seed": args["seed"],
        "stub": STUB,
    }


def load() -> None:
    if STUB:
        _READY["loaded"] = True
        return
    if not Path(SRC).is_dir():
        raise RuntimeError("the upstream source is absent: " + SRC)
    if not Path(WEIGHTS).is_dir():
        raise RuntimeError("the weights are absent: " + WEIGHTS)
    _READY["loaded"] = True


def build_app():
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel

    app = FastAPI(title="p3sam_mesh_segmentation", version="0.1.0")

    class PredictRequest(BaseModel):
        mesh: str
        segment_every_part: bool = False
        max_parts: int = 32
        seed: int = -1

    @app.get("/health")
    def health():
        return {"status": "ok", "ready": _READY["loaded"], "stub": STUB}

    @app.post("/predict")
    def run(request: PredictRequest):
        try:
            return predict(request.model_dump())
        except InputError as error:
            return JSONResponse(status_code=400, content={"error": str(error)})

    return app


if __name__ == "__main__":
    import uvicorn

    load()
    uvicorn.run(build_app(), host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
