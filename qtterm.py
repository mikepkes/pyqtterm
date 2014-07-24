#!/usr/bin/python

import traceback
import math
import keyword as pythonkeyword
import __builtin__

try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui

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
    def __init__(self, parent=None):
        super(QtTermEntryWidget, self).__init__(parent)

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

    def execute(self):
        script = self.toPlainText()
        try:
            exec(script)
        except Exception:
            print traceback.format_exc()

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

    def handleLink(self, url):
        print url

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


        self._results.insertHtml("<a href='http://www.google.com'>Go to Google</a>")

def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    w = QtTermWidget()
    w.show()
    app.exec_()

if __name__ == "__main__":
    main()

