import pytest
import io


@pytest.mark.xfail(reason='todo')
def test_chunks():
    single = io.BytesIO()
    chunked = io.BytesIO()

    assert single == chunked
