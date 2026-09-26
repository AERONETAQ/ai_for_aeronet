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
    ipython==9.17.1

# root fs is mounted read-only at run time -> everything writable lives in /tmp (tmpfs) or /workspace
ENV HOME=/tmp MPLCONFIGDIR=/tmp/mpl MPLBACKEND=Agg PYTHONUNBUFFERED=1

COPY exec_server.py /exec_server.py
WORKDIR /workspace
CMD ["python", "/exec_server.py"]
