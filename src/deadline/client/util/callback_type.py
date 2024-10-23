from __future__ import annotations

from abc import ABCMeta, abstractmethod

from typing import Any, Optional

from deadline.client.ui.dialogs.submit_job_to_deadline_dialog import (  # type: ignore
    SubmitJobToDeadlineDialog,
    JobBundlePurpose,
)

from deadline.client.job_bundle.submission import AssetReferences
from deadline.client.util.ui_callback import UICallbackResponse


class DeadlineCloudCallbackType(metaclass=ABCMeta):
    @abstractmethod
    def on_ui_callback(
        self,
        dialog: SubmitJobToDeadlineDialog,
        settings: object,
        asset_references: AssetReferences,
        host_requirements: Optional[dict[str, Any]] = None,
    ) -> UICallbackResponse:
        pass

    @abstractmethod
    def on_create_job_bundle_callback(
        self,
        widget: SubmitJobToDeadlineDialog,
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
