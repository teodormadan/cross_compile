# This file creates the root filesystem for the workspace to build against
# It installs all build, run, and test dependencies for the workspace
# It uses QEmu user-mode emulation to perform this dependency installation
# Assumptions: bin/ directory in the docker build context contains the necessary qemu binary

ARG BASE_IMAGE
FROM ${BASE_IMAGE}

SHELL ["/bin/bash", "-c"]
COPY bin/* /usr/bin/

# Set timezone
RUN echo 'Etc/UTC' > /etc/timezone && \
    ln -sf /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN apt-get update && apt-get install --no-install-recommends -y \
        tzdata \
        locales \
    && rm -rf /var/lib/apt/lists/*

# Set locale
RUN echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen && \
    locale-gen && \
    update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL C.UTF-8

# Extra package managers for installing dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
      python3-pip \
      python3-setuptools \
      dirmngr \
      gnupg2 \
      lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Add the ros apt repo
RUN apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' \
    --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654

ARG ROS_VERSION
RUN echo "deb http://packages.ros.org/${ROS_VERSION}/ubuntu `lsb_release -cs` main" \
    > /etc/apt/sources.list.d/${ROS_VERSION}-latest.list

# Install some pip packages needed for testing ROS 2
RUN if [[ "${ROS_VERSION}" == "ros2" ]]; then \
    python3 -m pip install -U \
    flake8 \
    flake8-blind-except \
    flake8-builtins \
    flake8-class-newline \
    flake8-comprehensions \
    flake8-deprecated \
    flake8-docstrings \
    flake8-import-order \
    flake8-quotes \
    pytest-repeat \
    pytest-rerunfailures \
    pytest \
    pytest-cov \
    pytest-runner \
  ; fi

# Install Fast-RTPS dependencies for ROS 2
RUN if [[ "${ROS_VERSION}" == "ros2" ]]; then \
    apt-get update && apt-get install --no-install-recommends -y \
        libasio-dev \
        libtinyxml2-dev \
    && rm -rf /var/lib/apt/lists/* \
  ; fi

# Run arbitrary user setup (copy data and run script)
COPY user-custom-data/ custom-data/
COPY user-custom-setup .
RUN chmod +x ./user-custom-setup && \
    ./user-custom-setup && \
    rm -rf /var/lib/apt/lists/*

# Use generated rosdep installation script
COPY install_rosdeps.sh .
RUN chmod +x install_rosdeps.sh
RUN apt-get update && \
    ./install_rosdeps.sh && \
    rm -rf /var/lib/apt/lists/*
