# http_access

An extension of `eoxserver` that allows direct http access and range requests to access 
raster data.

## Install

To add to a django instance, edit the following files:

`settings.py`
```python
INSTALLED_APPS = (
    ...
    'http_access'
)
```

`urls.py`
```python
urlpatterns = [
    ...
    re_path(r'^http/', include('http_access.urls'))
]
```

## Usage

The files can directly be accessed with http range requests with the `Range` header, the
storage name (`STORAGE_NAME`) and the path to the file (`/PATH/TO/FILE`) in the storage.

```shell
curl -i -H "Range: bytes=15-60" http://host.com/<STORAGE_NAME>/<PATH/TO/FILE>
```
