from typing import Optional, Union

from django.http import HttpResponseNotFound, StreamingHttpResponse, HttpResponse
from django.http.response import Http404
from django.shortcuts import get_object_or_404

from eoxserver.backends import models as backends
from eoxserver.resources.coverages import models as coverages

from .utils import (
    parse_ranges,
    iter_file,
    wrap_streaming_content,
    generate_boundary,
    RangeNotSatisfiable,
    verify_file,
)


def return_file(
    request, path: str, storage_name: Optional[str] = None
) -> Union[HttpResponseNotFound, StreamingHttpResponse, HttpResponse]:
    try:
        if storage_name:
            storage = get_object_or_404(backends.Storage, name=storage_name)
        else:
            storage = None

        data_item = get_object_or_404(
            coverages.ArrayDataItem, location=path, storage=storage
        )
        ranges = request.headers.get("Range", None)
        _, ranges = parse_ranges(ranges)

        size = verify_file(data_item, ranges)
        if request.method == "GET":
            response = StreamingHttpResponse(iter_file(data_item, ranges=ranges))
            if not ranges:
                response["Content-Type"] = "image/tiff"
            elif len(ranges) == 1:
                _r = ranges[0]
                response["Content-Type"] = "image/tiff"
                response["Content-Range"] = f"bytes {_r[0]}-{_r[1]}/{size}"
                response.status_code = 206
            else:
                boundary = generate_boundary()
                response.streaming_content = wrap_streaming_content(
                    response.streaming_content, ranges, boundary, size
                )
                response[
                    "Content-Type"
                ] = f"multipart/byteranges; boundary={boundary.decode()}"
                response.status_code = 206
        else:
            response = HttpResponse("")
            response["Content-Type"] = "image/tiff"
            response["Content-Length"] = str(size)

        response["Access-Control-Allow-Origin"] = "*"
        response["Accept-Ranges"] = "bytes"
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, HEAD"
        response["Access-Control-Allow-Headers"] = "X-PINGOTHER, Content-Type, Range"
        response["Access-Control-Max-Age"] = "86400"

        return response

    except Http404:
        return HttpResponseNotFound("<h1>404 file not found</h1>")

    except RangeNotSatisfiable:
        response = HttpResponse("<h1>416 requested range not satisfiable<h1>")
        response.status_code = 416
        return response
