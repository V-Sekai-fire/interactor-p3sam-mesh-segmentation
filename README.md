# interactor-p3sam-mesh-segmentation

A model image that segments a mesh into parts and returns a label per face plus the split part meshes.

## Use

The image serves one prediction endpoint over HTTP. [RFD 1041](https://github.com/V-Sekai-fire/manuals-weftspun/tree/main/rfd/1041-p3sam-mesh-segmentation) owns its interface and [RFD 1036](https://github.com/V-Sekai-fire/manuals-weftspun/tree/main/rfd/1036-packaging-convention) its packaging. The upstream weights carry a territory-restricted community licence, not MIT, so the model has not cleared the [RFD 1028](https://github.com/V-Sekai-fire/manuals-weftspun/tree/main/rfd/1028-model-license-gate) licence gate. The server's call into the upstream model is a guard that raises until it is wired in.

## Build and run

The `contract` stage builds a stub server that answers with the interface's shape and needs no GPU:

```sh
docker build --target contract -t interactor-p3sam-mesh-segmentation:contract .
docker run --rm -p 8000:8000 interactor-p3sam-mesh-segmentation:contract
```

The server listens on the port `PORT` names.

## Licence

This repository states no licence.
