"""titiler.api.utils."""

import hashlib
import json
import time
from io import BytesIO
from typing import Any, Dict, Optional, Tuple

import affine
import numpy
from rasterio.crs import CRS
from rio_color.operations import parse_operations
from rio_color.utils import scale_dtype, to_math_type
from rio_tiler.profiles import img_profiles
from rio_tiler.utils import _chunks, linear_rescale, render

from titiler.db.memcache import CacheLayer
from titiler.ressources.common import drivers
from titiler.ressources.enums import ImageType

from starlette.requests import Request


def get_cache(request: Request) -> Optional[CacheLayer]:
    """Get Memcached Layer."""
    try:
        return request.state.cache
    except AttributeError:
        return None


def get_hash(**kwargs: Any) -> str:
    """Create hash from a dict."""
    return hashlib.sha224(json.dumps(kwargs, sort_keys=True).encode()).hexdigest()


def postprocess(
    tile: numpy.ndarray,
    mask: numpy.ndarray,
    rescale: Optional[str] = None,
    color_formula: Optional[str] = None,
) -> numpy.ndarray:
    """Post-process tile data."""
    if rescale:
        rescale_arr = list(map(float, rescale.split(",")))
        rescale_arr = list(_chunks(rescale_arr, 2))
        if len(rescale_arr) != tile.shape[0]:
            rescale_arr = ((rescale_arr[0]),) * tile.shape[0]

        for bdx in range(tile.shape[0]):
            tile[bdx] = numpy.where(
                mask,
                linear_rescale(
                    tile[bdx], in_range=rescale_arr[bdx], out_range=[0, 255]
                ),
                0,
            )
        tile = tile.astype(numpy.uint8)

    if color_formula:
        # make sure one last time we don't have
        # negative value before applying color formula
        tile[tile < 0] = 0
        for ops in parse_operations(color_formula):
            tile = scale_dtype(ops(to_math_type(tile)), numpy.uint8)

    return tile


def reformat(
    data: numpy.ndarray,
    mask: numpy.ndarray,
    img_format: ImageType,
    colormap: Optional[Dict[int, Tuple[int, int, int, int]]] = None,
    transform: Optional[affine.Affine] = None,
    crs: Optional[CRS] = None,
):
    """Reformat image data to bytes"""
    if img_format == ImageType.npy:
        sio = BytesIO()
        numpy.save(sio, (data, mask))
        sio.seek(0)
        content = sio.getvalue()
    else:
        driver = drivers[img_format.value]
        options = img_profiles.get(driver.lower(), {})
        if transform and crs and ImageType.tif in img_format:
            options = {"crs": crs, "transform": transform}

        content = render(data, mask, img_format=driver, colormap=colormap, **options)
    return content


# This code is copied from marblecutter
#  https://github.com/mojodna/marblecutter/blob/master/marblecutter/stats.py
# License:
# Original work Copyright 2016 Stamen Design
# Modified work Copyright 2016-2017 Seth Fitzsimmons
# Modified work Copyright 2016 American Red Cross
# Modified work Copyright 2016-2017 Humanitarian OpenStreetMap Team
# Modified work Copyright 2017 Mapzen
class Timer(object):
    """Time a code block."""

    def __enter__(self):
        """Starts timer."""
        self.start = time.time()
        return self

    def __exit__(self, ty, val, tb):
        """Stops timer."""
        self.end = time.time()
        self.elapsed = self.end - self.start
