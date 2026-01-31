# We use a lightweight base image.
# Python and Node are actually installed via "features" in devcontainer.json
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    build-essential \
    curl \
    git \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# INSTALL POETRY
# We install it globally so it's available in the shell immediately
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory
WORKDIR /workspace