# Copyright 2019 Copyright (c) 2019 SAP SE or an SAP affiliate company. All rights reserved. This file is licensed under the Apache Software License, v. 2 except as noted otherwise in the LICENSE file.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import yaml
import os
from functools import reduce

class ConfigValidator:
    @staticmethod
    def validate_str(clazz, config):
         if not isinstance(config, str):
            raise TypeError("Incorrect type for {} config. Required str, got {}.".format(clazz, type(config)))

    @staticmethod
    def validate_dict(clazz, config):
        if not isinstance(config, dict):
            raise TypeError("Incorrect type for {} config. Required dict, got {}.".format(clazz, type(config)))

        if not ConfigValidator.__is_dict_config_valid(config, clazz.__dict__.get("required_keys"), clazz.__dict__.get("optional_keys")):
            raise ValueError("Config for {} is not in the correct format.".format(clazz))

        for base in clazz.__bases__:
            if not ConfigValidator.__is_dict_config_valid(config, base.__dict__.get("required_keys"), base.__dict__.get("optional_keys")):
                raise ValueError("Config for {} is not in the correct format.".format(clazz))

    @staticmethod
    def __is_dict_config_valid(config, required_keys, optional_keys=None):
        validate_required_keys = lambda key: False if key["key"] not in config.keys() or not isinstance(config[key["key"]], key["types"]) else True
        validate_optional_keys = lambda key: False if key["key"] in config.keys() and not isinstance(config[key["key"]], key["types"]) else True
        reducer = lambda x, y: x and y

        return (required_keys is None or len(required_keys) == 0 or reduce(reducer, map(validate_required_keys, required_keys))) \
            and (optional_keys is None or len(optional_keys) == 0 or reduce(reducer, map(validate_optional_keys, optional_keys)))

def parse_dockerfile_config_yaml(dockerfile_config_path):
    components = None
    with open(dockerfile_config_path, "r") as tools_config_file:
        components = yaml.load(tools_config_file, yaml.SafeLoader)
    if components is None:
        print("Couldnt read from file {}.".format(dockerfile_config_path))
        exit(1)
    return components

def parse_dockerfile_configs(dockerfile_config_path, additional_config_paths):
    dockerfile_config = parse_dockerfile_config_yaml(os.path.abspath(dockerfile_config_path))
    for sub_array in additional_config_paths:
        for additional_config_path in sub_array:
            additional_dockerfile_config = parse_dockerfile_config_yaml(os.path.abspath(additional_config_path))
            dockerfile_config.extend(additional_dockerfile_config)

    return dockerfile_config