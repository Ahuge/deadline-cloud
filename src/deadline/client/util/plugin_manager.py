# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""UI Components for the Render Submitter"""
from __future__ import annotations

import os
from typing import Any, Optional

from deadline.client.util.callback_loader import import_module_class
from deadline.client.util.callback_type import DeadlineCloudCallbackType
from deadline.client.util.create_job_bundle_callback import CREATE_JOB_BUNDLE_CALLBACK_NOOP
from deadline.client.util.post_submit_callback import POST_SUBMIT_CALLBACK_NOOP
from deadline.client.util.ui_callback import UI_CALLBACK_NOOP

from deadline.client.ui.dialogs.submit_job_to_deadline_dialog import SubmitJobToDeadlineDialog

from deadline.client.job_bundle.submission import AssetReferences
from deadline.client.ui.dialogs._types import JobBundlePurpose


class PluginManager(object):
    def __init__(self, plugin_directory=None):
        super(PluginManager, self).__init__()
        self._plugins = []
        if plugin_directory is not None:
            self._initialize_plugin_directory(plugin_directory)

    def _initialize_plugin_directory(self, plugins_dir):
        for plugin_file in os.listdir(plugins_dir):
            _class = import_module_class(
                module_path=os.path.join(plugins_dir, plugin_file),
                module_name=os.path.splitext(plugin_file)[0],
                class_type=DeadlineCloudCallbackType
            )
            self._plugins.append(_class)

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
            on_create_job_bundle_callback = create_job_bundle_callback
            on_ui_callback = ui_callback
            on_post_submit_callback = post_submit_callback

        self._plugins.append(HookPlugin)

    def call_post_submit_hook(self, job_id: str):
        for _plugin in self._plugins:
            _plugin.call_post_submit_hook(
                job_id=job_id,
            )

    def call_create_job_bundle_callback(
            self,
            widget: SubmitJobToDeadlineDialog,
            job_bundle_dir: str,
            settings: object,
            queue_parameters: list[dict[str, Any]],
            asset_references: AssetReferences,
            host_requirements: Optional[dict[str, Any]] = None,
            purpose: JobBundlePurpose = JobBundlePurpose.SUBMISSION,
    ):
        for _plugin in self._plugins:
            _plugin.on_create_job_bundle_callback(
                widget=widget,
                job_bundle_dir=job_bundle_dir,
                settings=settings,
                queue_parameters=queue_parameters,
                asset_references=asset_references,
                host_requirements=host_requirements,
                purpose=purpose,
            )

    def call_ui_hook(self, job_settings, asset_references, host_requirements=None):
        job_uis = []
        for _plugin in self._plugins:
            job_settings, asset_references, host_requirements, job_ui = self._call_ui_hook(
                _plugin, job_settings, asset_references, host_requirements
            )
            if job_ui is not None:
                job_uis.append(job_ui)
        return job_settings, asset_references, host_requirements, job_uis

    def _call_ui_hook(self, plugin, job_settings, asset_references, host_requirements=None):
        host_requirements = None
        job_ui = None

        ui_callback_response = plugin.on_ui_callback(
            dialog=self,
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
