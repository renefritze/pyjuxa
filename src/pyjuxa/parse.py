import os
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

from pyjuxa.db import Testcase, Testsuite, connect

class ParseError(Exception):

    def __init__(self, filename, error):
        assert os.path.isfile(filename)
        self.filename = filename
        self.error = error

    def __str__(self):
        return 'XML Parse Error for file {}:\n{}'.format(self.filename, self.error)

'''
<testsuite name="ProfilerTest" tests="6" failures="0" disabled="0" errors="0" time="4.185">
<testsuite errors="0" failures="0" name="pytest" skips="0" tests="643" time="34.035">
'''


def _make_case(case_xml, session):
    tc = Testcase()
    tc.name = case_xml.get('name')
    tc.time = case_xml.get('time')
    tc.classname = case_xml.get('classname')
    tc.filename = case_xml.get('filename', '')
    tc.line = case_xml.get('line', '')
    session.add(tc)
    session.commit()


def from_file(path):
    try:
        # sanitize
        soup = BeautifulSoup(open(path).read(), 'xml')
        root = ET.fromstring(str(soup))
    except ET.ParseError as e:
        raise ParseError(path, e)
    cases_xml = root.findall('.//testcase')

    Session = connect()
    for case in cases_xml:
        _make_case(case, session=Session())



if __name__ == '__main__':
    datadir = os.path.join(os.path.dirname(__file__), '..', 'pyjuxatests', 'data')
    from_file(os.path.join(datadir, 'pymor', '01.xml'))
    from_file(os.path.join(datadir, 'dune-xt', 'test_tuple.xml'))
