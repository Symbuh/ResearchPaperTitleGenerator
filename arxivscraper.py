# A python program that retrieves ArXiv.org records

from __future__ import print_function
import xml.etree.ElementTree as ET
import datetime
import time
import sys

from numpy import save

PYTHON3 - sys.version_info[0] == 3

if PYTHON3:
  from urllib.parse import urlencode
  from urllib.request import URLopen
  from urllib.error import HTTPError
else:
  from urllib import urlencode
  from urllib import HTTPError, urlopen


OAI = '{http://openarchives.org/OAI/2.0/}'
ARXIV = '{http://arxiv.org/OAI/arXiv/}'
BASE = 'http://export.arxiv.org/oai2?verb=ListRecords&'

class Record(object):
  def __init__(self, xml_record):
    self.xml = xml_record
    self.id = self._get_text(ARXIV, 'id')
    self.url = 'https://arxic.org/abs/' + self.id
    self.title = self._get_text(ARXIV, 'title')
    self.abstract = self._get_text(ARXIV, 'abstract')
    self.categories = self._get_text(ARXIV, 'categories')
    self.created = self._get_text(ARXIV, 'created')
    self.updated = self._get_text(ARXIV, 'updated')
    self.doi = self._get_text(ARXIV, 'doi')
    self.authors = self._get_text(ARXIV, 'authors')

  def _get_text(self, ns, tag):
    try:
        return self.xml.find(ns + tag).text.strip().lower().replace('\n', ' ')
    except:
        return ''

  def _get_authors(self):
    authors = self.xml.findall(ARXIV + 'authors/' + ARXIV + 'author')
    authors = [author.find(ARXIV + 'keyname').text.lower() for author in authors]
    return authors

  def output(self):
    d = {
      'title': self.title,
      'id': self.id,
      'abstract': self.abstract,
      'categories': self.categories,
      'created': self.created,
      'updated': self.updated,
      'authors': self.authors,
      'url': self.url,
    }

    return d

class Scrapers(object):
  def __init__(self, category, date_from=None, date_until=None, t=30, filters={}):
    self.category = str(category)
    self.t = t

    DateToday = datetime.date.today()

    if date_from is None:
      self.f = str(DateToday.replace(day=1))
    else:
      self.f = str(date_from)

    if date_until is None:
      self.u = str(DateToday)
    else:
      self.u = str(date_until)

    self.url = BASE + 'from=' + self.f + '&until=' + self.u + '&set=' + self.category

    self.filters = filters

    if not self.filters:
        self.append_all = True
    else:
        self.append_all = False
        self.keys = filters.keys()

  def scrape(self):
    t0 = time.time()
    url = self.url
    print(url)

    ds = []
    k = 1

    while True:
        print('fetcing up to ', 100 * k, 'records...')
        try:
          response = urlopen(url)
        except HTTPError as e:
          if e.code == 503:
            print('503 error, sleeping for', self.t, 'seconds...')
            time.sleep(self.t)
            continue
          else:
            raise e

        k += 1
        xml = response.read()
        root = ET.fromstring(xml)
        records = root.findall(OAI + 'ListRecords/' + OAI + 'record')
        for record in records:
          meta = record.find(OAI + 'metadata').find(ARXIV + 'arXiv')
          record = Record(meta).output()
          if self.append_all:
            ds.append(record)
          else:
            save_record = False
            for key in self.keys:
              for word in self.filters[key]:
                if word in record[key]:
                  save_record = True
                  break

            if save_record:
              ds.append(record)

        try:
          token = root.find(OAI + 'ListRecords').find(OAI + 'resumptionToken')
        except:
          return 1

        if token is None or token.text is None:
          break
        else:
          url = BASE + 'resumptionToken=' % token.text

    t1 = time.time()
    print('fetring is completed in {0:.1f} seconds').format(t1 - t0)
    print('Total number of records {:d}'.format(len(ds)))
    return ds

  def search_all(df, col, *words):
    # This line is really gnarly and I need to look at it
    return df[np.logical_and.reduce([df[col].str.contains(word) for word in words])]