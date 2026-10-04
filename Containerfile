FROM ubuntu:22.04

# Prevent tzdata prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python, pip, and curl
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl git && \
    rm -rf /var/lib/apt/lists/*

# Install pytest globally for the Tester agent
RUN pip3 install pytest

# Install the Antigravity CLI and move it to a global path
RUN curl -fsSL https://antigravity.google/cli/install.sh | bash && \
    mv ~/.local/bin/agy /usr/local/bin/agy

# Default command
CMD ["agy"]

