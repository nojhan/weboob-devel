# -*- coding: utf-8 -*-

# Copyright(C) 2010  Romain Bignon
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import sys
from PyQt4.QtCore import QTimer, SIGNAL, QObject, QString, QSize
from PyQt4.QtGui import QMainWindow, QApplication, QStyledItemDelegate, \
                        QStyleOptionViewItemV4, QTextDocument, QStyle, \
                        QAbstractTextDocumentLayout, QPalette

from weboob.core.ouiboube import Weboob
from weboob.core.scheduler import IScheduler

from ..base import BaseApplication

__all__ = ['QtApplication', 'QtMainWindow', 'QtDo', 'HTMLDelegate']

class QtScheduler(IScheduler):
    def __init__(self, app):
        self.app = app
        self.timers = {}

    def schedule(self, interval, function, *args):
        timer = QTimer()
        timer.setInterval(interval)
        timer.setSingleShot(False)
        self.app.connect(timer, SIGNAL("timeout()"), lambda: self.timeout(timer.timerId(), False, function, *args))
        self.timers[timer.timerId()] = timer

    def repeat(self, interval, function, *args):
        timer = QTimer()
        timer.setInterval(interval)
        timer.setSingleShot(True)
        self.app.connect(timer, SIGNAL("timeout()"), lambda: self.timeout(timer.timerId(), True, function, *args))
        self.timers[timer.timerId()] = timer

    def timeout(self, _id, single, function, *args):
        function(*args)
        if single:
            self.timers.pop(_id)

    def want_stop(self):
        self.app.quit()

    def run(self):
        self.app.exec_()

class QtApplication(QApplication, BaseApplication):
    def __init__(self):
        QApplication.__init__(self, sys.argv)
        self.setApplicationName(self.APPNAME)

        BaseApplication.__init__(self)

    def create_weboob(self):
        return Weboob(scheduler=QtScheduler(self))

class QtMainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

class QtDo(QObject):
    def __init__(self, weboob, cb, eb=None):
        QObject.__init__(self)

        if not eb:
            eb = self.default_eb

        self.weboob = weboob
        self.process = None
        self.cb = cb
        self.eb = eb

        self.connect(self, SIGNAL('cb'), self.local_cb)
        self.connect(self, SIGNAL('eb'), self.local_eb)

    def run_thread(func):
        def inner(self, *args, **kwargs):
            self.process = func(self, *args, **kwargs)
            self.process.callback_thread(self.thread_cb, self.thread_eb)
        return inner

    @run_thread
    def do(self, *args, **kwargs):
        return self.weboob.do(*args, **kwargs)

    @run_thread
    def do_caps(self, *args, **kwargs):
        return self.weboob.do_caps(*args, **kwargs)

    @run_thread
    def do_backends(self, *args, **kwargs):
        return self.weboob.do_backends(*args, **kwargs)

    def default_eb(self, backend, error, backtrace):
        # TODO display a messagebox
        print error
        print backtrace

    def local_cb(self, backend, data):
        self.cb(backend, data)
        if not backend:
            self.disconnect(self, SIGNAL('cb'), self.local_cb)
            self.disconnect(self, SIGNAL('eb'), self.local_eb)

    def local_eb(self, backend, error, backtrace):
        self.eb(backend, error, backtrace)
        self.disconnect(self, SIGNAL('cb'), self.local_cb)
        self.disconnect(self, SIGNAL('eb'), self.local_eb)

    def thread_cb(self, backend, data):
        self.emit(SIGNAL('cb'), backend, data)

    def thread_eb(self, backend, error, backtrace):
        self.emit(SIGNAL('eb'), backend, error, backtrace)

class HTMLDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        optionV4 = QStyleOptionViewItemV4(option)
        self.initStyleOption(optionV4, index)

        style = optionV4.widget.style() if optionV4.widget else QApplication.style()

        doc = QTextDocument()
        doc.setHtml(optionV4.text)

        # painting item without text
        optionV4.text = QString()
        style.drawControl(QStyle.CE_ItemViewItem, optionV4, painter)

        ctx = QAbstractTextDocumentLayout.PaintContext()

        # Hilight text if item is selected
        if optionV4.state & QStyle.State_Selected:
            ctx.palette.setColor(QPalette.Text, optionV4.palette.color(QPalette.Active, QPalette.HighlightedText))

        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, optionV4)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        optionV4 = QStyleOptionViewItemV4(option)
        self.initStyleOption(optionV4, index)

        doc = QTextDocument()
        doc.setHtml(optionV4.text)
        doc.setTextWidth(optionV4.rect.width())

        return QSize(doc.idealWidth(), max(doc.size().height(), optionV4.decorationSize.height()))
