#!/bin/sh

IMAGE_NAME=com3524
CONTAINER_NAME=forest-fire-team13

# 1. Start XQuartz access for Docker
xhost +localhost

# 2. Remove old container
docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1

# 3. Build image
docker build -t "$IMAGE_NAME" .

# 4. Run container with mounts
docker run -it --rm \
    --name "$CONTAINER_NAME" \
    -e DISPLAY=host.docker.internal:0 \
    -e PYTHONPATH=/src \
    -p 5000:5000 \
    -v "$(pwd)/CAPyle_releaseV2":/src/CAPyle_releaseV2 \
    -v "$(pwd)/run_tool.py":/src/run_tool.py \
    "$IMAGE_NAME" \
    python3 -m run_tool
