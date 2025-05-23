FROM python:3.9-slim

# Define build arguments for proxy settings
ARG HTTP_PROXY
ARG HTTPS_PROXY

# Create non-root user
RUN groupadd -r manus && useradd -r -g manus -m -s /bin/bash manus

# Set proxy environment variables if ARGs are provided
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}

# Set working directory for app-related operations early
ENV APP_HOME=/opt/nanomanus_app
WORKDIR ${APP_HOME}

# Install dependencies
# RUN echo "HTTP_PROXY is: $HTTP_PROXY" && echo "HTTPS_PROXY is: $HTTPS_PROXY" # Debug line, can be removed
COPY requirements.txt .
RUN pip install --no-cache-dir \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    -r requirements.txt

# Unset proxy environment variables after pip install if they were set
RUN if [ -n "${HTTP_PROXY}" ]; then unset HTTP_PROXY; fi
RUN if [ -n "${HTTPS_PROXY}" ]; then unset HTTPS_PROXY; fi

# Copy application code (project root from host -> ${APP_HOME} in container)
# This means ${APP_HOME}/nanoOpenManus/ will be the package root.
COPY . ${APP_HOME}

# Correctly overwrite original tools with safe versions INSIDE the nanoOpenManus package structure
COPY docker/safe_tools/file_saver.py ${APP_HOME}/nanoOpenManus/app/tools/file_saver.py
COPY docker/safe_tools/python_execute.py ${APP_HOME}/nanoOpenManus/app/tools/python_execute.py

# Set PYTHONPATH to the directory containing the 'nanoOpenManus' package
ENV PYTHONPATH=${APP_HOME}

# Create fixed working directory outside /app, only this directory can be written to
# Ensure permissions are set after all files are copied to APP_HOME
RUN mkdir -p /workspace_in_container && \
    chown manus:manus /workspace_in_container
ENV ALLOWED_WRITE_DIR=/workspace_in_container

# Switch to non-root user
USER manus

# Set environment variables
# Ensures Python can find modules in /app (e.g., nanoOpenManus package)
ENV PYTHONPATH=${APP_HOME}
ENV MAX_STEPS=15
ENV DEBUG=true

# Run entrypoint script (which is now very simple)
ENTRYPOINT []
CMD ["tail", "-f", "/dev/null"] 