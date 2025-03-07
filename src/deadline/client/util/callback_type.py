from __future__ import annotations

from abc import ABCMeta, abstractmethod

from typing import Any, Optional

from qtpy import QtWidgets
from deadline.client.ui.dialogs._types import JobBundlePurpose

from deadline.client.job_bundle.submission import AssetReferences
from .ui_callback import UICallbackResponse
from .create_job_bundle_callback import CREATE_JOB_BUNDLE_CALLBACK_NOOP
from .post_submit_callback import POST_SUBMIT_CALLBACK_NOOP
from .ui_callback import UI_CALLBACK_NOOP


class DeadlineCloudCallbackType(metaclass=ABCMeta):
    DEFAULT_CREATE_JOB_BUNDLE_CALLBACK = CREATE_JOB_BUNDLE_CALLBACK_NOOP
    DEFAULT_POST_SUBMIT_CALLBACK = POST_SUBMIT_CALLBACK_NOOP
    DEFAULT_UI_CALLBACK = UI_CALLBACK_NOOP
    @abstractmethod
    def on_ui_callback(
        self,
        dialog: QtWidgets.QDialog,
        settings: object,
        asset_references: AssetReferences,
        host_requirements: Optional[dict[str, Any]] = None,
    ) -> UICallbackResponse:
        pass

    @abstractmethod
    def on_create_job_bundle_callback(
        self,
        widget: QtWidgets.QDialog,
        job_bundle_dir: str,
        settings: object,
        queue_parameters: list[dict[str, Any]],
        asset_references: AssetReferences,
        host_requirements: Optional[dict[str, Any]] = None,
        purpose: JobBundlePurpose = JobBundlePurpose.SUBMISSION,
    ) -> None:
        pass

    @abstractmethod
    def on_post_submit_callback(
            self,
            job_id: str,
    ) -> None:
        pass
