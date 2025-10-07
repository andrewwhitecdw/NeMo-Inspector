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

from dash import html
from dash.dependencies import Input, Output
from flask import current_app

from nemo_inspector.callbacks import app
from nemo_inspector.layouts import get_compare_test_layout
from nemo_inspector.settings.constants import (
    CODE_BEGIN,
    CODE_END,
    CODE_OUTPUT_BEGIN,
    CODE_OUTPUT_END,
)
from nemo_inspector.settings.constants.configurations import CODE_SEPARATORS


@app.callback(
    Output("page_content", "children"),
    Input("url", "pathname"),
)
def nav_click(url: str) -> html.Div:
    config = current_app.config["nemo_inspector"]
    config["code_separators"] = (
        config["code_tags"][CODE_BEGIN],
        config["code_tags"][CODE_END],
    )
    config["code_output_separators"] = (
        config["code_tags"][CODE_OUTPUT_BEGIN],
        config["code_tags"][CODE_OUTPUT_END],
    )

    return get_compare_test_layout()
