#!/usr/bin/env python3
import os
import tempfile
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from git import Repo
from urllib.parse import urlparse

from pyjuxa.db import Testcase, Testsuite, connect, Config, Project


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


def _make_case(session, suite, case_xml):
    tc = Testcase()
    tc.suite_id = suite.id
    tc.name = case_xml.get('name')
    tc.time = case_xml.get('time')
    tc.classname = case_xml.get('classname')
    tc.filename = case_xml.get('filename', '')
    tc.line = case_xml.get('line', '')
    session.add(tc)
    session.commit()


def from_file(session, config, path):
    try:
        # sanitize
        soup = BeautifulSoup(open(path).read(), 'xml')
        root = ET.fromstring(str(soup))
    except ET.ParseError as e:
        raise ParseError(path, e)
    suite_xml = root.findall('.//testsuite')[0]
    suite = Testsuite()
    suite.name = suite_xml.get('name')
    suite.time = float(suite_xml.get('time'))
    suite.errors = int(suite_xml.get('errors'))
    suite.tests = int(suite_xml.get('tests'))
    suite.skips = int(suite_xml.get('disabled', suite_xml.get('skips')))
    suite.errors = int(suite_xml.get('errors')) + int(suite_xml.get('failures', 0))
    suite.project_id = config.project_id
    cases_xml = root.findall('.//testcase')
    for case in cases_xml:
        _make_case(session, suite, case)
    session.add(suite)
    session.commit()


def process_dir(session, project, path, commit):
    name = os.path.dirname(path)
    #print('DIR {} at {}'.format(name, commit))
    test_config = session.query(Config).filter_by(name=name, project_id=project.id).first() or Config(name=name, project_id=project.id)
    for entry in os.listdir(path):
        filepath = os.path.join(path, entry)
        if os.path.isfile(filepath) and entry.endswith('xml'):
            from_file(session, test_config, filepath)
    session.add(test_config)
    session.commit()


def process_repo(session, repo_url, branch='master'):
    project_name = urlparse(repo_url)[2].replace('.git', '').replace('/', '_')
    project = session.query(Project).filter_by(name=project_name).first() or Project(name=project_name)
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_dir = os.path.join(tmp_dir, 'repo')
        repo = Repo.clone_from(repo_url, repo_dir, branch=branch)
        for commit in repo.iter_commits():
            for entry in os.listdir(repo_dir):
                subdir = os.path.join(repo_dir, entry)
                if not os.path.isdir(subdir):
                    continue
                repo.head.reference = commit
                repo.head.reset(index=True, working_tree=True)
                process_dir(session, project, subdir, commit)


if __name__ == '__main__':
    datadir = os.path.join(os.path.dirname(__file__), '..', 'pyjuxatests', 'data')
    # from_file(os.path.join(datadir, 'pymor', '01.xml'))
    # from_file(os.path.join(datadir, 'dune-xt', 'test_tuple.xml'))
    session = connect('dune-xt-common.db')()
    process_repo(session, 'https://github.com/dune-community/dune-xt-common-testlogs')
