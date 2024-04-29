#
# oci-azure-observability version 1.0
#
# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.

import base64
import hashlib
import hmac
import json
import logging
import os
import time
import urllib

import requests

"""
see https://learn.microsoft.com/en-us/rest/api/eventhub/send-event
see https://learn.microsoft.com/en-us/rest/api/eventhub/generate-sas-token
"""


service_bus_namespace = os.getenv('AZURE_SERVICE_BUS_NAMESPACE', 'not-configured')
event_hub_path = os.getenv('AZURE_EVENT_HUB_PATH', 'not-configured')
sas_key_name = os.getenv('AZURE_SAS_KEY_NAME', 'not-configured')
sas_key = os.getenv('AZURE_SAS_KEY', 'not-configured')


def post_to_azure_event_hub(body_bytes: bytes):
    """
    Sends each event to Azure Event Hub Endpoint.
    """

    api_endpoint = "https://{}.servicebus.windows.net/{}/messages".format(service_bus_namespace, event_hub_path)
    session = requests.Session()

    try:
        logging.info("starting adapter session")
        adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10)
        session.mount('https://', adapter)
        http_headers = {'Content-type': 'application/atom+xml;type=entry;charset=utf-8',
                        'Authorization': build_azure_event_hub_sas_token(),
                        'Host': '{}.servicebus.windows.net'.format(service_bus_namespace)}

        event_list = json.loads(body_bytes)
        if not isinstance(event_list, list):
            event_list = [event_list]

        for event in event_list:
            post_response = session.post(api_endpoint, data=json.dumps(event), headers=http_headers)
            if post_response.status_code != 201:
                raise Exception('error posting to API endpoint', post_response.text, post_response.reason)

    finally:
        logging.info("closing adapter session")
        session.close()


def build_azure_event_hub_sas_token():
    """
    Returns an authorization token dictionary
    for making calls to Event Hubs REST API.
    See https://learn.microsoft.com/en-us/rest/api/eventhub/generate-sas-token
    """

    uri = urllib.parse.quote_plus("https://{}.servicebus.windows.net/{}".format(service_bus_namespace, event_hub_path))
    sas = sas_key.encode('utf-8')
    expiry = str(int(time.time() + 10000))
    string_to_sign = (uri + '\n' + expiry).encode('utf-8')
    signed_hmac_sha256 = hmac.HMAC(sas, string_to_sign, hashlib.sha256)
    signature = urllib.parse.quote(base64.b64encode(signed_hmac_sha256.digest()))

    # se – Token expiry instant. Integer reflecting seconds since epoch 00:00:00 UTC on 1 January 1970 (UNIX epoch)
    # skn – Name of the authorization rule, which is the SAS key name.
    # sr – URI of the resource being accessed.
    # sig – Signature.

    return 'SharedAccessSignature sr={}&sig={}&se={}&skn={}'.format(uri, signature, expiry, sas_key_name)

