# Sandbox image for the agent's code execution. Libraries are pinned HERE (not in
# the repo's requirements.txt) because this is the container's own environment.
FROM python:3.13-slim

RUN pip install --no-cache-dir \
    numpy==2.2.2 \
    pandas==2.2.3 \
    pyarrow==24.0.0 \
    matplotlib==3.11.2 \
    seaborn==0.13.2 \
    scipy==1.18.1 \
    statsmodels==0.15.0 \
    ipython==9.17.1 \
    cartopy==0.25.0 \
    shapely==2.1.2 \
    pyproj==3.7.2 \
    pyshp==3.0.2.post1

# Natural Earth shapes for cartopy maps, downloaded NOW because the sandbox has no network at run time:
# coastline, land, ocean, lakes, country borders, country polygons, state/province polygons, each at 110m, 50m and 10m.
# cartopy looks in CARTOPY_DATA_DIR before it tries to download. (Same as ai_for_vayu/sandbox.)
ENV CARTOPY_DATA_DIR=/opt/cartopy
COPY download_natural_earth.py /download_natural_earth.py
RUN python /download_natural_earth.py

# root fs is mounted read-only at run time -> everything writable lives in /tmp (tmpfs) or /workspace
ENV HOME=/tmp MPLCONFIGDIR=/tmp/mpl MPLBACKEND=Agg PYTHONUNBUFFERED=1

COPY exec_server.py /exec_server.py
WORKDIR /workspace
CMD ["python", "/exec_server.py"]

# docker build -t aeronet-sandbox .
