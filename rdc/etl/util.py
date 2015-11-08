# -*- coding: utf-8 -*-
#
# Copyright 2012-2014 Romain Dorgueil
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import cgi
import time
import re
import requests
import types
import unidecode
from blessings import Terminal as _Terminal
from cached_property import cached_property
from datetime import datetime
from lxml import etree
from six.moves import html_parser

VALID_HTML_TAGS = ['br']

# default unicode character mapping (you may not see some chars, leave as is )
char_map = {'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'Ae', 'Å': 'A', 'Æ': 'A', 'Ā': 'A', 'Ą': 'A',
            'Ă': 'A', 'Ç': 'C', 'Ć': 'C', 'Č': 'C', 'Ĉ': 'C', 'Ċ': 'C', 'Ď': 'D', 'Đ': 'D', 'È': 'E',
            'É': 'E', 'Ê': 'E', 'Ë': 'E', 'Ē': 'E', 'Ę': 'E', 'Ě': 'E', 'Ĕ': 'E', 'Ė': 'E', 'Ĝ': 'G',
            'Ğ': 'G', 'Ġ': 'G', 'Ģ': 'G', 'Ĥ': 'H', 'Ħ': 'H', 'Ì': 'I', 'Í': 'I', 'Î': 'I', 'Ï': 'I',
            'Ī': 'I', 'Ĩ': 'I', 'Ĭ': 'I', 'Į': 'I', 'İ': 'I', 'Ĳ': 'IJ', 'Ĵ': 'J', 'Ķ': 'K', 'Ľ': 'K',
            'Ĺ': 'K', 'Ļ': 'K', 'Ŀ': 'K', 'Ł': 'L', 'Ñ': 'N', 'Ń': 'N', 'Ň': 'N', 'Ņ': 'N', 'Ŋ': 'N',
            'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'Oe', 'Ø': 'O', 'Ō': 'O', 'Ő': 'O', 'Ŏ': 'O',
            'Œ': 'OE', 'Ŕ': 'R', 'Ř': 'R', 'Ŗ': 'R', 'Ś': 'S', 'Ş': 'S', 'Ŝ': 'S', 'Ș': 'S', 'Š': 'S',
            'Ť': 'T', 'Ţ': 'T', 'Ŧ': 'T', 'Ț': 'T', 'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'Ue', 'Ū': 'U',
            'Ů': 'U', 'Ű': 'U', 'Ŭ': 'U', 'Ũ': 'U', 'Ų': 'U', 'Ŵ': 'W', 'Ŷ': 'Y', 'Ÿ': 'Y', 'Ý': 'Y',
            'Ź': 'Z', 'Ż': 'Z', 'Ž': 'Z', 'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'ae', 'ā': 'a',
            'ą': 'a', 'ă': 'a', 'å': 'a', 'æ': 'ae', 'ç': 'c', 'ć': 'c', 'č': 'c', 'ĉ': 'c', 'ċ': 'c',
            'ď': 'd', 'đ': 'd', 'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e', 'ē': 'e', 'ę': 'e', 'ě': 'e',
            'ĕ': 'e', 'ė': 'e', 'ƒ': 'f', 'ĝ': 'g', 'ğ': 'g', 'ġ': 'g', 'ģ': 'g', 'ĥ': 'h', 'ħ': 'h',
            'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i', 'ī': 'i', 'ĩ': 'i', 'ĭ': 'i', 'į': 'i', 'ı': 'i',
            'ĳ': 'ij', 'ĵ': 'j', 'ķ': 'k', 'ĸ': 'k', 'ł': 'l', 'ľ': 'l', 'ĺ': 'l', 'ļ': 'l', 'ŀ': 'l',
            'ñ': 'n', 'ń': 'n', 'ň': 'n', 'ņ': 'n', 'ŉ': 'n', 'ŋ': 'n', 'ò': 'o', 'ó': 'o', 'ô': 'o',
            'õ': 'o', 'ö': 'oe', 'ø': 'o', 'ō': 'o', 'ő': 'o', 'ŏ': 'o', 'œ': 'oe', 'ŕ': 'r', 'ř': 'r',
            'ŗ': 'r', 'ś': 's', 'š': 's', 'ť': 't', 'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'ue', 'ū': 'u',
            'ů': 'u', 'ű': 'u', 'ŭ': 'u', 'ũ': 'u', 'ų': 'u', 'ŵ': 'w', 'ÿ': 'y', 'ý': 'y', 'ŷ': 'y',
            'ż': 'z', 'ź': 'z', 'ž': 'z', 'ß': 'ss', 'ſ': 'ss', 'Α': 'A', 'Ά': 'A', 'Ἀ': 'A', 'Ἁ': 'A',
            'Ἂ': 'A', 'Ἃ': 'A', 'Ἄ': 'A', 'Ἅ': 'A', 'Ἆ': 'A', 'Ἇ': 'A', 'ᾈ': 'A', 'ᾉ': 'A', 'ᾊ': 'A',
            'ᾋ': 'A', 'ᾌ': 'A', 'ᾍ': 'A', 'ᾎ': 'A', 'ᾏ': 'A', 'Ᾰ': 'A', 'Ᾱ': 'A', 'Ὰ': 'A', 'Ά': 'A',
            'ᾼ': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E', 'Έ': 'E', 'Ἐ': 'E', 'Ἑ': 'E', 'Ἒ': 'E',
            'Ἓ': 'E', 'Ἔ': 'E', 'Ἕ': 'E', 'Έ': 'E', 'Ὲ': 'E', 'Ζ': 'Z', 'Η': 'I', 'Ή': 'I', 'Ἠ': 'I',
            'Ἡ': 'I', 'Ἢ': 'I', 'Ἣ': 'I', 'Ἤ': 'I', 'Ἥ': 'I', 'Ἦ': 'I', 'Ἧ': 'I', 'ᾘ': 'I', 'ᾙ': 'I',
            'ᾚ': 'I', 'ᾛ': 'I', 'ᾜ': 'I', 'ᾝ': 'I', 'ᾞ': 'I', 'ᾟ': 'I', 'Ὴ': 'I', 'Ή': 'I', 'ῌ': 'I',
            'Θ': 'TH', 'Ι': 'I', 'Ί': 'I', 'Ϊ': 'I', 'Ἰ': 'I', 'Ἱ': 'I', 'Ἲ': 'I', 'Ἳ': 'I', 'Ἴ': 'I',
            'Ἵ': 'I', 'Ἶ': 'I', 'Ἷ': 'I', 'Ῐ': 'I', 'Ῑ': 'I', 'Ὶ': 'I', 'Ί': 'I', 'Κ': 'K', 'Λ': 'L',
            'Μ': 'M', 'Ν': 'N', 'Ξ': 'KS', 'Ο': 'O', 'Ό': 'O', 'Ὀ': 'O', 'Ὁ': 'O', 'Ὂ': 'O', 'Ὃ': 'O',
            'Ὄ': 'O', 'Ὅ': 'O', 'Ὸ': 'O', 'Ό': 'O', 'Π': 'P', 'Ρ': 'R', 'Ῥ': 'R', 'Σ': 'S', 'Τ': 'T',
            'Υ': 'Y', 'Ύ': 'Y', 'Ϋ': 'Y', 'Ὑ': 'Y', 'Ὓ': 'Y', 'Ὕ': 'Y', 'Ὗ': 'Y', 'Ῠ': 'Y', 'Ῡ': 'Y',
            'Ὺ': 'Y', 'Ύ': 'Y', 'Φ': 'F', 'Χ': 'X', 'Ψ': 'PS', 'Ω': 'O', 'Ώ': 'O', 'Ὠ': 'O', 'Ὡ': 'O',
            'Ὢ': 'O', 'Ὣ': 'O', 'Ὤ': 'O', 'Ὥ': 'O', 'Ὦ': 'O', 'Ὧ': 'O', 'ᾨ': 'O', 'ᾩ': 'O', 'ᾪ': 'O',
            'ᾫ': 'O', 'ᾬ': 'O', 'ᾭ': 'O', 'ᾮ': 'O', 'ᾯ': 'O', 'Ὼ': 'O', 'Ώ': 'O', 'ῼ': 'O', 'α': 'a',
            'ά': 'a', 'ἀ': 'a', 'ἁ': 'a', 'ἂ': 'a', 'ἃ': 'a', 'ἄ': 'a', 'ἅ': 'a', 'ἆ': 'a', 'ἇ': 'a',
            'ᾀ': 'a', 'ᾁ': 'a', 'ᾂ': 'a', 'ᾃ': 'a', 'ᾄ': 'a', 'ᾅ': 'a', 'ᾆ': 'a', 'ᾇ': 'a', 'ὰ': 'a',
            'ά': 'a', 'ᾰ': 'a', 'ᾱ': 'a', 'ᾲ': 'a', 'ᾳ': 'a', 'ᾴ': 'a', 'ᾶ': 'a', 'ᾷ': 'a', 'β': 'b',
            'γ': 'g', 'δ': 'd', 'ε': 'e', 'έ': 'e', 'ἐ': 'e', 'ἑ': 'e', 'ἒ': 'e', 'ἓ': 'e', 'ἔ': 'e',
            'ἕ': 'e', 'ὲ': 'e', 'έ': 'e', 'ζ': 'z', 'η': 'i', 'ή': 'i', 'ἠ': 'i', 'ἡ': 'i', 'ἢ': 'i',
            'ἣ': 'i', 'ἤ': 'i', 'ἥ': 'i', 'ἦ': 'i', 'ἧ': 'i', 'ᾐ': 'i', 'ᾑ': 'i', 'ᾒ': 'i', 'ᾓ': 'i',
            'ᾔ': 'i', 'ᾕ': 'i', 'ᾖ': 'i', 'ᾗ': 'i', 'ὴ': 'i', 'ή': 'i', 'ῂ': 'i', 'ῃ': 'i', 'ῄ': 'i',
            'ῆ': 'i', 'ῇ': 'i', 'θ': 'th', 'ι': 'i', 'ί': 'i', 'ϊ': 'i', 'ΐ': 'i', 'ἰ': 'i', 'ἱ': 'i',
            'ἲ': 'i', 'ἳ': 'i', 'ἴ': 'i', 'ἵ': 'i', 'ἶ': 'i', 'ἷ': 'i', 'ὶ': 'i', 'ί': 'i', 'ῐ': 'i',
            'ῑ': 'i', 'ῒ': 'i', 'ΐ': 'i', 'ῖ': 'i', 'ῗ': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n',
            'ξ': 'ks', 'ο': 'o', 'ό': 'o', 'ὀ': 'o', 'ὁ': 'o', 'ὂ': 'o', 'ὃ': 'o', 'ὄ': 'o', 'ὅ': 'o',
            'ὸ': 'o', 'ό': 'o', 'π': 'p', 'ρ': 'r', 'ῤ': 'r', 'ῥ': 'r', 'σ': 's', 'ς': 's', 'τ': 't',
            'υ': 'y', 'ύ': 'y', 'ϋ': 'y', 'ΰ': 'y', 'ὐ': 'y', 'ὑ': 'y', 'ὒ': 'y', 'ὓ': 'y', 'ὔ': 'y',
            'ὕ': 'y', 'ὖ': 'y', 'ὗ': 'y', 'ὺ': 'y', 'ύ': 'y', 'ῠ': 'y', 'ῡ': 'y', 'ῢ': 'y', 'ΰ': 'y',
            'ῦ': 'y', 'ῧ': 'y', 'φ': 'f', 'χ': 'x', 'ψ': 'ps', 'ω': 'o', 'ώ': 'o', 'ὠ': 'o', 'ὡ': 'o',
            'ὢ': 'o', 'ὣ': 'o', 'ὤ': 'o', 'ὥ': 'o', 'ὦ': 'o', 'ὧ': 'o', 'ᾠ': 'o', 'ᾡ': 'o', 'ᾢ': 'o',
            'ᾣ': 'o', 'ᾤ': 'o', 'ᾥ': 'o', 'ᾦ': 'o', 'ᾧ': 'o', 'ὼ': 'o', 'ώ': 'o', 'ῲ': 'o', 'ῳ': 'o',
            'ῴ': 'o', 'ῶ': 'o', 'ῷ': 'o', '¨': '', '΅': '', '᾿': '', '῾': '', '῍': '', '῝': '', '῎': '',
            '῞': '', '῏': '', '῟': '', '῀': '', '῁': '', '΄': '', '΅': '', '`': '', '῭': '', 'ͺ': '',
            '᾽': '', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E', 'Ж': 'ZH',
            'З': 'Z', 'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P',
            'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'KH', 'Ц': 'TS', 'Ч': 'CH', 'Ш': 'SH',
            'Щ': 'SHCH', 'Ы': 'Y', 'Э': 'E', 'Ю': 'YU', 'Я': 'YA', 'а': 'A', 'б': 'B', 'в': 'V', 'г': 'G',
            'д': 'D', 'е': 'E', 'ё': 'E', 'ж': 'ZH', 'з': 'Z', 'и': 'I', 'й': 'I', 'к': 'K', 'л': 'L',
            'м': 'M', 'н': 'N', 'о': 'O', 'п': 'P', 'р': 'R', 'с': 'S', 'т': 'T', 'у': 'U', 'ф': 'F',
            'х': 'KH', 'ц': 'TS', 'ч': 'CH', 'ш': 'SH', 'щ': 'SHCH', 'ы': 'Y', 'э': 'E', 'ю': 'YU', 'я': 'YA',
            'Ъ': '', 'ъ': '', 'Ь': '', 'ь': '', 'ð': 'd', 'Ð': 'D', 'þ': 'th', 'Þ': 'TH',
            'ა': 'a', 'ბ': 'b', 'გ': 'g', 'დ': 'd', 'ე': 'e', 'ვ': 'v', 'ზ': 'z', 'თ': 't', 'ი': 'i',
            'კ': 'k', 'ლ': 'l', 'მ': 'm', 'ნ': 'n', 'ო': 'o', 'პ': 'p', 'ჟ': 'zh', 'რ': 'r', 'ს': 's',
            'ტ': 't', 'უ': 'u', 'ფ': 'p', 'ქ': 'k', 'ღ': 'gh', 'ყ': 'q', 'შ': 'sh', 'ჩ': 'ch', 'ც': 'ts',
            'ძ': 'dz', 'წ': 'ts', 'ჭ': 'ch', 'ხ': 'kh', 'ჯ': 'j', 'ჰ': 'h'}


