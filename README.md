# BIOMERO Container Template: Nuclei Segmentation Workflow

A BIAFLOWS-compatible Docker container for automated nuclei segmentation in DAPI fluorescence images using Otsu thresholding, morphological operations, and watershed separation.

## Parameters

| Parameter | Description | Default | Type |
|-----------|-------------|---------|------|
| `sigma` | Gaussian blur standard deviation (higher = more smoothing) | 2.0 | float |
| `max_size` | Maximum debris size to remove in pixels (objects ≤ this are removed) | 200 | int |
| `closing_radius` | Morphological closing disk radius (bridges gaps between fragments) | 3 | int |

---


## Building the Container

Create the Docker image with all depencies installed, via the following command:

```bash
docker build -t w_nuclei_segmentation:latest .
```


## Local Testing (Interactive Mode)

### 1. Start Interactive Docker Session

Start the interactive session via the following command and make sure to replace the data paths after `-v` with your local image dataset and result folder paths.

```bash
docker run -it --rm \
  -v C:/Users/YourName/YourProject/images:/data/in \
  -v C:/Users/YourName/YourProject/results:/data/out \
  --entrypoint /bin/bash \
  w_nuclei_segmentation:latest
```

### 2. Run the Wrapper Inside Container

Inside the interactive Docker session, you can run the script via the wrapper:

```bash
python /app/wrapper.py \
  --local \
  --infolder /data/in \
  --outfolder /data/out \
  --no_metrics_computation \
  --sigma 2.0 \
  --max_size 200 \
  --closing_radius 3
```

### 3. Exit Container

```bash
exit
```

Results will be stored in your local directory indicated in the interactive session start command, e.g. in the example above `C:/Users/YourName/YourProject/results` .


## Publishing to Docker Hub

### 1. Tag Your Image

```bash
docker tag w_nuclei_segmentation:latest <dockerhub_username>/w_nuclei_segmentation:v1.0.0
```

### 2. Login to Docker Hub

```bash
docker login
```

### 3. Push to Docker Hub

```bash
docker push <dockerhub_username>/w_nuclei_segmentation:v1.0.0
```
