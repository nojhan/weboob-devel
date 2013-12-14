# -*- coding: utf-8 -*-

# Copyright(C) 2013      Romain Bignon
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


from weboob.tools.browser import BaseBrowser

from .pages import CitiesPage, SearchPage, SearchErrorPage, \
                   SearchInProgressPage, ResultsPage


__all__ = ['VoyagesSNCFBrowser']


class VoyagesSNCFBrowser(BaseBrowser):
    PROTOCOL = 'http'
    DOMAIN = 'www.voyages-sncf.com'
    ENCODING = 'utf-8'

    PAGES = {
        'http://www.voyages-sncf.com/completion/VSC/FR/fr/cityList.js':     (CitiesPage, 'raw'),
        'http://www.voyages-sncf.com/billet-train':                         SearchPage,
        'http://www.voyages-sncf.com/billet-train\?.+':                     SearchErrorPage,
        'http://www.voyages-sncf.com/billet-train/recherche-en-cours.*':    SearchInProgressPage,
        'http://www.voyages-sncf.com/billet-train/resultat.*':              ResultsPage,
    }

    def get_stations(self):
        self.location('/completion/VSC/FR/fr/cityList.js')
        return self.page.get_stations()

    def iter_departures(self, departure, arrival, date):
        self.location('/billet-train')
        self.page.search(departure, arrival, date)

        return self.page.iter_results()
