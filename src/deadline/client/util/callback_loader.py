# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
import importlib.util
import inspect
import sys
from typing import Any, Optional, get_type_hints

from qtpy import QtWidgets
from deadline.client.ui.dialogs._types import JobBundlePurpose
from deadline.client.job_bundle.submission import AssetReferences


def _reference_callback_signature(
    widget: QtWidgets.QDialog,
    job_bundle_dir: str,
    settings: object,
    queue_parameters: list[dict[str, Any]],
    asset_references: AssetReferences,
    host_requirements: Optional[dict[str, Any]] = None,
    purpose: JobBundlePurpose = JobBundlePurpose.SUBMISSION,
):
    pass


CALLBACK_REFERENCE_SIGNATURE = inspect.signature(_reference_callback_signature).parameters
CALLBACK_REFERENCE_HINTS = get_type_hints(_reference_callback_signature)


def import_module_function(module_path, module_name, function_name):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return getattr(mod, function_name)


def import_module_class(module_path, module_name, class_type):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    _classes = []
    for attr in filter(lambda x: isinstance(getattr(mod, x), type), dir(mod)):
        if issubclass(getattr(mod, attr), class_type):
            _class = getattr(mod, attr)
            if not hasattr(_class, "__abstractmethods__") or not _class.__abstractmethods__:
                return _class
    raise ImportError("Could not find class object as a fully concrete class of type {}".format(class_type.__name__))


def _validate_parameter_type(parameter_type, other_type):
    if parameter_type == other_type:
        return True

    if parameter_type in other_type.__bases__:
        return True
    return False


def validate_function_signature(function, reference_signature=CALLBACK_REFERENCE_SIGNATURE, hints=CALLBACK_REFERENCE_HINTS):
    parameters = inspect.signature(function).parameters
    if parameters == reference_signature:
        return True

    function_hints = get_type_hints(function)

    for param_name in hints:
        if not function_hints.get(param_name):
            return False
        if not _validate_parameter_type(
            hints[param_name], function_hints[param_name]
        ):
            return False
    return True
