#!/usr/bin/env python

import yaml
import os
import sys
import urllib
import re
import datetime

DATE_MIN = '2014-09-18'
DATE_MAX = '2015-09-18'

BASE_URL = 'https://git.openstack.org/cgit'
PROJECTS_URL = ('%s/openstack/governance/plain/reference/projects.yaml' %
                (BASE_URL))

date_min = datetime.datetime.strptime(DATE_MIN, '%Y-%m-%d').strftime('%s')
date_max = datetime.datetime.strptime(DATE_MAX, '%Y-%m-%d').strftime('%s')


def check_date(date):
    epoch = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%s')
    if epoch > date_min and epoch < date_max:
        return True
    return False

try:
    project_name = os.path.basename(os.path.dirname(sys.argv[1]))
    author = os.path.basename(sys.argv[1])[:-4].replace(' ', '+')
except:
    print "usage: %s candidacy_file" % sys.argv[0]
    exit(1)

if not os.path.isfile('.projects.yaml'):
    open('.projects.yaml', 'w').write(
        urllib.urlopen(PROJECTS_URL).read()
    )
projects = yaml.load(open('.projects.yaml'))

if project_name == "TC":
    project_list = projects.values()
else:
    try:
        project_list = [projects[project_name]]
    except:
        print "Can't find project [%s] in %s" % (project_name, projects.keys())
        exit(1)

for project in project_list:
    for deliverable in project['deliverables'].values():
        for repo_name in deliverable["repos"]:
            url = '%s/%s/log/?qt=author&q=%s' % (BASE_URL, repo_name, author)
            print "Querying: %s" % url
            found = False
            for l in urllib.urlopen(url).read().split('\n'):
                if "commit/?id=" not in l:
                    continue
                try:
                    url = ('http://git.openstack.org/%s' %
                           re.search("href='([^']*)'", l).groups()[0])
                    date = re.search('<td>([^<]*)</td>', l).groups()[0]
                    if not check_date(date):
                        continue
                except:
                    continue
                print "[%s]: %s" % (date, url)
                found = True
            if found:
                exit(0)
exit(1)
