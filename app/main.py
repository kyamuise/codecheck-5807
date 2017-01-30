#!/usr/bin/env python3

import sys
import datetime
import pandas
import json
import urllib.request
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
from collections import OrderedDict

def main(argv):
    for v in argv:
        print(v)

    for line in sys.stdin:
        line = line.rstrip()

        (startDateStr, endDateStr) = line.split("]")[1].split()
        keywords = [str.strip().strip('"') for str in line.split("]")[0][1:].split(",")]

        startDatetime = datetime.datetime.strptime(startDateStr, '%Y-%m-%d')
        endDatetime = datetime.datetime.strptime(endDateStr, '%Y-%m-%d')

        calcCoeff(reqAPI(keywords, startDatetime, endDatetime))

def calcCoeff(data):
    dataFrame = pandas.DataFrame(data)
    corrMatrix = dataFrame.corr().round(3).as_matrix().tolist()

    print(json.dumps({'coefficients': corrMatrix, 'posChecker':False}))

def urlEncode(url):
    p = urlparse(url)
    query = urllib.parse.quote_plus(p.query, safe='=&')
    url = '{}://{}{}{}{}{}{}{}{}'.format(
        p.scheme, p.netloc, p.path,
        ';' if p.params else '', p.params,
        '?' if p.query else '', query,
        '#' if p.fragment else '', p.fragment)

    return url


def reqAPI(keywords, startDatetime, endDatetime):

    numFounds = OrderedDict()

    baseurl = 'http://54.92.123.84/search?ackey=869388c0968ae503614699f99e09d960f9ad3e12&sort=ReleaseDate asc&rows=1'

    for keyword in keywords:
        numFounds[keyword] = []
        query = ''

        tmpStartDatetime = startDatetime
        tmpEndDatetime = startDatetime + datetime.timedelta(days=7)

        while tmpEndDatetime < endDatetime:
            query = 'q=Body:' + keyword + ' AND ' + 'ReleaseDate:[' + tmpStartDatetime.strftime("%Y-%m-%d") + ' TO ' + tmpEndDatetime.strftime("%Y-%m-%d") + ']'

            url = baseurl + '&' + query

            tmpStartDatetime = tmpEndDatetime + datetime.timedelta(days=1)
            tmpEndDatetime = tmpStartDatetime + datetime.timedelta(days=7)

            req = urllib.request.Request(urlEncode(url))

            with urllib.request.urlopen(req) as response:
                XmlData = response.read()

            root = ET.fromstring(XmlData)

            numFounds[keyword].append(int(root[2].attrib['numFound']))

    return numFounds
main([])
