# -*- coding: utf-8 -*-

# Copyright(C) 2013      Bezleputh
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


from weboob.tools.test import BackendTest


class ApecTest(BackendTest):
    BACKEND = 'apec'

    def test_apec(self):
        l = list(self.backend.search_job(u'maitre brasseur'))
        assert len(l)
        advert = self.backend.get_job_advert(l[0].id, None)
        print advert.__repr__()
        self.assertTrue(advert.url, 'URL for announce "%s" not found: %s' % (advert.id, advert.url))