from __future__ import annotations

import os

import uvicorn

from app import create_app, init_logger
from app.settings import AppSettings

app_settings = AppSettings()

init_logger(app_settings)

app = create_app(app_settings)

if __name__ == "__main__":
    bind_addr = os.getenv("BIND_ADDRESS")
    if bind_addr is None:
        uvicorn.run(app, host="127.0.0.1", port=4000)
    elif bind_addr.startswith("unix://"):
        uvicorn.run(app, uds=bind_addr.removeprefix("unix://"))
    else:
        host, port = bind_addr.split(":")
        uvicorn.run(app, host=host, port=int(port))
