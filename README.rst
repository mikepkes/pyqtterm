PyQtTerm
================

PyQtTerm is a python-based qt widget providing basic python editing and execution.

Motivation
----------
PyQtTerm was started to allow for an easy way to integrate a python terminal in applications
that already provide a python interpreter but no interactive console/terminal.

Existing Functionality
----------------------
- Live Terminal Execution
- Basic Syntax Highlighting
- Current Line Highlighting
- Line Numbering
- Syntax Error Line Highlighting
- Traceback Hyperlinks (with hover-over detail)

Planned Functionality
---------------------
- Stacktrace Browser
- Better Syntax Markup
- Verbose Syntax Error Popover
- Source File Loading
- History Restore

Installation
------------
```
python setup.py build
python setup.py install
```

Usage
-----

```
    from PySide import QtGui
    import qtterm
    import sys
    app = QtGui.QApplication(sys.argv)
    w = qtterm.QtTermWidget()
    w.show()
    app.exec_()
```

License
-------

Provided under the Simplified BSD License
