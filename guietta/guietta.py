# -*- coding: utf-8 -*-

import functools
from collections import Iterable

from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtWidgets import QPushButton, QRadioButton, QCheckBox
from PyQt5.QtWidgets import QLineEdit, QGridLayout


if QApplication.instance() is None:
    app = QApplication([])


# Widget shortcuts

B = QPushButton
E = QLineEdit
_ = QLabel
C = QCheckBox
R = QRadioButton

class ___:   # Horizontal continuation
    pass

class I:     # Vertical continuation
    pass

_specials = (_, ___, I)

_default_signals = { QPushButton: 'clicked',
                    QLineEdit: 'returnPressed' }

# Some helper functions


def _iterable(x):
    return isinstance(x, Iterable) and not isinstance(x, str)


def _normalize(x):
    return ''.join(c for c in x if c.isalnum() or c == '_')


def _bound_method(method):
    return hasattr(method, '__self__')


def _layer_check(*lists, element_func=lambda x: True, errstr=''):
    '''
    Argument checking for layers.

    Checks that the arguments to a layer (__init__, events(), colors(), etc)
    are well-formed: a series of lists of equal lengths
    and with valid elements. In case on any error, an exception
    will be raised.

    Parameters
    ----------
    *lists : any
        the arguments to check
    element_func : callable, optional
        the function to call for all elements, returning True if the
        element is valid. If not set, elements are always valid

    Raises
    ------
    ValueError
        In case the arugments are not lists.
    TypeError
        In case the lists have differing lengths or the elements are not valid
    '''
    ncols = len(lists[0])
    for row in lists:
        if not _iterable(row):
            raise ValueError('Arguments are not lists (or iterables)')

        if len(row) != ncols:
            raise ValueError('Row lengths differ')
        for element in row:
            if not element_func(element) and element not in _specials:
                raise TypeError(errstr)


class Gui:
    '''Main GUI object'''

    def __init__(self, *lists):

        # Input argument checks
        def must_be_widget(x):
            return isinstance(x, QWidget) or x in _specials
        _layer_check(*lists, element_func=must_be_widget,
                     errstr='Elements are not widgets')

        self._layout = QGridLayout()
        self._widgets = {}    # widgets by name
        self._aliases = {}    # name aliases (1 alias per name)

        # Intermediate step that will be filled by replicating
        # widgets when ___ and I are encountered.
        self._step1 = []
        for row in lists:
            self._step1.append([])
            for j in row:
                self._step1[-1].append(None)

        for i, row in enumerate(lists):
            for j, element in enumerate(row):

                # Special cases
                if element == _:
                    element = QLabel('')
                elif element == ___:
                    self._step1[i][j] = self._step1[i][j-1]
                    continue
                elif element == I:
                    self._step1[i][j] = self._step1[i-1][j]
                    continue

                self._step1[i][j] = element

        # Now a multi-cell widget has been replicated both in rows
        # and in columns. Look for repetitions to calculate spans.
     
        done = set()  # To avoid repeated insertions
        for i, row in enumerate(lists):
            for j, element in enumerate(row):

                element = self._step1[i][j]
                if element not in done:
                    rowspan = 0
                    colspan = 0
                    for ii in range(i, len(lists)):
                        if self._step1[ii][j] == element:
                            rowspan += 1
                    for jj in range(j, len(row)):
                        if self._step1[i][jj] == element:
                            colspan += 1

                    self._layout.addWidget(element, i, j, rowspan, colspan)
                    text = _normalize(element.text())
                    while text in self._widgets:
                        text += '_'
                    self._widgets[text] = element
                    done.add(element)

    def events(self, *lists):
        '''Defines the GUI events'''

        # Input argument checks
        def must_be_callable(x):
            return callable(x) or x in _specials
        _layer_check(*lists, element_func=must_be_callable,
                     errstr='Elements are not callables')

        for i, row in enumerate(lists):
            for j, slot in enumerate(row):

                if slot not in _specials:
                    item = self[i,j]
                    signal = getattr(item, _default_signals[item.__class__])
                    if _bound_method(slot):
                        signal.connect(slot)
                    else:
                        f = functools.partial(slot, self)
                        signal.connect(functools.partial(slot, self))

    def names(self, *lists):
        '''Overrides the default names'''
        _layer_check(*lists, element_func=lambda x: isinstance(x, str),
                     errstr='Elements are not strings')

        names_by_widget = {v: k for k, v in self._widgets.items()}
        print(names_by_widget)

        for i, row in enumerate(lists):
            for j, alias in enumerate(row):

                if alias not in _specials:
                    item = self[i,j]
                    name = names_by_widget[item]
                    self._aliases[alias] = name

    def colors(self, *args):
        '''Defines the GUI events'''
        pass

    def groups(self, *args):
        '''Defines the GUI events'''
        pass

    def __getattr__(self, name):
        '''Returns a widget using its name or alias'''
        
        if name in self._aliases:
            name = self._aliases[name]
            
        if name in self._widgets:
            return self._widgets[name]
        else:
            # Default behaviour
            raise AttributeError

    def __getitem__(self, name):
        '''widget by coordinates [row,col]'''
        return self._layout.itemAtPosition(name[0], name[1]).widget()

    def all(group=''):
        '''replicates command on all widgets'''
        pass

    def window(self):
        window = QWidget()
        window.setLayout(self._layout)
        return window

    def import_into(self, obj):

        widgets = {**self._widgets, **self._aliases}

        for name, widget in widgets.items():
            if hasattr(obj, name):
                raise Exception('Cannot import: duplicate name %s ' % name)
            else:
                setattr(obj, name, widget)
        
    def run(self, argv=None):
        if argv is None:
            argv = []
        app = QApplication.instance()
        window = self.window()
        window.show()
        app.exec_()
        

        
        
        