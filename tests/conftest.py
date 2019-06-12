import asynctest
import pytest

from starlette.applications import Starlette


@pytest.fixture(scope='function')
def app():
    return Starlette()


@pytest.fixture
def send():
    return asynctest.CoroutineMock()


@pytest.fixture
def scope():
    def inner(type=None, method=None, scheme=None, server=None, path=None, headers=None):
        if type is None:
            type = "http"
        if method is None:
            method = "GET"
        if scheme is None:
            scheme = "https"
        if server is None:
            server = ("www.example.mock", 80)
        if path is None:
            path = "/"
        if headers is None:
            headers = []

        return {"type": type, "method": method, "scheme": scheme, "server": server, "path": path, "headers": headers}
    return inner
