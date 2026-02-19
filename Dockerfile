FROM python:3.7-slim

# ------------------------------------------------------------------------------
# Install system dependencies (required since not included in slim image)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    libgeos-dev \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------------------------
# Install Cytomine python client
RUN git clone https://github.com/cytomine-uliege/Cytomine-python-client.git && \
    cd /Cytomine-python-client && \
    git checkout tags/v2.7.3 && \
    pip install --no-cache-dir . && \
    rm -r /Cytomine-python-client
#RUN pip install --no-cache-dir cytomine-python-client==2.4.1

# Install scientific Python packages first (numpy is needed by biaflows-utilities)
RUN pip install --no-cache-dir \
    numpy \
    scipy

# ------------------------------------------------------------------------------
# Install BIAFLOWS utilities (annotation exporter, compute metrics, helpers,...)
RUN git clone https://github.com/Neubias-WG5/biaflows-utilities.git && \
    cd /biaflows-utilities/ && \
    git checkout tags/v0.9.2 && \
    pip install --no-cache-dir .

# Install BIAFLOWS utilities binaries
RUN chmod +x /biaflows-utilities/bin/* && \
    cp /biaflows-utilities/bin/* /usr/bin/ && \
    rm -r /biaflows-utilities

# ------------------------------------------------------------------------------
# Install Python packages for nuclei segmentation workflow
#RUN pip install --no-cache-dir \
#    numpy \
#    scipy \
#    scikit-image \
#    imageio

RUN pip install --no-cache-dir imageio

# ------------------------------------------------------------------------------
# Create app directory and add workflow files
RUN mkdir -p /app
WORKDIR /app

# Add the entrypoint script (wrapper.py) & workflow metadata file (descriptor.json)
ADD simple_analysis_pipeline.py /app/simple_analysis_pipeline.py
ADD wrapper.py /app/wrapper.py
ADD descriptor.json /app/descriptor.json

# ------------------------------------------------------------------------------
# Run wrapper script upon container start
ENTRYPOINT ["python", "/app/wrapper.py"]
