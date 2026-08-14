# interactor-p3sam-mesh-segmentation -- vast.ai worker, RFD 0036/0041.
#
# License: review pending -- Tencent's own Community License, territory
# restricted. NOT MIT despite RFD 0041's cog.yaml claiming it is. Resolve
# this before shipping to anyone; see README.
#
# Weights: 0.8 GB bf16. Real source below, RFD 0041's weights.invalid was a
# placeholder (RFC 2606), never a real pin.

FROM python:3.11-slim AS contract
WORKDIR /app
RUN pip install --no-cache-dir usd-core==25.5 fastapi==0.115.5 uvicorn==0.32.1 pydantic==2.10.3
COPY server.py /app/server.py
COPY test_input.json /app/test_input.json
ENV WEFTSPUN_STUB=1 PORT=8000
EXPOSE 8000
CMD ["python", "/app/server.py"]

FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04 AS worker

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    P3SAM_SRC=/src/Hunyuan3D-Part/P3-SAM \
    P3SAM_WEIGHTS=/weights/p3sam

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3.11 python3-pip git libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
      torch==2.5.1 numpy==2.1.3 safetensors==0.4.5 trimesh==4.10.1 \
      huggingface_hub==0.26.2 fastapi==0.115.5 uvicorn==0.32.1 pydantic==2.10.3

# NOT YET WIRED UP FOR REAL -- see server.py's _run_upstream NotImplementedError
# and README's Status section. This clone and weight download are here so the
# worker stage's shape is right; the actual predict() call still needs
# confirming against P3-SAM/model.py before this image does real work.
ARG P3SAM_REF=main
RUN git clone https://github.com/Tencent-Hunyuan/Hunyuan3D-Part.git /src/Hunyuan3D-Part \
    && git -C /src/Hunyuan3D-Part checkout "${P3SAM_REF}"

RUN python3 -c "\
from huggingface_hub import snapshot_download; \
snapshot_download('tencent/Hunyuan3D-Part', local_dir='/weights/p3sam', allow_patterns=['P3-SAM/*'])" \
    || echo "weight download not yet confirmed against a real HF repo id -- see README"

WORKDIR /app
COPY server.py /app/server.py

ENV PORT=8000
EXPOSE 8000

CMD ["python3", "-u", "/app/server.py"]
