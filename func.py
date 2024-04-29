#
# oci-azure-observability version 1.0
#
# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.

import io
import json
import logging
import os
import base64
from fdk import response

from func_azure_event_hub import post_to_azure_event_hub
from func_azure_workspace import post_to_azure_workspace

# Select Azure target service destination
azure_target = os.getenv('AZURE_TARGET', 'eventhub')

# Enable if the function will be processing events or logs passing through OCI Streaming
is_oci_streaming_conversion_enabled = eval(os.getenv('OCI_STREAMING_CONVERSION_ENABLED', "True"))

# Set all registered loggers to the configured log_level
logging_level = os.getenv('LOGGING_LEVEL', 'INFO')
loggers = [logging.getLogger()] + [logging.getLogger(name) for name in logging.root.manager.loggerDict]
[logger.setLevel(logging.getLevelName(logging_level)) for logger in loggers]

# --------------------------------------------
# Functions
# --------------------------------------------


def handler(ctx, data: io.BytesIO = None):
    """
    OCI Function Entrypoint
    :param ctx: OCI Function context
    :param data: message payload bytes object
    :return: None
    """

    try:

        log_body = data.getvalue()
        logging.info(f"{ctx.FnName()} / event payload bytes : {len(log_body)} / logging level: {logging_level}")

        if is_oci_streaming_conversion_enabled:
            log_body = convert_oci_streaming_format(log_body)

        if azure_target == 'eventhub':
            post_to_azure_event_hub(log_body)
        else:
            post_to_azure_workspace(log_body)

        return response.Response(ctx, response_data=json.dumps({"status": "Success"}),
                                 headers={"Content-Type": "application/json"})

    except Exception as err:
        logging.error("Error in handler: {}".format(str(err)))
        raise err


def convert_oci_streaming_format(body_bytes: bytes):
    """
    This function detects if the body is OCI Streaming format and converts it as needed to remove OCI
    Streaming preamble / wrapper JSON if that is the case.  Otherwise, it returns the original argument value.

    :param body_bytes: fn message body
    :return: converted / original payload
    """

    converted = list()
    event_list = json.loads(body_bytes)

    # The presence of 'stream', 'partition' and 'value' attributes per message indicate
    # that the list of events are in Streaming format.

    for event in event_list:
        stream = event.get('stream')
        partition = event.get('partition')
        value = event.get('value')

        if stream and partition and value:
            bytes_value = base64.b64decode(value)
            utf8_value = bytes_value.decode('utf-8')
            converted.append(json.loads(utf8_value))

        else:
            logging.debug('OCI Streaming format not detected')
            return body_bytes

    converted_bytes = bytes(json.dumps(converted), 'ascii')
    logging.debug('OCI Streaming format detected, conversion complete')

    return converted_bytes


def local_test_mode(filename):
    """
    Test routine
    """

    logging.info("testing {}".format(filename))

    with open(filename, 'r') as f:
        data = json.load(f)
        converted_bytes = bytes(json.dumps(data), 'ascii')
        post_to_azure_event_hub(body_bytes=converted_bytes)


"""
Local Testing 
"""

# if __name__ == "__main__":
    # local_test_mode('unittests_data/test.json')
    # local_test_mode('unittests_data/test-list.json')
