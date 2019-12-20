from typing import Optional, Type

from .errors import ContentSizeExceeded

from .logger import get_logger


class ContentSizeLimitMiddleware:
    """ Content size limiting middleware for ASGI applications

    Args:
      app (ASGI application): ASGI application
      max_content_size (optional): the maximum content size allowed in bytes, None for no limit
      exception_cls (optional): the class of exception to raise (ContentSizeExceeded is the default)
    """

    def __init__(
        self,
        app,
        max_content_size: Optional[int] = None,
        exception_cls: Optional[Type[Exception]] = None,
    ):
        self.app = app
        self.max_content_size = max_content_size
        if exception_cls is None:
            self.exception_cls = ContentSizeExceeded
        else:
            self.exception_cls = exception_cls

        self.logger = get_logger(__name__)

    def receive_wrapper(self, receive):
        received = 0

        async def inner():
            nonlocal received
            message = await receive()
            if message["type"] != "http.request" or self.max_content_size is None:
                return message
            body_len = len(message.get("body", b""))
            received += body_len
            if received > self.max_content_size:
                raise self.exception_cls(
                    f"Maximum content size limit ({self.max_content_size}) exceeded ({received} bytes read)"
                )
            return message

        return inner

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        wrapper = self.receive_wrapper(receive)
        await self.app(scope, wrapper, send)
