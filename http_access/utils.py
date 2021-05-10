import string
import random
import re
from typing import Generator, List, Tuple, Union

from eoxserver.resources.coverages import models as coverages
from eoxserver.backends.access import vsi_open
import eoxserver.core.util.multiparttools as mp

class RangeNotSatisfiable(Exception):
    pass

def iter_file(data_item: coverages.ArrayDataItem, ranges: List[Tuple]=None, chunk_size: int=65000) -> Generator:
    with vsi_open(data_item) as r:
        if ranges:
            for _r in ranges:
                bottom = _r[0]
                top = _r[1]

                if bottom is not None and top is not None:
                    r.seek(bottom, 0)
                    while bottom < top:
                        yield r.read(min(top - bottom + 1, chunk_size))
                        bottom += chunk_size
                elif bottom is not None and top is None:
                    r.seek(bottom, 0)
                    while True:
                        data = r.read(chunk_size)
                        if not data:
                            break
                        yield data

                elif bottom is None and top is not None:
                    r.seek(-top, 2)
                    while True:
                        data = r.read(chunk_size)
                        if not data:
                            break
                        yield data
                else:
                    continue
        else:
            while True:
                data = r.read(chunk_size)
                if not data:
                    break
                yield data

def parse_ranges(ranges: Union[str, None]) -> Tuple[str, List]:
    if ranges:
        ranges = re.match(r'bytes=((\d*-\d*,?)+)', ranges)
        if not ranges:
            raise RangeNotSatisfiable('Requested Range Not Satisfiable')

        ranges = ranges.group()
        units, ranges  = ranges.split('=')

        range_list = []
        ranges = ranges.split(',')
        for range in ranges:
            start_index, end_index = range.split('-')
            try:
                start_index = int(start_index)
            except ValueError:
                start_index = None
            try:
                end_index = int(end_index)
            except ValueError:
                end_index = None

            if (start_index and end_index) and start_index > end_index:
                raise RangeNotSatisfiable('Requested Range Not Satisfiable')
            if not start_index and not end_index:
                raise RangeNotSatisfiable('Requested Range Not Satisfiable')
            range_list.append((start_index, end_index))


        return units, range_list
    
    return None, []

def wrap_streaming_content(content: map, ranges: List[Tuple], boundary: str, size: str='*') -> Generator:
    for chunk, _r in zip(content, ranges):
        yield wrap_chunk(chunk, _r, boundary, size)
    yield b'--' + boundary + b'--'

def wrap_chunk(chunk: bytes, _r: Tuple[int], boundary: str, size: str='*') -> bytes:
    type = b'Content-Type: image/tiff\n'
    range = f'Content-Range: bytes {_r[0] or ""}-{_r[1] or ""}/{size}\n'.encode()
    chunk = b'--' + boundary + b'\n' + type + range + b'\n' + chunk + b'\n'
    return chunk

def generate_boundary() -> str:
    characters = string.ascii_lowercase + string.digits
    result_str = ''.join(random.sample(characters, 8))
    return str.encode(result_str)

def verify_file(data_item, ranges: List[Tuple]=[]):
    with vsi_open(data_item) as r:  
        r.seek(0, 2)
        size = r.tell()
        for _r in ranges:
            bottom = _r[0]
            if bottom and bottom > size:
                raise RangeNotSatisfiable("Range Not Satisfiable")

    return str(size)
