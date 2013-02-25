# -*- coding: utf-8 -*-

# Copyright(C) 2010-2012 Julien Veyssier
#
# This file is part of weboob.
#
# weboob is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# weboob is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with weboob. If not, see <http://www.gnu.org/licenses/>.


try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs  # NOQA

from urlparse import urlsplit

from weboob.capabilities.subtitle import Subtitle
from weboob.capabilities.base import NotAvailable
from weboob.tools.browser import BasePage
from weboob.tools.misc import get_bytes_size
import time


__all__ = ['SubtitlesPage','SearchPage']


class SearchPage(BasePage):
    """ Page which contains results as a list of movies
    """
    def iter_subtitles(self):
        tabresults = self.parser.select(self.document.getroot(),'table#search_results')
        if len(tabresults) > 0:
            table = tabresults[0]
            # for each result line, explore the subtitle list page to iter subtitles
            for line in self.parser.select(table,'tr'):
                links = self.parser.select(line,'a')
                if len(links) > 0:
                    a = links[0]
                    url = a.attrib.get('href','')
                    if "ads.opensubtitles" not in url:
                        self.browser.location("http://www.opensubtitles.org%s"%url)
                        assert self.browser.is_on_page(SubtitlesPage) or self.browser.is_on_page(SubtitlePage)
                        # subtitles page does the job
                        for subtitle in self.browser.page.iter_subtitles():
                            yield subtitle


class SubtitlesPage(BasePage):
    """ Page which contains several subtitles for a single movie
    """
    def iter_subtitles(self):
        tabresults = self.parser.select(self.document.getroot(),'table#search_results')
        if len(tabresults) > 0:
            table = tabresults[0]
            # for each result line, get informations
            # why following line doesn't work all the time (for example 'search fr sopranos guy walks' ?
            #for line in self.parser.select(table,'tr'):
            for line in table.getiterator('tr'):
                # some lines are useless, specially ads
                if line.attrib.get('id','').startswith('name'):
                    yield self.get_subtitle_from_line(line)

    def get_subtitle_from_line(self,line):
        cells = self.parser.select(line,'td')
        if len(cells) > 0:
            first_cell = cells[0]
            links = self.parser.select(line,'a')
            a = links[0]
            urldetail = a.attrib.get('href','')
            self.browser.location("http://www.opensubtitles.org%s"%urldetail)
            assert self.browser.is_on_page(SubtitlePage)
            # subtitle page does the job
            return self.browser.page.get_subtitle()
            """
            faster but less accurate
            we can already get the subtitle from the list page
            """
            #name = u" ".join(a.text.strip().split())
            #spanlist = self.parser.select(first_cell,'span')
            #if len(spanlist) > 0:
            #    long_name = spanlist[0].attrib.get('title','')
            #else:
            #    texts = first_cell.itertext()
            #    long_name = texts.next()
            #    long_name = texts.next()
            #    if "Download at 25" in long_name:
            #        long_name = "---"
            #name = "%s (%s)"%(name,long_name)
            #second_cell = cells[1]
            #link = self.parser.select(second_cell,'a',1)
            #lang = link.attrib.get('href','').split('/')[-1].split('-')[-1]
            #nb_cd = int(cells[2].text.strip().lower().replace('cd',''))
            #fps = 0
            #desc = ''
            #cell_dl = cells[4]
            #href = self.parser.select(cell_dl,'a',1).attrib.get('href','')
            #url = "http://www.opensubtitles.org%s"%href
            #id = href.split('/')[-1]

            #subtitle = Subtitle(id,name)
            #subtitle.url = url
            #subtitle.fps = fps
            #subtitle.language = lang
            #subtitle.nb_cd = nb_cd
            #subtitle.description = "no desc"
            #return subtitle


class SubtitlePage(BasePage):
    """ Page which contains a single subtitle for a movie
    """
    def get_subtitle(self):
        father = self.parser.select(self.document.getroot(),'a#app_link',1).getparent()
        a = self.parser.select(father,'a')[1]
        id = a.attrib.get('href','').split('/')[-1]
        url = "http://www.opensubtitles.org/subtitleserve/sub/%s"%id
        link = self.parser.select(self.document.getroot(),'link[rel=bookmark]',1)
        title = link.attrib.get('title','')
        nb_cd = int(title.lower().split('cd')[0].split()[-1])
        lang = title.split('(')[1].split(')')[0]
        file_names = self.parser.select(self.document.getroot(),"img[title~=filename]")
        if len(file_names) > 0:
            file_name = file_names[0].getparent().text_content()
            file_name = " ".join(file_name.split())
            desc = u"files :"
            for f in file_names:
                desc_line = f.getparent().text_content()
                desc += "\n"+" ".join(desc_line.split())
        name = "%s (%s)"%(title,file_name)
        fps = 0

        subtitle = Subtitle(id,name)
        subtitle.url = url
        subtitle.fps = fps
        subtitle.language = lang
        subtitle.nb_cd = nb_cd
        subtitle.description = desc
        return subtitle

    def iter_subtitles(self):
        yield self.get_subtitle()