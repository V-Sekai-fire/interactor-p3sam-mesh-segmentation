# interactor-p3sam-mesh-segmentation

Model image for `p3sam_mesh_segmentation`, per
[weftspun's RFD 0036](https://github.com/weftspun/request-for-discussion/tree/main/0036-packaging-convention)
packaging convention. Interface facts from
[RFD 0041](https://github.com/weftspun/request-for-discussion/tree/main/0041-p3sam-mesh-segmentation).

## License — corrected, not carried from the RFD

**RFD 0041's `cog.yaml` records `license: "MIT"`. That's wrong**, checked against the real
upstream: P3-SAM ships as part of [`Tencent-Hunyuan/Hunyuan3D-Part`](
https://github.com/Tencent-Hunyuan/Hunyuan3D-Part), under the **Tencent Hunyuan 3D-Part
Community License Agreement** — a custom, territory-limited license ("does not apply in the
European Union, United Kingdom and South Korea"), not MIT. No separately-licensed standalone
P3-SAM repo exists (checked GitHub search directly).

Marked **license: review pending** here, not MIT — per [RFD 0028](
https://github.com/weftspun/request-for-discussion/tree/main/0028-model-license-gate), the
license gate is a hard prerequisite before shipping to paying users, and this model has not
cleared it. Whoever owns RFD 0041 should correct that record.

## Model

| Property | Value |
|---|---|
| Upstream | [Tencent-Hunyuan/Hunyuan3D-Part](https://github.com/Tencent-Hunyuan/Hunyuan3D-Part), `P3-SAM/` |
| License | **review pending** — Tencent Hunyuan 3D-Part Community License (territory-restricted), not MIT as RFD 0041 states |
| Parameters | 0.4 B, estimated (RFD 0041) |
| bf16 | 0.8 GB |
| Q4_K_M | 0.22 GB (not shipped — bf16 is the format) |

P3-SAM replaces PartField, which RFD 0028 removed for a non-commercial weight license — worth
noting since P3-SAM's own license needs the same scrutiny that removed PartField.

## Interface

`POST /predict`:

| Input | Type | Default | Note |
|---|---|---|---|
| `mesh` | Path/URL/base64 (GLB) | required | |
| `segment_every_part` | bool | false | Returns every part found, ignores `max_parts` |
| `max_parts` | int | 32 | |
| `seed` | int | -1 | |

Returns `{labels, parts, seed, stub}` — **not** `{glb, layer}` like the mesh-generation models.
Per RFD 0041: `labels` is one integer per face (written as a file, not an inline list — a
210000-vertex mesh's face array is large), `parts` is a list of split-mesh GLBs. The label
array is the stable output — a later decimation renumbers faces, so a split mesh isn't stable
input for the rig/remix stages the way the label array is.

## Build

```sh
docker build --target contract -t interactor-p3sam-mesh-segmentation:contract .
docker run --rm -p 8000:8000 interactor-p3sam-mesh-segmentation:contract
curl -X POST localhost:8000/predict -d @test_input.json -H 'Content-Type: application/json'
```

## Status

**Scaffolded from the RFD, not yet built or run.** `_run_upstream()`'s exact call into P3-SAM's
Python API is not yet verified against the real repo the way TRELLIS.2's was — `model.py` exists
in `Tencent-Hunyuan/Hunyuan3D-Part/P3-SAM/` but its exact inference entry point wasn't confirmed
in this pass. Confirm before trusting the worker stage. **License is the harder blocker**:
resolve that before this image ships to anyone, regardless of what code verification finds.
