from io import BytesIO
import json
from typing import Union

import boto3
import requests
from keystoneauth1 import session
from keystoneauth1.identity import v3
from swiftclient.client import Connection
from swiftclient.exceptions import ClientException
from botocore import UNSIGNED
from botocore.exceptions import ClientError
from botocore.config import Config

from django.http import HttpResponse, HttpResponseNotFound, StreamingHttpResponse
from django.http.response import Http404
from django.shortcuts import get_object_or_404

from eoxserver.backends import models as backends
from eoxserver.resources.coverages import models as coverages
from eoxserver.backends.access import vsi_open

def get_s3_file(path: str, _range: str, storage: backends.Storage) -> Union[HttpResponse, HttpResponseNotFound, StreamingHttpResponse]:
    storage_auth = json.loads(storage.storage_auth.auth_parameters)
    bucket = storage.url

    s3 = boto3.client(
        "s3",
        aws_access_key_id=storage_auth["ACCESS_KEY_ID"],
        aws_secret_access_key=storage_auth["SECRET_ACCESS_KEY"],
        config=Config(signature_version=UNSIGNED) if storage_auth.get("PUBLIC", False) else None,
    )

    try:
        if _range:
            resp = s3.get_object(Bucket=bucket, Key=path, Range=_range)
            b = BytesIO(resp["Body"].read())
            response = HttpResponse(b, content_type="application/octet-stream")
        else:
            url = s3.generate_presigned_url(
                ClientMethod="get_object", 
                ExpiresIn=3600,
                Params={
                    "Bucket": bucket,
                    "Key": path,
                },
            )
            r = requests.get(url=url, stream=True)
            r.raise_for_status()
            response = StreamingHttpResponse(r.raw, content_type="application/octet-stream")
    except (IOError, ClientError):
        response = HttpResponseNotFound("<h1>File not found</h1>")

    return response


def get_swift_file(path: str, _range: str, storage: backends.Storage) -> Union[HttpResponse, HttpResponseNotFound]:

    bucket = storage.url
    storage_auth = storage.storage_auth
    url = storage_auth.url
    storage_auth = json.loads(storage.storage_auth.auth_parameters)
    auth = v3.Password(
        auth_url=url,
        username=storage_auth["username"],
        password=storage_auth["password"],
        # user_domain_name="Default",
        # project_name="test",
        # project_domain_name="Default",
    )
    keystone_session = session.Session(auth=auth)
    swift_conn = Connection(session=keystone_session)

    try:
        if _range:
            _, obj = swift_conn.get_object(bucket, path, headers={"Range": _range})
            b = BytesIO(obj)
            response = HttpResponse(b, content_type="application/octet-stream")
        else:
            _, obj = swift_conn.get_object(bucket, path)
            response = HttpResponse(obj, content_type="application/octet-stream")
    except (IOError, ClientException):
        response = HttpResponseNotFound("<h1>File not found</h1>")
    return response


def return_file(request, storage_name: str, path: str) -> Union[HttpResponse, HttpResponseNotFound]:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    debugpy.wait_for_client()

    try:
        storage = get_object_or_404(backends.Storage, name=storage_name)
        _ = get_object_or_404(coverages.ArrayDataItem, location=path)
        _range = request.headers.get("Range", None)

    except Http404:
        return HttpResponseNotFound("<h1>File not found</h1>")
    
    storage_type = storage.storage_type
    try:
        if storage_type.lower() == "swift":
            return get_swift_file(path, _range, storage)
        elif storage_type.lower() == "s3":
            return get_s3_file(path, _range, storage)
        else:
            return HttpResponseNotFound("<h1>File not found</h1>")
    except Exception as e:
        return HttpResponse(e, status=500)
