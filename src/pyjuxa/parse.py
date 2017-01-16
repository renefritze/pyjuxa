#!/usr/bin/env python3
import os
import tempfile
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from git import Repo
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


def from_file(path, session=None):
    try:
        # sanitize
        soup = BeautifulSoup(open(path).read(), 'xml')
        root = ET.fromstring(str(soup))
    except ET.ParseError as e:
        raise ParseError(path, e)
    cases_xml = root.findall('.//testcase')

    session = session or connect()()
    for case in cases_xml:
        _make_case(case, session=session)


def process_dir(path, commit, session):
    name = os.path.dirname(path)
    #print('DIR {} at {}'.format(name, commit))
    for entry in os.listdir(path):
        filepath = os.path.join(path, entry)
        if os.path.isfile(filepath):
            from_file(filepath)

def process_repo(repo_url, branch='master'):
    session = connect()()
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_dir = os.path.join(tmp_dir, 'repo')
        repo = Repo.clone_from(repo_url, repo_dir, branch=branch)
        for commit in repo.iter_commits():
            for entry in os.listdir(repo_dir):
                subdir = os.path.join(repo_dir, entry)
                if not os.path.isdir(subdir):
                    continue
                process_dir(subdir, commit, session)



if __name__ == '__main__':
    datadir = os.path.join(os.path.dirname(__file__), '..', 'pyjuxatests', 'data')
    # from_file(os.path.join(datadir, 'pymor', '01.xml'))
    # from_file(os.path.join(datadir, 'dune-xt', 'test_tuple.xml'))
    process_repo('https://github.com/dune-community/dune-xt-common-testlogs')
