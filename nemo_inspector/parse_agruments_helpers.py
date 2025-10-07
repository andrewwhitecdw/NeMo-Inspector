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

import argparse
import dataclasses
from typing import Any, Optional, Type

from nemo_inspector.utils.common import get_type_default, resolve_union_or_any


class ParseDict(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for value in values:
            key, value = value.split("=")
            getattr(namespace, self.dest)[key] = value


def add_arguments_from_dataclass(
    parser: argparse.ArgumentParser,
    dataclass_type: Type[Any],
    prefix: str = "",
    use_default: Optional[str] = None,
    enforce_required: bool = True,
    use_type_defaults: bool = True,
):
    for field in dataclasses.fields(dataclass_type):
        field_name = f"{prefix}{field.name}"
        field_type = field.type
        # Handle default values and default_factory
        has_default = field.default != dataclasses.MISSING
        has_default_factory = field.default_factory != dataclasses.MISSING

        # Handle nested dataclasses
        if dataclasses.is_dataclass(field_type):
            add_arguments_from_dataclass(
                parser,
                field_type,
                prefix=f"{field_name}.",
                use_default=use_default,
                enforce_required=enforce_required,
                use_type_defaults=use_type_defaults,
            )
            continue

        arg_name = f"--{field_name}"

        # Handle Optional and Union types
        field_type = resolve_union_or_any(field_type)

        # Determine if the argument is required
        is_required = not has_default and not has_default_factory and use_default

        # Helper function to add the argument to the parser
        def add_argument(**kwargs):
            # Ensure default is passed only once
            if "default" not in kwargs:
                if use_type_defaults and field.default == dataclasses.MISSING:
                    kwargs["default"] = get_type_default(field_type)
                elif has_default:
                    kwargs["default"] = field.default
            kwargs["required"] = kwargs.get("required", is_required and enforce_required)
            parser.add_argument(arg_name, **kwargs)

        # Add argument based on the type of the field
        default_message = f"(default: {str(field.default)})" if has_default else ""
        kwargs = {"default": use_default} if use_default else {}
        if field_type == bool:
            add_argument(
                action="store_true",
                help=f"{field_name} flag {default_message}",
                **kwargs,
            )
        elif field_type == dict:
            add_argument(
                nargs="*",
                action=ParseDict,
                help=f"{field_name} flag {default_message}",
                **kwargs,
            )
        else:
            add_argument(
                type=field_type, help=f"{field_name} flag {default_message}", **kwargs
            )


def create_dataclass_from_args(
    dataclass_type: Type[Any], args_dict: dict, prefix: str = ""
):
    init_kwargs = {}
    for field in dataclasses.fields(dataclass_type):
        field_name = f"{prefix}{field.name}"
        field_type = field.type
        # Handle nested dataclasses
        if dataclasses.is_dataclass(field_type):
            value = create_dataclass_from_args(
                field_type,
                args_dict,
                prefix=f"{field_name}.",
            )
            init_kwargs[field.name] = value
            continue

        arg_name = field_name
        if arg_name in args_dict:
            value = args_dict[arg_name]
        else:
            if field.default != dataclasses.MISSING:
                value = field.default
            elif field.default_factory != dataclasses.MISSING:
                value = field.default_factory()
            else:
                value = get_type_default(field_type)
        init_kwargs[field.name] = value
    return dataclass_type(**init_kwargs)


def args_postproccessing(args):
    args["input_file"] = str(args.get("input_file", ""))

    return args
