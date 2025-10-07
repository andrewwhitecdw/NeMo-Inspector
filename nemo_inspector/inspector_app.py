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

import sys
from pathlib import Path
import argparse
import dataclasses
import signal

from nemo_inspector.parse_agruments_helpers import (
    add_arguments_from_dataclass,
    args_postproccessing,
    create_dataclass_from_args,
)

sys.path.append(str(Path(__file__).parents[1]))

from nemo_inspector.layouts import get_main_page_layout

from nemo_inspector.settings.inspector_config import InspectorConfig
from nemo_inspector.settings.constants.configurations import CODE_SEPARATORS


def main():
    signal.signal(signal.SIGALRM, signal.SIG_IGN)

    parser = argparse.ArgumentParser(description="NeMo Inspector")

    add_arguments_from_dataclass(
        parser,
        InspectorConfig,
        enforce_required=False,
        use_type_defaults=True,
    )

    args = parser.parse_args()
    args_dict = vars(args)

    cfg = dataclasses.asdict(create_dataclass_from_args(InspectorConfig, args_dict))
    cfg.setdefault("code_tags", {})
    cfg["code_tags"] = {**CODE_SEPARATORS, **cfg["code_tags"]}
    cfg = args_postproccessing(cfg)
    from nemo_inspector.callbacks import app

    app.server.config.update({"nemo_inspector": cfg})
    app.title = "NeMo Inspector"
    app.layout = get_main_page_layout()
    app.run(
        host="localhost",
        port="8080",
    )


if __name__ == "__main__":
    main()