def slugify(s, strip=False):
    """
    Simple slug filter, that has no knowledge of diacritics. Prefer slughifi (see below) to this method for good slugs,
    even if for simple languages like english this may be enough (and probably faster).

    >>> text = u"C'est déjà l'été."
    >>> slugify(text)
    'c-est-deja-l-ete-'

    """
    str = re.sub(r'\W+', '-', unidecode.unidecode(s).lower())
    if strip:
        str = re.sub('(^-+|-+$)', '', str)
    return str


def replace_char(m):
    char = m.group()
    if char in char_map:
        return char_map[char]
    else:
        return char


def unaccent(value):
    """
    Replace diacritics with their ascii counterparts.
    """
    # unicodification
    if type(value) != str:
        value = str(value, 'utf-8', 'ignore')

    # try to replace chars
    value = re.sub('[^a-zA-Z0-9\\s\\-]{1}', replace_char, value)

    return value.encode('ascii', 'ignore')


def slughifi(value, do_slugify=True, overwrite_char_map=None, strip=False):
    """
    High Fidelity slugify - slughifi.py, v 0.1

    This was found somewhere on internet, and slightly adapted for our needs.

    Examples :

    >>> text = u"C'est déjà l\'été."
    >>> slughifi(text)
    'c-est-deja-l-ete-'
    >>> slughifi(text, overwrite_char_map={"'": '-',})
    'c-est-deja-l-ete-'
    >>> slughifi(text, do_slugify=False)
    'C-est deja l-ete.'

    """

    # unicodification
    if type(value) != str:
        value = str(value, 'utf-8', 'ignore')

    # overwrite chararcter mapping
    if overwrite_char_map:
        char_map.update(overwrite_char_map)

    # try to replace chars
    value = re.sub('[^a-zA-Z0-9\\s\\-]{1}', replace_char, value)

    # apply ascii slugify
    if do_slugify:
        value = slugify(value, strip=strip)

    return value.encode('ascii', 'ignore')


