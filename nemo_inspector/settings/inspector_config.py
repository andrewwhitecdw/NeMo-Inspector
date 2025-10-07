# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
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

from dataclasses import dataclass, field
from itertools import chain
from pathlib import Path
from typing import Dict, Iterable, List

from nemo_inspector.settings.constants.configurations import CODE_SEPARATORS


def _expand_paths(paths: Iterable[str]) -> List[str]:
    expanded_files: List[str] = []
    for path in paths:
        expanded = Path(path).expanduser()
        if any(char in str(expanded) for char in ["*", "?"]):
            expanded_files.extend(sorted(map(str, expanded.parent.glob(expanded.name))))
        elif expanded.is_dir():
            expanded_files.extend(sorted(map(str, expanded.rglob("*.jsonl"))))
        elif expanded.exists():
            expanded_files.append(str(expanded))
    return expanded_files


def unroll_files(paths: Iterable[str]) -> List[str]:
    return list(dict.fromkeys(chain.from_iterable(_expand_paths([path]) for path in paths)))


@dataclass(kw_only=True)
class InspectorConfig:
    model_prediction: Dict[str, str] = field(default_factory=dict)
    save_generations_path: str = "nemo_inspector/results/saved_generations"
    code_tags: Dict[str, str] = field(default_factory=lambda: CODE_SEPARATORS)

    def __post_init__(self):
        self.model_prediction = {
            model_name: unroll_files(file_path.split(" "))
            for model_name, file_path in self.model_prediction.items()
        }
