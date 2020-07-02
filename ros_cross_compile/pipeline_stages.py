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
from typing import List, NamedTuple, Optional

from ros_cross_compile.docker_client import DockerClient
from ros_cross_compile.platform import Platform


ConfigOptions = NamedTuple('ConfigOptions', [('skip_rosdep_collection', Optional[bool]),
                                             ('skip_rosdep_keys', List[str]),
                                             ('custom_script', Optional[Path]),
                                             ('custom_data_dir', Optional[Path]),
                                             ('custom_setup_script', Optional[Path])])


class PipelineStage(metaclass=ABCMeta):
    """Represents a stage of the pipeline."""

    @abstractmethod
    def __init__(self):
        self.name = ''

    @abstractmethod
    def __call__(self, platform: Platform, docker_client: DockerClient, ros_workspace_dir: Path,
                 customizations: ConfigOptions):
        pass