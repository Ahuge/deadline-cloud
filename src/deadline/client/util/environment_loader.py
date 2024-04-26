import os


from . import ui_callback, post_submit_callback, create_job_bundle_callback
from deadline.client.exceptions import DeadlineOperationError


def load_dcc_environment_callbacks(dcc_name: str):
    on_create_job_bundle_callback = None
    on_ui_callback = None
    on_post_submit_callback = None

    if os.path.exists(os.environ.get("DEADLINE_{dcc}_CREATE_JOB_BUNDLE_CALLBACK".format(dcc=dcc_name.upper()), "")):
        try:
            on_create_job_bundle_callback = create_job_bundle_callback.load_create_job_bundle_callback(
                module_path=os.environ.get("DEADLINE_{dcc}_CREATE_JOB_BUNDLE_CALLBACK".format(dcc=dcc_name.upper()))
            )
        except Exception:
            import traceback
            raise DeadlineOperationError(
                "Error while loading on_create_job_bundle_callback at {path}. {trace}".format(
                    path=os.environ.get("DEADLINE_{dcc}_CREATE_JOB_BUNDLE_CALLBACK".format(dcc=dcc_name.upper())),
                    trace=traceback.format_exc()
                )
            )

    if os.path.exists(os.environ.get("DEADLINE_{dcc}_UI_CALLBACK".format(dcc=dcc_name.upper()), "")):
        try:
            on_ui_callback = ui_callback.load_ui_callback(
                module_path=os.environ.get("DEADLINE_{dcc}_UI_CALLBACK".format(dcc=dcc_name.upper()))
            )
        except Exception:
            import traceback
            raise DeadlineOperationError(
                "Error while loading on_pre_submit_callback at {path}. {trace}".format(
                    path=os.environ.get("DEADLINE_{dcc}_UI_CALLBACK".format(dcc=dcc_name.upper())),
                    trace=traceback.format_exc()
                )
            )

    if os.path.exists(os.environ.get("DEADLINE_{dcc}_POST_SUBMIT_CALLBACK".format(dcc=dcc_name.upper()), "")):
        try:
            on_post_submit_callback = post_submit_callback.load_post_submit_callback(
                module_path=os.environ.get("DEADLINE_{dcc}_POST_SUBMIT_CALLBACK".format(dcc=dcc_name.upper())),
            )
        except Exception:
            import traceback
            raise DeadlineOperationError(
                "Error while loading on_post_submit_callback at {path}. {trace}".format(
                    path=os.environ.get("DEADLINE_{dcc}_POST_SUBMIT_CALLBACK".format(dcc=dcc_name.upper())),
                    trace=traceback.format_exc()
                )
            )
    return on_ui_callback, on_post_submit_callback, on_create_job_bundle_callback
