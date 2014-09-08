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
import os
import time
import datetime

from rdc.etl import DEFAULT_FIELD
from rdc.etl.transform.extract import Extract
from rdc.etl.util import create_http_reader, create_file_reader, cached_property, create_ftp_reader


class FileExtract(Extract):
    """
    Extract data from a file into a field.

    .. attribute:: uri

        The path for source file. Can be either an absolute/relative filesystem path or an HTTP/HTTPS resource.

    .. attribute:: output_field

        The field that will contain file content. Use the topic (`_`) field by default.

    """
    uri = None
    output_field = DEFAULT_FIELD

    def __init__(self, uri=None, output_field=None):
        super(FileExtract, self).__init__()

        self.uri = uri or self.uri
        self.output_field = output_field or self.output_field

    @cached_property
    def reader(self):
        if self.uri is None:
            raise RuntimeError('No URI configured in ' + self.__class__.__name__ + ' transformation.')

        if self.uri.find('http://') == 0 or self.uri.find('https://') == 0:
            return create_http_reader(self.uri)
        elif self.uri.find('ftp://') == 0:
            return create_ftp_reader(self.uri)
        else:
            return create_file_reader(self.uri)

    @cached_property
    def content(self):
        return self.reader()

    def extract(self):
        yield {
            self.output_field: self.content
        }

class CachedFileExtract(FileExtract):
    def __init__(self, uri=None, output_field=None, cache_path=None, cache_lifetime=None):
        super(CachedFileExtract, self).__init__(uri, output_field)
        self.cache_path = cache_path
        self.cache_lifetime = cache_lifetime


    @cached_property
    def content(self):
        if not os.path.exists(self.cache_path) or os.path.getmtime(self.cache_path) < time.mktime(
                (datetime.datetime.now() - datetime.timedelta(seconds=self.cache_lifetime)).timetuple()):
            with open(self.cache_path, 'w+b') as f:
                f.write(self.reader())

        with open(self.cache_path, 'r') as f:
            return f.read()