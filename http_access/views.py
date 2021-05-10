from typing import Union

from django.http import HttpResponseNotFound, StreamingHttpResponse, HttpResponse
from django.http.response import Http404
from django.shortcuts import get_object_or_404

from eoxserver.backends import models as backends
from eoxserver.resources.coverages import models as coverages

from .utils import parse_ranges, iter_file, wrap_streaming_content, generate_boundary, RangeNotSatisfiable, verify_file

def return_file(request, storage_name: str, path: str) -> Union[HttpResponseNotFound, StreamingHttpResponse, HttpResponse]:

    try:
        storage = get_object_or_404(backends.Storage, name=storage_name)
        data_item = get_object_or_404(coverages.ArrayDataItem, location=path, storage=storage)
        ranges = request.headers.get("Range", None)
        _, ranges = parse_ranges(ranges)


        if request.method == 'GET':
            if ranges:
                size = verify_file(data_item, ranges)
            response = StreamingHttpResponse(iter_file(data_item, ranges=ranges))
            if not ranges:
                response['Content-Type'] = 'image/tiff'
            else:
                boundary = generate_boundary()
                response.streaming_content = wrap_streaming_content(response.streaming_content, ranges, boundary, size)
                response['Content-Type'] = f'multipart/byteranges; boundary={boundary.decode()}'
                response.status_code = 206
        else:
            response = HttpResponse('<h1>Test<h1>')

        response['Access-Control-Allow-Origin'] = '*'
        response['Accept-Ranges'] = 'bytes'
        response['Access-Control-Allow-Methods']= 'POST, GET, OPTIONS'
        response['Access-Control-Allow-Headers']= 'X-PINGOTHER, Content-Type'
        response['Access-Control-Max-Age']= '86400'

        return response

    except Http404:
        return HttpResponseNotFound("<h1>404 file not found</h1>")

    except RangeNotSatisfiable:
        response = HttpResponse('<h1>416 requested range not satisfiable<h1>')
        response.status_code = 416
        return response