def filter_html(value):
    """
    Simple filter that removes all html found and replace HTML line breaks by a simple line feed character.
    """
    from BeautifulSoup import BeautifulSoup

    if value is None:
        return None

    soup = BeautifulSoup(value)
    tags = soup.findAll(True)
    for tag in tags:
        if tag.name not in VALID_HTML_TAGS:
            tag.hidden = True

    if tags:
        value = soup.renderContents().replace('  ', ' ').replace('\n', '').replace('<br />', '\n')
    else:
        value = soup.renderContents().replace('  ', ' ')

    if value:
        value = html_unescape(str(value, 'utf-8'))

    return value


class Timer(object):
    """
    Context manager used to time execution of stuff.
    """

    def __enter__(self):
        self.__start = time.time()

    def __exit__(self, type=None, value=None, traceback=None):
        # Error handling here
        self.__finish = time.time()

    @property
    def duration(self):
        return self.__finish - self.__start

    def __str__(self):
        return str(int(self.duration * 1000) / 1000.0) + 's'


def create_http_reader(url):
    """
    Simple reader for an HTTP resource.
    """

    def http_reader():
        return requests.get(url).content

    return http_reader


def create_ftp_reader(url):
    """
    Simple reader for an HTTP resource.
    """
    import urllib.parse, ftplib

    parsed_url = urllib.parse.urlparse(url)

    def ftp_reader():
        ftp_file_content = []

        def handle_binary(data):
            ftp_file_content.append(data)

        ftp = ftplib.FTP(host=parsed_url.hostname,
                         user=parsed_url.username,
                         passwd=parsed_url.password)
        ftp.retrbinary(cmd='RETR {0}'.format(parsed_url.path),
                       callback=handle_binary)
        return ''.join(ftp_file_content)

    return ftp_reader


def create_file_reader(path):
    """
    Simple reader for a local filesystem resource.
    """

    def file_reader():
        with open(path, 'rU') as f:
            return f.read()

    return file_reader

def sfloat(mixed, default=None):
    """Safe float cast."""
    try:
        return float(mixed)
    except:
        return default

def sint(mixed, default=None):
    """Safe int cast."""
    try:
        return int(mixed)
    except:
        return default

def sbool(mixed, default=None):
    """Safe boolean cast."""
    try:
        return bool(mixed)
    except:
        return default

# Exports
try:
    terminal = _Terminal()
except:
    class FakeTerminal(object):
        clear_eol = ''
        move_up = ''
        is_a_tty = False
        def __call__(self, *args):
            return ''.join(*args)
        def __getattr__(self, item):
            return self
    terminal = FakeTerminal()


html_escape = cgi.escape
def html_unescape(txt):
    if not isinstance(txt, str):
        try:
            txt = txt.decode('raw_unicode_escape')
        except:
            print(txt)

    return html_parser.HTMLParser().unescape(txt)
now = datetime.now
cached_property = cached_property
etree = etree

