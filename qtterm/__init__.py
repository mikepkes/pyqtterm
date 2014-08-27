#!/usr/bin/python

"""
Copyright (c) 2014, Michael Kessler
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

import ast
import sys
import traceback
import math
import keyword as pythonkeyword
import __builtin__
from threading import Lock

__author__ = "Michael Kessler"
__author_email__ = "mike@toadgrass.com"
__copyright__ = "Copyright 2014, Michael Kessler"
__credits__ = ["Michael Kessler"]
__license__ = "Simplified BSD"
__version__ = "0.1"
__maintainer__ = "Michael Kessler"
__maintainer_email__ = "mike@toadgrass.com"
__module_name__ = "qtterm"
__short_desc__ = "A QT simple python-qt based python terminal"
__status__ = "Planning"
__url__ = 'http://www.github.com/michaelkessler/pyqtterm'

try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui

# From http://blog.client9.com/2008/10/04/escaping-html-in-python.html
# This is really really ugly.
def html_escape(text):
    text = text.replace('&', '&amp;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    text = text.replace(">", '&gt;')
    text = text.replace("<", '&lt;')
    return text

class OutputRedirect(QtCore.QObject):

    output = QtCore.Signal(str)

    def __init__(self, tee=True, parent=None):
        super(OutputRedirect, self).__init__(parent)
        self._handle = None
        self._tee = tee

    def __enter__(self):
        self._handle = sys.stdout
        sys.stdout = self
        return self

    def __exit__(self, type, value, traceback):
        sys.stdout = self._handle
        

    def write(self, msg):
        self.output.emit(msg)
        if self._tee:
            self._handle.write(msg)
        

class HighlightRule(object):
    def __init__(self, pattern, format):
        self.pattern = pattern
        self.format = format

class PythonHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent):
        super(PythonHighlighter, self).__init__(parent)
        self.rules = []

        brush = QtGui.QBrush(QtCore.Qt.darkGreen, QtCore.Qt.SolidPattern)
        builtin = QtGui.QTextCharFormat()
        builtin.setForeground(brush)
        builtin.setFontWeight(QtGui.QFont.Bold)
        builtins = dir(__builtin__)

        for word in builtins:
            pattern = QtCore.QRegExp("\\b{w}\\b".format(w=word))
            rule = HighlightRule(pattern, builtin)
            self.rules.append(rule)

        brush = QtGui.QBrush( QtCore.Qt.darkBlue, QtCore.Qt.SolidPattern)
        keyword = QtGui.QTextCharFormat()
        keyword.setForeground(brush)
        keyword.setFontWeight(QtGui.QFont.Bold)
        keywords = pythonkeyword.kwlist

        for word in keywords:
            pattern = QtCore.QRegExp("\\b{w}\\b".format(w=word))
            rule = HighlightRule(pattern, keyword)
            self.rules.append(rule)

        brush = QtGui.QBrush(QtGui.QColor.fromRgb(255,140,0),QtCore.Qt.SolidPattern)
        pattern = QtCore.QRegExp( "#[^\n]*")
        comment = QtGui.QTextCharFormat()
        comment.setForeground(brush)
        comment.setFontWeight(QtGui.QFont.Light)
        rule = HighlightRule(pattern, comment)
        self.rules.append(rule)

        self.setDocument(parent.document())

    def highlightBlock(self, text):
        for rule in self.rules:
            expression = QtCore.QRegExp(rule.pattern)
            index = expression.indexIn(text)
            while index>=0:
                length = expression.matchedLength()
                self.setFormat(index, length, rule.format)
                index = expression.indexIn(text, index+length)
        self.setCurrentBlockState(0)
            
class QtTermEntryLineNumberWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(QtTermEntryLineNumberWidget, self).__init__(parent)
        self._editor = parent

    def paintEvent(self, event):
        self._editor.lineNumberAreaPaintEvent(event)

class QtTermEntryWidget(QtGui.QPlainTextEdit):

    traceback = QtCore.Signal(int)
    syntaxError = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(QtTermEntryWidget, self).__init__(parent)

        self._termWidget = parent
        font = QtGui.QFont("Monaco")
        font.setStyleHint(font.TypeWriter, font.PreferDefault)
        self.setFont(font)

        self._lineNumber = QtTermEntryLineNumberWidget(self)
        self._highlighter = PythonHighlighter(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0);
        self.highlightCurrentLine();

        self.executeAction = QtGui.QAction('Execute Python', self)
        self.executeAction.setShortcut(QtGui.QKeySequence("Ctrl+Return"))
        self.executeAction.triggered.connect(self.execute)
        self.addAction(self.executeAction)

        self.syntaxError.connect(self.displaySyntaxError)

        self.stdoutRedirect = OutputRedirect()

        self._locals = {}

    def displaySyntaxError(self, line):

        sel = QtGui.QTextEdit.ExtraSelection()
        lineColor = QtGui.QColor(QtCore.Qt.red).lighter(150)
        sel.format.setBackground(QtGui.QBrush(lineColor,QtCore.Qt.SolidPattern))
        sel.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        sel.cursor = QtGui.QTextCursor(self.document())
        sel.cursor.movePosition(sel.cursor.NextBlock, QtGui.QTextCursor.MoveAnchor, line-1)
        sel.cursor.clearSelection()
        extraSelections = [sel]

        self.setExtraSelections(extraSelections)

    def execute(self):
        script = self.toPlainText()

        try:
            script_code = compile(script, '<interactive interpreter>', 'exec')
        except (SyntaxError) as e:
            self.syntaxError.emit(e.lineno)
            return
        with self.stdoutRedirect:
            try:
                exec(script_code, globals(), self._locals)
            except (StandardError) as e: #Which error should this be?
                type_, value_, traceback_ = sys.exc_info()
                tb = traceback.extract_tb(traceback_)

                index = self._termWidget.storeTraceback(tb)
                self.traceback.emit(index)


    def lineNumberAreaPaintEvent(self, event):
        painter = QtGui.QPainter(self._lineNumber)
        painter.fillRect(event.rect(), QtGui.QColor.fromRgb(200,200,200))
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber+1)
                painter.setPen(QtCore.Qt.black)
                painter.drawText(0, top, self._lineNumber.width(), self.fontMetrics().height(), QtCore.Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def highlightCurrentLine(self):

        sel = QtGui.QTextEdit.ExtraSelection()
        lineColor = QtGui.QColor(QtCore.Qt.gray).lighter(150)
        sel.format.setBackground(QtGui.QBrush(lineColor,QtCore.Qt.DiagCrossPattern))
        sel.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        sel.cursor = self.textCursor()
        sel.cursor.clearSelection()
        extraSelections = [sel]

        self.setExtraSelections(extraSelections)

    def updateLineNumberArea(self, area, num):
        if (num):
            self._lineNumber.scroll(0, num)
        else:
            self._lineNumber.update(0, area.y(), self._lineNumber.width(), area.height())

        if area.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def updateLineNumberAreaWidth(self, num):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def lineNumberAreaWidth(self):
        digits = math.floor(math.log10(self.blockCount()))+1
        space = 3 + self.fontMetrics().width('9')*digits
        return space

    def resizeEvent(self, event):
        super(QtTermEntryWidget, self).resizeEvent(event)

        cr = self.contentsRect()
        nr = QtCore.QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())
        self._lineNumber.setGeometry(nr)

class QtTermResultsWidget(QtGui.QTextBrowser):
    def __init__(self, parent=None):
        super(QtTermResultsWidget, self).__init__(parent)
        self.setOpenLinks(False)
        self.anchorClicked.connect(self.handleLink)
        cursor = self.textCursor()
        self.setReadOnly(True)

        self._termWidget = parent

        self.writeLock = Lock()

    def handleLink(self, url):
        pass
        #TODO: Implement some sort of traceback display.

    def handleOutput(self, text):
        with self.writeLock:
            self.moveCursor(QtGui.QTextCursor.End)
            self.insertPlainText(text)

    def handleTraceback(self, index):
        with self.writeLock:
            tb = self._termWidget.traceback(index)
            self.moveCursor(QtGui.QTextCursor.End)

            linkName = "Error: {path}".format(path=traceback.format_list(tb)[-1])
            hoverText = ' '.join(traceback.format_list(tb))
            # For some reason the </a> doesn't get closed unless we have something after it, hence the space.
            self.insertHtml("""<a href='traceback:///{index}' title='{hoverText}'>{linkName} </a>&nbsp""".format(
                    linkName=linkName,
                    index=index,
                    hoverText=hoverText,
                )
            )
            self.insertPlainText("\n")

class QtTermWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(QtTermWidget, self).__init__(parent)

        layout = QtGui.QVBoxLayout(self)
        self._splitter = QtGui.QSplitter(QtCore.Qt.Vertical, self)
        layout.addWidget(self._splitter)

        self._results = QtTermResultsWidget(self)
        self._splitter.addWidget(self._results)

        self._entry = QtTermEntryWidget(self)
        self._splitter.addWidget(self._entry)

        self.setLayout(layout)

        self._tracebacks = []

        self._entry.traceback.connect(self._results.handleTraceback)

        self._entry.stdoutRedirect.output.connect(self._results.handleOutput)

    def traceback(self, index):
        return self._tracebacks[index]


    def storeTraceback(self, tb):
        self._tracebacks.append(tb)
        return len(self._tracebacks)-1

def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    w = QtTermWidget()
    w.show()
    app.exec_()

if __name__ == "__main__":
    main()

