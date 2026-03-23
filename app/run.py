import asyncio
import contextlib

from typing import Any

import uvicorn

from app.core.config import settings
from app.core.app_factory import app


async def main() -> None:
    server_configs: dict[str, Any] = {
        "proxy_headers": True,
        "forwarded_allow_ips": "*",
        "host": settings.HOST,
        "port": settings.PORT,
    }

    config = uvicorn.Config(
        app,
        **server_configs,
    )

    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
