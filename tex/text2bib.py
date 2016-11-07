import sys
import re

ARTICLE_P_ENTRY = """
@article{{article{number},
  author  = {{{data[authors]}}},
  title   = {{{data[title]}}},
  journal = {{{data[journal]}}},
  year    = {data[year]},
  issue  = {data[issue]},
  pages   = {{{data[pages]}}}
}}
"""

ARTICLE_ENTRY = """
@article{{article{number},
  author  = {{{data[authors]}}},
  title   = {{{data[title]}}},
  journal = {{{data[journal]}}},
  year    = {data[year]},
  issue  = {data[issue]}
}}
"""

BOOK_ENTRY = """
@book{{book{number},
  author    = {{{data[authors]}}},
  title     = {{{data[title]}}},
  publisher = {{{data[publisher]}}},
  year      = {data[year]},
  address   = {{{data[city]}}}
}}
"""

THESIS_ENTRY = """
@phdthesis{{phdthesis{number},
  author       = {{{data[authors]}}},
  title        = {{{data[title]}}},
  year         = {data[year]},
  address      = {{{data[city]}}}
}}
"""

INBOOK_ENTRY = """
@incollection{{incollection{number},
  author       = {{{data[authors]}}},
  title        = {{{data[title]}}},
  booktitle    = {{{data[booktitle]}}},
  publisher    = {{{data[publisher]}}},
  year         = {data[year]},
  address      = {{{data[city]}}}
}}
"""

INBOOK_P_ENTRY = """
@incollection{{incollection{number},
  author       = {{{data[authors]}}},
  title        = {{{data[title]}}},
  booktitle    = {{{data[booktitle]}}},
  pages        = {{{data[pages]}}},
  publisher    = {{{data[publisher]}}},
  year         = {data[year]},
  address      = {{{data[city]}}}
}}
"""


def _parse_article(i, text):
    authors = ''
    pa = re.compile('[А-Я]\S+\s+([А-Я]\.){1,2}')
    for ma in pa.finditer(text, endpos=text.find('//')):
        if authors:
            authors += ' and '
        authors += ma.group()

    if 'С.' in text:
        p = re.compile('(\S+\s+([А-Я]\.){1,2},?\s)+\s*(?P<title>[^/]+)//'
                       + '\s*(?P<journal>.+)(?=\d{4})\s*(?P<year>\d+)\.\s*(Т\.)?\s*(?P<volume>[\d\-]+)?\.?'
                       + '\s*№\s*(?P<issue>[\d\-]+)\.[^С]*С\.\s*(?P<pages>[0-9\-]+)')
        m = p.match(text)
        if m:
            data = {k: v.strip() for k, v in m.groupdict().items() if v is not None}
            data['authors'] = authors
            return ARTICLE_P_ENTRY.format(number=i, data=data)
        else:
            print('Error paged article {0}: '.format(i) + text)
    else:
        p = re.compile('(\S+\s+([А-Я]\.){1,2},?\s)+\s*(?P<title>[^/]+)//'
                       + '\s*(?P<journal>.+)(?=\d{4})\s*(?P<year>\d+)\.\s*(T\.)?\s*(?P<volume>[\d\-]+)?\.?'
                       + '\s*№\s*(?P<issue>[\d\-]+)')
        m = p.match(text)
        if m:
            data = {k: v.strip() for k, v in m.groupdict().items() if v is not None}
            data['authors'] = authors
            return ARTICLE_ENTRY.format(number=i, data=data)
        else:
            print('Error article {0}: '.format(i) + text)


