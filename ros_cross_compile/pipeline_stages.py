# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Wrapper abstractions for each pipeline stage.

The abstractions allows for streamlining the pipeline into a unified
'pipeline runner' and collecting of time series data from each stage.
"""

from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import List, Optional

from ros_cross_compile.builders import run_emulated_docker_build
from ros_cross_compile.data_collector import DataCollector
from ros_cross_compile.dependencies import assert_install_rosdep_script_exists
from ros_cross_compile.dependencies import gather_rosdeps
from ros_cross_compile.docker_client import DockerClient
from ros_cross_compile.platform import Platform
from ros_cross_compile.sysroot_creator import create_workspace_sysroot_image


class PipelineStage(metaclass=ABCMeta):
    """Represents a stage of the pipeline."""

    @abstractmethod
    def __init__(self, data_collector: DataCollector):
        self.data_collector = data_collector

    @abstractmethod
    def __call__(self, platform: Platform, docker_client: DockerClient, ros_workspace_dir: Path,
                 skip_rosdep_keys: List, custom_rosdep_script: Optional[Path] = None,
                 custom_data_dir: Optional[Path] = None):
        pass


class DependenciesStage(PipelineStage):
    """Represents stage that gets ros dependencies and sets up the rosdep installation script."""

    def __init__(self, data_collector):
        super().__init__(data_collector)

    def __call__(self, platform: Platform, docker_client: DockerClient, ros_workspace_dir: Path,
                 skip_rosdep_keys: List, custom_rosdep_script: Optional[Path] = None,
                 custom_data_dir: Optional[Path] = None):
        gather_rosdeps(
            docker_client=docker_client,
            platform=platform,
            workspace=ros_workspace_dir,
            skip_rosdep_keys=skip_rosdep_keys,
            custom_script=custom_rosdep_script,
            custom_data_dir=custom_data_dir)
        assert_install_rosdep_script_exists(ros_workspace_dir, platform)


class CreateSysrootStage(PipelineStage):
    """Represents stage that creates the 'sysroot' docker image."""

    def __init__(self, data_collector):
        super().__init__(data_collector)

    def __call__(self, platform: Platform, docker_client: DockerClient, ros_workspace_dir: Path,
                 skip_rosdep_keys: List, custom_rosdep_script: Optional[Path] = None,
                 custom_data_dir: Optional[Path] = None):
        with self.data_collector.data_timer(create_workspace_sysroot_image.__name__):
            create_workspace_sysroot_image(docker_client, platform)


class RunDockerBuildStage(PipelineStage):
    """Represents stage that actually performs the cross compilation in a Docker image."""

    def __init__(self, data_collector):
        super().__init__(data_collector)

    def __call__(self, platform: Platform, docker_client: DockerClient, ros_workspace_dir: Path,
                 skip_rosdep_keys: List, custom_rosdep_script: Optional[Path] = None,
                 custom_data_dir: Optional[Path] = None):
        with self.data_collector.data_timer(run_emulated_docker_build.__name__):
            run_emulated_docker_build(docker_client, platform, ros_workspace_dir)
