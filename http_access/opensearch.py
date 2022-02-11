from typing import List, Tuple

from django.urls import reverse
from eoxserver.resources.coverages import models as coverages


def get_coverage_links(request, coverage: coverages.Coverage) -> List[Tuple[str, str]]:
    links = []
    for array_data_item in coverage.arraydata_items.all():
        if array_data_item.storage:
            storage_name = array_data_item.storage.name
            url = reverse(
                "http_access:file",
                kwargs={"storage_name": storage_name, "path": array_data_item.location},
            )
        else:
            url = reverse(
                "http_access:file-local",
                kwargs={"path": array_data_item.location},
            )
        href = request.build_absolute_uri(url)
        links.append(("via", href))

    return links


class HttpAccessResultItemFeedLinkGenerator:
    def get_links(self, request, item: coverages.EOObject) -> List[Tuple[str, str]]:
        if isinstance(item, coverages.Coverage):
            return get_coverage_links(request, item)
        elif isinstance(item, coverages.Product):
            links = []
            for coverage in item.coverages.all():
                links.extend(get_coverage_links(request, coverage))
            return links
        return []
