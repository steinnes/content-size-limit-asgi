# content size limit

[![CircleCI](https://circleci.com/gh/steinnes/content-size-limit-asgi.svg?style=svg)](https://circleci.com/gh/steinnes/content-size-limit-asgi)

This is a middleware for ASGI which intercepts the receive() method to raise
an exception when the read bytes exceed the given limit.

## Example

```python
import uvicorn

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse

from content_size_limit_asgi import ContentSizeLimitMiddleware


app = Starlette()

@app.route("/", methods=["POST"])
async def index(request):
    body = await request.body()
    return PlainTextResponse(f"body: {body.decode('utf-8')}")


app.add_middleware(ContentSizeLimitMiddleware, max_content_size=512)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=6001, log_level='debug')
```

To test the app:

```
$ curl --limit-rate 5k -q -v http://localhost:6001/ -d `printf 'A%.0s' {1..99999}`
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 6001 (#0)
> POST / HTTP/1.1
> Host: localhost:6001
> User-Agent: curl/7.54.0
> Accept: */*
> Content-Length: 99999
> Content-Type: application/x-www-form-urlencoded
> Expect: 100-continue
>
< HTTP/1.1 100 Continue
< HTTP/1.1 500 Internal Server Error
< date: Wed, 12 Jun 2019 14:41:28 GMT
< server: uvicorn
< content-length: 21
< content-type: text/plain; charset=utf-8
* HTTP error before end of send, stop sending
<
* Closing connection 0
Internal Server Error
```

The app console log should read:
```
$ PYTHONPATH=. python tapp.py
INFO: Started server process [48160]
INFO: Waiting for application startup.
DEBUG: None - ASGI [1] Started
WARNING 2019-06-12 14:42:18,003 content_size_limit.middleware: ASGI scope of type lifespan is not supported yet
WARNING: ASGI scope of type lifespan is not supported yet
DEBUG: None - ASGI [1] Sent {'type': 'lifespan.startup'}
DEBUG: None - ASGI [1] Received {'type': 'lifespan.startup.complete'}
INFO: Uvicorn running on http://127.0.0.1:6001 (Press CTRL+C to quit)
DEBUG: ('127.0.0.1', 52103) - Connected
DEBUG: ('127.0.0.1', 52103) - ASGI [2] Started
DEBUG: ('127.0.0.1', 52103) - ASGI [2] Sent {'type': 'http.request', 'body': '<16384 bytes>', 'more_body': True}
DEBUG: ('127.0.0.1', 52103) - ASGI [2] Received {'type': 'http.response.start', 'status': 500, 'headers': '<...>'}
INFO: ('127.0.0.1', 52103) - "POST / HTTP/1.1" 500
DEBUG: ('127.0.0.1', 52103) - ASGI [2] Received {'type': 'http.response.body', 'body': '<21 bytes>'}
DEBUG: ('127.0.0.1', 52103) - ASGI [2] Raised exception
ERROR: Exception in ASGI application
Traceback (most recent call last):
  File "/Users/ses/.pyenv/versions/3.7.3/lib/python3.7/site-packages/uvicorn/protocols/http/httptools_impl.py", line 368, in run_asgi
    result = await app(self.scope, self.receive, self.send)
  File "/Users/ses/.pyenv/versions/3.7.3/lib/python3.7/site-packages/uvicorn/middleware/message_logger.py", line 58, in __call__
    raise exc from None
  File "/Users/ses/.pyenv/versions/3.7.3/lib/python3.7/site-packages/uvicorn/middleware/message_logger.py", line 54, in __call__
    await self.app(scope, inner_receive, inner_send)
  File "/Users/ses/.pyenv/versions/3.7.3/lib/python3.7/site-packages/starlette/applications.py", line 133, in __call__
    await self.error_middleware(scope, receive, send)
  File "/Users/ses/.pyenv/versions/3.7.3/lib/python3.7/site-packages/starlette/middleware/errors.py", line 122, in __call__
    raise exc from None
  File "/Users/ses/.pyenv/versions/3.7.3/lib/python3.7/site-packages/starlette/middleware/errors.py", line 100, in __call__
    await self.app(scope, receive, _send)
  File "/Users/ses/w/content-size-limit-asgi/content_size_limit/middleware.py", line 48, in __call__
    await self.app(scope, wrapper, send)
  File "/Users/ses/.pyenv/versions/3.7.3/lib/python3.7/site-packages/starlette/exceptions.py", line 73, in __call__
    raise exc from None
  File "/Users/ses/.pyenv/versions/3.7.3/lib/python3.7/site-packages/starlette/exceptions.py", line 62, in __call__
    await self.app(scope, receive, sender)
  File "/Users/ses/.pyenv/versions/3.7.3/lib/python3.7/site-packages/starlette/routing.py", line 585, in __call__
    await route(scope, receive, send)
  File "/Users/ses/.pyenv/versions/3.7.3/lib/python3.7/site-packages/starlette/routing.py", line 207, in __call__
    await self.app(scope, receive, send)
  File "/Users/ses/.pyenv/versions/3.7.3/lib/python3.7/site-packages/starlette/routing.py", line 40, in app
    response = await func(request)
  File "tapp.py", line 13, in index
    body = await request.body()
  File "/Users/ses/.pyenv/versions/3.7.3/lib/python3.7/site-packages/starlette/requests.py", line 167, in body
    async for chunk in self.stream():
  File "/Users/ses/.pyenv/versions/3.7.3/lib/python3.7/site-packages/starlette/requests.py", line 152, in stream
    message = await self._receive()
  File "/Users/ses/w/content-size-limit-asgi/content_size_limit/middleware.py", line 36, in inner
    f"Maximum content size limit ({self.max_content_size}) exceeded ({received} bytes read)"
content_size_limit.errors.ContentSizeExceeded: Maximum content size limit (512) exceeded (16384 bytes read)
DEBUG: ('127.0.0.1', 52103) - Disconnected
```

## Why not just raise in the route / view functon itself?

Depending on the ASGI server/framework used, you might not have access to
the raw stream to stop reading immediately once the maximum content size
has been exceeded.

Take this Starlette view for example:


```python

@app.route("/documents/upload", methods=["POST"])
def upload_document(request):
    data = await request.body()
    if len(data) > Config.MAX_FILE_SIZE:
        return api_400(
            f"This file exceeds the maximum file size we support at this time ({Config.MAX_FILE_SIZE})",
            code=MAX_FILE_SIZE_EXCEEDED,
        )
    ...
```

If the maximum file size is 5MB, and the uploaded file was 50MB, then this
implementation reads the entire 50MB into memory before rejecting the
request.
