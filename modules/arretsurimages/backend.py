# -*- coding: utf-8 -*-

# Copyright(C) 2013      franek
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


from weboob.capabilities.video import ICapVideo, BaseVideo
from weboob.capabilities.collection import ICapCollection, CollectionNotFound
from weboob.tools.backend import BaseBackend, BackendConfig
from weboob.tools.value import ValueBackendPassword

from .browser import ArretSurImagesBrowser
from .video import ArretSurImagesVideo

__all__ = ['ArretSurImagesBackend']


class ArretSurImagesBackend(BaseBackend, ICapVideo, ICapCollection):
    NAME = 'arretsurimages'
    DESCRIPTION = u'arretsurimages website'
    MAINTAINER = u'franek'
    EMAIL = 'franek@chicour.net'
    VERSION = '0.f'

    CONFIG = BackendConfig(ValueBackendPassword('login',    label='email', masked=False),
                           ValueBackendPassword('password', label='Password'))
    BROWSER = ArretSurImagesBrowser
    
    def create_default_browser(self):
        return self.create_browser(self.config['login'].get(), self.config['password'].get())
    
    def search_videos(self, pattern, sortby=ICapVideo.SEARCH_RELEVANCE, nsfw=False, max_results=None):
        with self.browser:
            return self.browser.search_videos(pattern)
            
    def get_video(self, _id):
        with self.browser:
            return self.browser.get_video(_id)            
            
    def fill_video(self, video, fields):
        if fields != ['thumbnail']:
            # if we don't want only the thumbnail, we probably want also every fields
            with self.browser:
                video = self.browser.get_video(ArretSurImagesVideo.id2url(video.id), video)
        if 'thumbnail' in fields and video.thumbnail:
            with self.browser:
                video.thumbnail.data = self.browser.readurl(video.thumbnail.url)

        return video            

    OBJECTS = {ArretSurImagesVideo: fill_video}