# -*- coding: utf-8-*-
"""This module provides classes and functions used for in-game menus."""

import pygame, sys

class _menu_entry:
    """This helper class represents an entry in a menu."""
    def __init__(self, label, reset_cb, enter_cb, inc_cb, dec_cb):
        """*label* - string - text label for this menu entry; *reset_cb* - function - callback executed to obtain initial value for this entry (if used), it should return a string; *enter_cb* - function - callback executed when this entry is **selected**, it can return a string (the new value); *inc_cb* - function - callback executed when this entry is **incremented**, it can return a string (the new value); *dec_cb* - function - callback executed when this entry is **decremented**, it can return a string (the new value).
        
        All callbacks take two arguments. The first one is an index (counting from 0) of the entry for which it's called in the current (sub)menu (so one set of callbacks can be defined for multiple entries). The second one is any object, the one provided by the argument *conf* of :py:class:`Menu` constructor. Any callback (or all) can be set to None, meaning it's not used."""
        self.label, self.reset_cb = label, reset_cb
        self.enter_cb = enter_cb
        self.inc_cb, self.dec_cb = inc_cb, dec_cb
        self.val = ""
        
class _menu:
    """This helper class represents a (sub)menu"""
    def __init__(self, label, contents):
        """*label* - string - text label of this sub menu, ignored if it's the root menu; *contents* - list of positions in this menu, either instances of this class or of :py:class:`_menu_entry`. See :py:data:`menu_layout` in **sliced/__init__.py** for an example."""
        self.label = label
        self.contents = contents

class Menu:
    """This class represents a menu."""
    def __init__(self, layout, conf):
        """*layout* - :py:class:`_menu` - layout of this menu; *conf* - any object to be passed to callbacks."""
        self.layout = layout
        self.path = [] #: list of strings of submenu's labels in path from current submenu to the root
        self.current = layout.contents
        self.selected = 0 #: index of currently selected position in current submenu
        self.conf = conf
        self.reset(self.current)
    def update_values(self):
        """Call :py:meth:`reset` on the whole menu."""
        self.reset(self.layout.contents)
    def reset(self, lay):
        """Recursively call reset callbacks on all entries in the submenu *lay*."""
        for i in xrange(len(lay)):
            if isinstance(lay[i], _menu):
                self.reset(lay[i].contents)
            else:
                if lay[i].reset_cb:
                    lay[i].val = lay[i].reset_cb(i, self.conf)
    def get_path(self):
        """Return a string representation of the current path."""
        return "/"+"/".join(self.path)
    def get_options_list(self):
        """Get list of positions in current submenu. Each element is a tuple *(label, value)*."""
        l=[]
        for i in self.current:
            if isinstance(i, _menu):
                l.append((i.label, ""))
            else:
                if i.val:
                    l.append((i.label, i.val))
                else:
                    l.append((i.label, ""))
        return l  
    def get_options_list2(self):
        """Get list of positions in current submenu. Each element is a string."""
        l=[]
        for i in self.current:
            if isinstance(i, _menu):
                l.append(i.label+"/")
            else:
                if i.val:
                    l.append(i.label+" : "+i.val)
                else:
                    l.append(i.label)
        return l   
    def escape(self):
        """Go one level up in the menu, if possible."""
        if self.path:
            self.selected = 0
            self.path = self.path[:-1]
            self.current = self.layout.contents
            for i in self.path:
                for j in self.current:
                    if j.label == i:
                        self.current = j.contents
                        break
    def enter(self):
        """If current position is a submenu, set the current submenu as that, else call the **enter callback** and update the value if needed."""
        opt = self.current[self.selected]
        if isinstance(opt, _menu):
            self.path.append(opt.label)
            self.current = opt.contents
            self.selected = 0
        else:
            if opt.enter_cb:
                tmp = opt.enter_cb(self.selected, self.conf)
                opt.val = tmp if tmp else ""
    def right(self):
        """If current position is an entry, call the **increment callback** and update the value if needed."""
        opt = self.current[self.selected]
        if isinstance(opt, _menu_entry) and opt.inc_cb:
            tmp = opt.inc_cb(self.selected, self.conf)
            opt.val = tmp if tmp else ""
    def left(self):
        """If current position is an entry, call the **decrement callback** and update the value if needed."""
        opt = self.current[self.selected]
        if isinstance(opt, _menu_entry) and opt.dec_cb:
            tmp = opt.dec_cb(self.selected, self.conf)
            opt.val = tmp if tmp else ""
    def up(self):
        """Increment current position index by 1 modulo number of positions (so if it's at the last it will go to the first)"""
        self.selected = ((self.selected-1)%len(self.current))
    def down(self):
        """Decrement current position index by 1 modulo number of positions (so if it's at the first it will go to the last)"""
        self.selected = ((self.selected+1)%len(self.current))

def bool2yn(b):
    """Helper function, returns \"yes\" if *b* is True, \"no\" if *b* is False."""
    return ["no", "yes"][b]
