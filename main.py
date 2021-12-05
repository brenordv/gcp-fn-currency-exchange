# -*- coding: utf-8 -*-
"""main.py
Main file that wraps the routines in the GCP function.

"""
import logging
from sys import exit
from simple_log_factory.log_factory import log_factory
from google.cloud.functions_v1.context import Context
from google.cloud import error_reporting

from func import check_quote
from utils import StopWatch

FN_NAME = "QUOTE_EXCHANGE_FN"


def main_pubsub(event: dict, context: Context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
         event (dict):  The dictionary with data specific to this type of
                        event. The `@type` field maps to
                         `type.googleapis.com/google.pubsub.v1.PubsubMessage`.
                        The `data` field maps to the PubsubMessage data
                        in a base64-encoded string. The `attributes` field maps
                        to the PubsubMessage attributes if any is present.
         context (google.cloud.functions.Context): Metadata of triggering event
                        including `event_id` which maps to the PubsubMessage
                        messageId, `timestamp` which maps to the PubsubMessage
                        publishTime, `event_type` which maps to
                        `google.pubsub.topic.publish`, and `resource` which is
                        a dictionary that describes the service API endpoint
                        pubsub.googleapis.com, the triggering topic's name, and
                        the triggering event type
                        `type.googleapis.com/google.pubsub.v1.PubsubMessage`.
    Returns:
        None. The output is written to Cloud Logging.
    """
    logger: logging = log_factory(log_name=FN_NAME)
    stopwatch = StopWatch(auto_start=True)

    client = error_reporting.Client()
    exit_code = 0

    try:
        logger.info(f"Start {FN_NAME}...")
        check_quote()

    except Exception as e:
        # Even thou the error is reported back, I'll log it just to see where it will be shown...
        logger.error(f"Error running function: {e}")

        # This will report the error back to GCP.
        client.report_exception()

        exit_code = -1

    elapsed_time = stopwatch.end()
    logger.info(f"All done! Elapsed time: {elapsed_time}")

    if exit_code == 0:
        return

    exit(exit_code)
