# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""UI Components for the Render Submitter"""
from __future__ import annotations

import logging
import os
from typing import Any, Optional

from .callback_loader import import_module_class
from .callback_type import DeadlineCloudCallbackType
from .create_job_bundle_callback import CREATE_JOB_BUNDLE_CALLBACK_NOOP
from .post_submit_callback import POST_SUBMIT_CALLBACK_NOOP
from .ui_callback import UI_CALLBACK_NOOP

from qtpy import QtWidgets

from deadline.client.job_bundle.submission import AssetReferences
from deadline.client.ui.dialogs._types import JobBundlePurpose

logger = logging.getLogger(__name__)


class PluginManager(object):
    def __init__(self, plugin_directory=None):
        super(PluginManager, self).__init__()
        self._plugins = []
        if plugin_directory is not None:
            self._initialize_plugin_directory(plugin_directory)

        # Default Deadline Cloud Plugins
        self._initialize_plugin_directory(os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins"))

    def _initialize_plugin_directory(self, plugins_dir):
        for plugin_file in filter(lambda pf: pf.endswith(".py") and pf != "__init__.py", os.listdir(plugins_dir)):
            print("Loading plugin: {}".format(plugin_file))
            _class = import_module_class(
                module_path=os.path.join(plugins_dir, plugin_file),
                module_name=os.path.splitext(plugin_file)[0],
                class_type=DeadlineCloudCallbackType
            )
            _instance = _class()
            _instance.PluginName = os.path.splitext(plugin_file)[0]
            _instance.PluginLocation = os.path.join(plugins_dir, plugin_file)
            self._plugins.append(_instance)

    def create_hook_plugin(self, create_job_bundle_callback=None, ui_callback=None, post_submit_callback=None):
        if all(map(lambda x: x is None, [create_job_bundle_callback, ui_callback, post_submit_callback])):
            # No need to create a HookPlugin
            return

        if create_job_bundle_callback is None:
            create_job_bundle_callback = CREATE_JOB_BUNDLE_CALLBACK_NOOP
        if ui_callback is None:
            ui_callback = UI_CALLBACK_NOOP
        if post_submit_callback is None:
            post_submit_callback = POST_SUBMIT_CALLBACK_NOOP

        class HookPlugin(DeadlineCloudCallbackType):
            def on_create_job_bundle_callback(self, *args, **kwargs):
                return create_job_bundle_callback(*args, **kwargs)

            def on_ui_callback(self, *args, **kwargs):
                return ui_callback(*args, **kwargs)

            def on_post_submit_callback(self, *args, **kwargs):
                return post_submit_callback(*args, **kwargs)

        _instance = HookPlugin()
        _instance.PluginName = "hook_plugin"
        _instance.PluginLocation = "environment"
        self._plugins.insert(0, _instance)

    def call_post_submit_hook(self, job_id: str):
        for _plugin in self._plugins:
            _plugin.on_post_submit_callback(
                job_id=job_id,
            )

    def call_create_job_bundle_callback(
            self,
            widget: QtWidgets.QDialog,
            job_bundle_dir: str,
            settings: object,
            queue_parameters: list[dict[str, Any]],
            asset_references: AssetReferences,
            host_requirements: Optional[dict[str, Any]] = None,
            purpose: JobBundlePurpose = JobBundlePurpose.SUBMISSION,
    ):
        for _plugin in self._plugins:
            logger.info("Calling on_create_job_bundle_callback for plugin: {}".format(_plugin.PluginName))
            _plugin.on_create_job_bundle_callback(
                widget=widget,
                job_bundle_dir=job_bundle_dir,
                settings=settings,
                queue_parameters=queue_parameters,
                asset_references=asset_references,
                host_requirements=host_requirements,
                purpose=purpose,
            )

    def call_ui_hook(
            self,
            dialog: QtWidgets.QDialog,
            job_settings: object,
            asset_references: AssetReferences,
            host_requirements: Optional[dict[str, Any]] = None,
    ):
        job_uis = []
        for _plugin in self._plugins:
            job_settings, asset_references, host_requirements, job_ui = self._call_ui_hook(
                plugin=_plugin, dialog=dialog, job_settings=job_settings,
                asset_references=asset_references, host_requirements=host_requirements
            )
            if job_ui is not None:
                job_ui.setToolTip("Plugin {plugin_name} loaded from {location}".format(
                    plugin_name=_plugin.PluginName,
                    location=_plugin.PluginLocation,
                ))
                job_uis.append(job_ui)
        return job_settings, asset_references, host_requirements, job_uis

    def _call_ui_hook(self, plugin, dialog, job_settings, asset_references, host_requirements=None):
        job_ui = None

        ui_callback_response = plugin.on_ui_callback(
            dialog=dialog,
            settings=job_settings,
            asset_references=asset_references,
            host_requirements=host_requirements,
        )
        if ui_callback_response.settings:
            job_settings = ui_callback_response.settings
        if ui_callback_response.asset_references:
            asset_references = ui_callback_response.asset_references
        if ui_callback_response.host_requirements:
            host_requirements = ui_callback_response.host_requirements
        if ui_callback_response.job_specific_ui:
            job_ui = ui_callback_response.job_specific_ui

        return job_settings, asset_references, host_requirements, job_ui
