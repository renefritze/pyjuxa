import pytest
from pkg_resources import resource_stream, resource_filename

from pyjuxa.parse import from_file


data_files = ['data/dune-xt/test_timings.xml', 'data/pymor/01.xml']


@pytest.fixture(params=data_files)
def xml_contents(request):
    with resource_stream('pyjuxatests', request.param) as f:
        return f.read()


@pytest.fixture(params=data_files)
def xml_paths(request):
    return resource_filename('pyjuxatests', request.param)


def test_parse_success(xml_paths):
    from_file(xml_paths)