def _parse_diss(i, text):
    if 'наук' in text:
        p = re.compile('(?P<authors>\S+\s+([А-Я]\.){1,2})+\s*(?P<title>.+)(?=Дисс).+'
                       + '(?<=наук\.)\s*(?P<city>[^,]+),\s*(?P<year>\d+)')
        m = p.match(text)
        if m:
            data = {k: v.strip() for k, v in m.groupdict().items()}
            return THESIS_ENTRY.format(number=i, data=data)
        else:
            print('Error diss {0}: '.format(i) + text)
    else:
        p = re.compile('(?P<authors>\S+\s+([А-Я]\.){1,2})+\s*(?P<title>.+)(?=Дисс).+'
                       + '(?<=логии\.)\s*(?P<city>[^,]+),\s*(?P<year>\d+)')
        m = p.match(text)
        if m:
            data = {k: v.strip() for k, v in m.groupdict().items()}
            return THESIS_ENTRY.format(number=i, data=data)
        else:
            print('Error diss {0}: '.format(i) + text)

def _parse_chapter(i, text):
    authors = ''
    pa = re.compile('[А-Я]\S+\s+([А-Я]\.){1,2}')
    for ma in pa.finditer(text, endpos=text.find('//')):
        if authors:
            authors += ' and '
        authors += ma.group()

    if 'С.' in text:
        p = re.compile('(\S+\s+([А-Я]\.){1,2},?\s)+\s*(?P<title>[^/]+)//'
                       + '(?P<booktitle>.+)(?= \S+:)(?P<city>[^:]+):\s*(?P<publisher>[^,]+),\s*(?P<year>\d+)\.'
                       + '\s*С\.\s*(?P<pages>[0-9\-]+)')
        m = p.match(text)
        if m:
            data = {k: v.strip() for k, v in m.groupdict().items()}
            data['authors'] = authors
            return INBOOK_P_ENTRY.format(number=i, data=data)
        else:
            print('Error paged chapter {0}: '.format(i) + text)

    else:
        p = re.compile('(\S+\s+([А-Я]\.){1,2},?\s)+\s*(?P<title>[^/]+)//'
                       + '(?P<booktitle>.+)(?= \S+:)(?P<city>[^:]+):\s*(?P<publisher>[^,]+),\s*(?P<year>\d+)')
        m = p.match(text)
        if m:
            data = {k: v.strip() for k, v in m.groupdict().items()}
            data['authors'] = authors
            return INBOOK_ENTRY.format(number=i, data=data)
        else:
            print('Error chapter {0}: '.format(i) + text)


def _parse_book(i, text):
    authors = ''
    pa = re.compile('[А-Я][а-яА-Я\-]+,?\s+([А-Я]\.){1,2}')
    for ma in pa.finditer(text):
        if authors:
            authors += ' and '
        authors += ma.group()

    p = re.compile('(\S+\s+([А-Я]\.){1,2},?\s)+\s*(?P<title>[^\.]+)\.'
                   + '\s*(?P<city>[^:]+):\s*(?P<publisher>[^,]+),\s*(?P<year>\d+)')
    m = p.match(text)
    if m:
        data = {k: v.strip() for k, v in m.groupdict().items()}
        data['authors'] = authors
        return BOOK_ENTRY.format(number=i, data=data)
    else:
        print('Error book {0}: '.format(i) + text)


def text2bib(i, text):
    m = re.compile('\d+\.').match(text)
    if m and text.startswith(m.group()):
        text = text[len(m.group()):].strip()

    text = text.replace('«', '<<')
    text = text.replace('»', '>>')
    text = text.replace('и др.', '')
    text = text.replace('Отв. ред.', '')
    text = text.replace('А/р.', '')
    text = text.replace('дисс', 'Дисс')
    text = text.replace('Вып.', '')
    if '№' in text:
        return _parse_article(i, text)
    elif 'Дисс' in text or 'дисс' in text:
        return _parse_diss(i, text)
    elif '//' in text:
        return _parse_chapter(i, text)
    elif ':' in text:
        return _parse_book(i, text)
    else:
        print('Bad bib entry')
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1]:
        bibs = []

        f = open(sys.argv[1], encoding='cp1251')
        for i, line in enumerate(f):
            bib = text2bib(i, line)
            if bib:
                bibs.append(bib)
        for bib in bibs:
            print(bib)
