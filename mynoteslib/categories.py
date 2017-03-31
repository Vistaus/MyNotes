#! /usr/bin/python3
# -*- coding:Utf-8 -*-
"""
My Notes - Sticky notes/post-it
Copyright 2016-2017 Juliette Monsel <j_4321@protonmail.com>

My Notes is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

My Notes is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


Category Manager
"""

from tkinter import StringVar, PhotoImage, Toplevel
from mynoteslib.constantes import CONFIG, LANG, COLORS, INV_COLORS, IM_PLUS, IM_MOINS
from mynoteslib.constantes import save_config, fill, optionmenu_patch
from tkinter.ttk import Label, Button, OptionMenu, Style, Separator, Entry, Frame
from tkinter.messagebox import askyesnocancel

class CategoryManager(Frame):
    """ Category manager for the sticky notes """

    def __init__(self, master, app, **kwargs):
        Frame.__init__(self, master, **kwargs)
        self.columnconfigure(0, weight=1)

        self.app = app

        self.style = Style(self)
        self.style.theme_use("clam")

        self.im_plus = PhotoImage(file=IM_PLUS)
        self.im_moins = PhotoImage(file=IM_MOINS)

        ### Default category
        self.frame_def_cat = Frame(self)
        self.default_category = StringVar(self.frame_def_cat,
                                          CONFIG.get("General",
                                                     "default_category").capitalize())
        Label(self.frame_def_cat, text=_("Default category ")).grid(row=0, column=0,
                                                                sticky="e",
                                                                padx=(4, 0))
        self.categories = CONFIG.options("Categories")
        self.categories.sort()
        categories = [cat.capitalize() for cat in self.categories]
        self.def_cat_menu = OptionMenu(self.frame_def_cat, self.default_category,
                                       CONFIG.get("General",
                                                  "default_category").capitalize(),
                                       *categories)
        optionmenu_patch(self.def_cat_menu, self.default_category)
        self.def_cat_menu.grid(row=0, column=1, sticky="w", padx=4, pady=4)

        ### Category colors, names ...
        self.frame_cat = Frame(self)
        self.colors = list(COLORS.keys())
        self.colors.sort()
        self.images = []
        for key in self.colors:
            self.images.append(PhotoImage(key, master=self, width=16, height=16))
            fill(self.images[-1], COLORS[key])
        self.cat_colors = {}
        self.cat_labels = {}
        self.cat_menus = {}
        self.cat_buttons = {}
        for i,cat in enumerate(self.categories):
            self.cat_labels[cat] = Label(self.frame_cat, text="%s " % cat.capitalize())
            self.cat_labels[cat].grid(row=i+2, column=0, sticky="e")
            self.cat_colors[cat] = StringVar(self)
            color = CONFIG.get("Categories", cat)
            self.cat_menus[cat] = OptionMenu(self.frame_cat, self.cat_colors[cat],
                                             INV_COLORS[color], *self.colors,
                                             command=lambda color, c=cat: self.change_menubutton_color(color, c),
                                             style="%s.TMenubutton" % cat)
            optionmenu_patch(self.cat_menus[cat], self.cat_colors[cat])
            self.style.configure("%s.TMenubutton" % cat, background=color)
            self.cat_menus[cat].grid(row=i+2, column=1, sticky="w", padx=4, pady=4)
            self.cat_buttons[cat] = Button(self.frame_cat, image=self.im_moins,
                                           command=lambda c=cat: self.del_cat(c))
            self.cat_buttons[cat].grid(row=i+2, column=2, padx=4, pady=4)

        self.add_cat_button = Button(self.frame_cat, image=self.im_plus,
                                     command=self.add_cat)
        self.add_cat_button.grid(row=i+3, column=0, pady=(0,4))

        if len(self.categories) == 1:
            self.cat_buttons[self.categories[0]].configure(state="disabled")

        ### placement
        self.frame_def_cat.grid(row=0, column=0, sticky="eswn")
        Separator(self, orient="horizontal").grid(row=1, columnspan=3,
                                                  pady=10, sticky="ew")
        self.frame_cat.grid(row=2, column=0, sticky="eswn")

    def change_menubutton_color(self, color, cat):
        """ change the color of the menubutton of the category cat when its
            default color is changed """
        self.style.configure("%s.TMenubutton" % cat, background=COLORS[color])

    def del_cat(self, category):
        rep = askyesnocancel(_("Question"),
                             _("Do you want to delete all notes belonging to \
the category %(category)s? If you answer 'No', the category will be deleted but \
the notes will belong to the default category." % {"category": category}))
        if rep is not None:
            del(self.cat_colors[category])
            self.cat_buttons[category].grid_forget()
            del(self.cat_buttons[category])
            self.cat_labels[category].grid_forget()
            del(self.cat_labels[category])
            self.cat_menus[category].grid_forget()
            del(self.cat_menus[category])
            self.categories.remove(category)
            CONFIG.remove_option("Categories", category)
            if self.default_category.get().lower() == category:
                self.def_cat_menu.destroy()
                self.default_category.set(self.categories[0].capitalize())
                categories = [cat.capitalize() for cat in self.categories]
                self.def_cat_menu = OptionMenu(self.frame_def_cat, self.default_category,
                                               None, *categories)
                optionmenu_patch(self.def_cat_menu, self.default_category)
                self.def_cat_menu.grid(row=0, column=1, sticky="w", padx=4, pady=4)
            if len(self.categories) == 1:
                self.cat_buttons[self.categories[0]].configure(state="disabled")
            if rep:
                self.app.delete_cat(category)

    def add_cat(self):
        top = Toplevel(self)
        top.transient(self)
        top.grab_set()
        top.resizable(False, False)
        top.title(_("New Category"))

        def valide(event=None):
           cat = name.get().strip().lower()
           if cat and not cat in self.categories:
               i = self.add_cat_button.grid_info()['row']
               self.add_cat_button.grid_configure(row=i+1)
               self.cat_labels[cat] = Label(self.frame_cat,
                                            text="%s " % cat.capitalize())
               self.cat_labels[cat].grid(row=i, column=0, sticky="e")
               self.cat_colors[cat] = StringVar(self, _("Yellow"))
               self.cat_menus[cat] = OptionMenu(self.frame_cat, self.cat_colors[cat],
                                                 _("Yellow"), *self.colors,
                                                command=lambda color, c=cat: self.change_menubutton_color(color, c),
                                                style="%s.TMenubutton" % cat)
               self.style.configure("%s.TMenubutton" % cat, background=COLORS[_("Yellow")])
               optionmenu_patch(self.cat_menus[cat], self.cat_colors[cat])
               self.cat_menus[cat].grid(row=i, column=1, padx=4, pady=4)
               self.cat_buttons[cat] = Button(self.frame_cat, image=self.im_moins,
                                              command=lambda c=cat: self.del_cat(c))
               self.cat_buttons[cat].grid(row=i, column=2, padx=4, pady=4)
               self.cat_buttons[self.categories[0]].configure(state="normal")
               self.categories.append(cat)
               self.categories.sort()
               self.def_cat_menu.destroy()
               categories = [cat.capitalize() for cat in self.categories]
               self.def_cat_menu = OptionMenu(self.frame_def_cat, self.default_category,
                                              None, *categories)
               optionmenu_patch(self.def_cat_menu, self.default_category)
               self.def_cat_menu.grid(row=0, column=1, sticky="w", padx=4, pady=4)
               top.destroy()

        name = Entry(top, justify="center")
        name.grid(row=0, column=0, columnspan=2, sticky="ew")
        name.bind("<Return>", valide)
        name.focus_set()
        Button(top, text="Ok", command=valide).grid(row=1, column=0, sticky="nswe")
        Button(top, text=_("Cancel"),
               command=top.destroy).grid(row=1, column=1, sticky="nswe")