"""Config."""

import os

PROJECT_NAME = "titiler"

SERVER_NAME = os.getenv("SERVER_NAME")
SERVER_HOST = os.getenv("SERVER_HOST")
BACKEND_CORS_ORIGINS = os.getenv(
    "BACKEND_CORS_ORIGINS", default="*"
)  # a string of origins separated by commas, e.g: "http://localhost, http://localhost:4200, http://localhost:3000, http://localhost:8080, http://local.dockertoolbox.tiangolo.com"

DISABLE_CACHE = os.getenv("DISABLE_CACHE")
MEMCACHE_HOST = os.environ.get("MEMCACHE_HOST")
MEMCACHE_PORT = int(os.environ.get("MEMCACHE_PORT", 11211))
MEMCACHE_USERNAME = os.environ.get("MEMCACHE_USERNAME")
MEMCACHE_PASSWORD = os.environ.get("MEMCACHE_PASSWORD")

DEFAULT_MOSAIC_BACKEND = os.getenv("DEFAULT_MOSAIC_BACKEND", "s3://")
DEFAULT_MOSAIC_HOST = os.getenv("DEFAULT_MOSAIC_HOST", "")
