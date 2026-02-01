# We use a lightweight base image.
# Python and Node are actually installed via "features" in devcontainer.json
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Install system dependencies for Python build
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    build-essential \
    curl \
    git \
    wget \
    ca-certificates \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install Python 3.14.1 from source
RUN wget https://www.python.org/ftp/python/3.14.1/Python-3.14.1.tgz \
    && tar -xzf Python-3.14.1.tgz \
    && cd Python-3.14.1 \
    && ./configure --enable-optimizations --with-ensurepip=install \
    && make -j $(nproc) \
    && make altinstall \
    && cd .. \
    && rm -rf Python-3.14.1 Python-3.14.1.tgz \
    && ln -s /usr/local/bin/python3.14 /usr/local/bin/python3 \
    && ln -s /usr/local/bin/python3.14 /usr/local/bin/python \
    && ln -s /usr/local/bin/pip3.14 /usr/local/bin/pip3 \
    && ln -s /usr/local/bin/pip3.14 /usr/local/bin/pip

# INSTALL POETRY
# We install it globally so it's available in the shell immediately
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry
ENV PATH="/opt/poetry/bin:$PATH"

# Set the working directory
WORKDIR /workspace