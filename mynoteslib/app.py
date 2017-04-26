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


Main class
"""

from tkinter import Tk, PhotoImage, Menu, Toplevel, TclError
from tkinter.ttk import Style, Label, Checkbutton, Button, Entry
import os, re, traceback
from shutil import copy
import pickle
from mynoteslib import tktray
from mynoteslib.constantes import CONFIG, PATH_DATA, PATH_DATA_BACKUP, LOCAL_PATH
from mynoteslib.constantes import backup, asksaveasfilename, askopenfilename
import mynoteslib.constantes as cst
from mynoteslib.config import Config
from mynoteslib.export import Export
from mynoteslib.sticky import Sticky
from mynoteslib.about import About
from mynoteslib.notemanager import Manager
from mynoteslib.version_check import UpdateChecker
from mynoteslib.messagebox import showerror, showinfo, askokcancel
import ewmh


class App(Tk):
    """ Main app: put an icon in the system tray with a right click menu to
        create notes ... """
    def __init__(self):
        Tk.__init__(self)
        self.withdraw()
        self.notes = {}
        self.img = PhotoImage(file=cst.IM_ICON)
        self.icon = PhotoImage(master=self, file=cst.IM_ICON_48)
        self.iconphoto(True, self.icon)

        self.ewmh = ewmh.EWMH()

        style = Style(self)
        style.theme_use("clam")

        self.close1 = PhotoImage("img_close", file=cst.IM_CLOSE)
        self.close2 = PhotoImage("img_closeactive", file=cst.IM_CLOSE_ACTIVE)
        self.roll1 = PhotoImage("img_roll", file=cst.IM_ROLL)
        self.roll2 = PhotoImage("img_rollactive", file=cst.IM_ROLL_ACTIVE)

        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.icon = tktray.Icon(self, docked=True)

        ### Menu
        self.menu_notes = Menu(self.icon.menu, tearoff=False)
        self.hidden_notes = {cat: {} for cat in CONFIG.options("Categories")}
        self.menu_show_cat = Menu(self.icon.menu, tearoff=False)
        self.menu_hide_cat = Menu(self.icon.menu, tearoff=False)
        self.icon.configure(image=self.img)
        self.icon.menu.add_command(label=_("New Note"), command=self.new)
        self.icon.menu.add_separator()
        self.icon.menu.add_command(label=_('Show All'),
                                   command=self.show_all)
        self.icon.menu.add_cascade(label=_('Show Category'),
                                   menu=self.menu_show_cat)
        self.icon.menu.add_cascade(label=_('Show Note'), menu=self.menu_notes,
                                   state="disabled")
        self.icon.menu.add_separator()
        self.icon.menu.add_command(label=_('Hide All'),
                                   command=self.hide_all)
        self.icon.menu.add_cascade(label=_('Hide Category'),
                                   menu=self.menu_hide_cat)
        self.icon.menu.add_separator()
        self.icon.menu.add_command(label=_("Preferences"),
                                   command=self.config)
        self.icon.menu.add_command(label=_("Note Manager"), command=self.manage)
        self.icon.menu.add_separator()
        self.icon.menu.add_command(label=_("Backup Notes"), command=self.backup)
        self.icon.menu.add_command(label=_("Restore Backup"), command=self.restore)
        self.icon.menu.add_separator()
        self.icon.menu.add_command(label=_("Export"), command=self.export_notes)
        self.icon.menu.add_command(label=_("Import"), command=self.import_notes)
        self.icon.menu.add_separator()
        self.icon.menu.add_command(label=_('Check for Updates'),
                                   command=lambda: UpdateChecker(self))
        self.icon.menu.add_command(label=_('About'), command=lambda: About(self))
        self.icon.menu.add_command(label=_('Quit'), command=self.quit)

        ### Restore notes
        self.note_data = {}
        if os.path.exists(PATH_DATA):
            with open(PATH_DATA, "rb") as fich:
                dp = pickle.Unpickler(fich)
                note_data = dp.load()
                for i, key in enumerate(note_data):
                    self.note_data["%i" % i] = note_data[key]
            backup()
            for key in self.note_data:
                data = self.note_data[key]
                cat = data["category"]
                if not CONFIG.has_option("Categories", cat):
                    CONFIG.set("Categories", cat, data["color"])
                if data["visible"]:
                    self.notes[key] = Sticky(self, key, **data)
                else:
                    self.add_note_to_menu(key, data["title"], cat)
        self.nb = len(self.note_data)
        self.update_menu()
        self.update_notes()
        self.make_notes_sticky()

        ### class bindings
#        # newline depending on mode
#        self.bind_class("Text", "<Return>",  self.insert_newline)
#        # char deletion taking into account list type
#        self.bind_class("Text", "<BackSpace>",  self.delete_char)
        # change Ctrl+A to select all instead of go to the beginning of the line
        self.bind_class('Text', '<Control-a>', self.select_all_text)
        self.bind_class('TEntry', '<Control-a>', self.select_all_entry)
        # unbind Ctrl+I and Ctrl+B
        self.bind_class('Text', '<Control-i>', lambda e: None)
        self.bind_class('Text', '<Control-b>', lambda e: None)
        self.bind_class('Text', '<Control-y>', lambda e: None)
        self.bind_class("Text", "<Control-z>", lambda e: None)
        self.bind_class("Text", "<Control-Lock-Y>", lambda e: None)
        # highlight checkboxes when inside text selection
        self.bind_class("Text", "<ButtonPress-1>", self.highlight_checkboxes, True)
        self.bind_class("Text", "<ButtonRelease-1>", self.highlight_checkboxes, True)
        self.bind_class("Text", "<B1-Motion>", self.highlight_checkboxes, True)
        evs = ['<<SelectAll>>', '<<SelectLineEnd>>', '<<SelectLineStart>>',
               '<<SelectNextChar>>', '<<SelectNextLine>>', '<<SelectNextPara>>',
               '<<SelectNextWord>>', '<<SelectNone>>', '<<SelectPrevChar>>',
               '<<SelectPrevLine>>','<<SelectPrevPara>>','<<SelectPrevWord>>']
        for ev in evs:
            self.bind_class("Text", ev, self.highlight_checkboxes, True)

        # check for updates
        if CONFIG.getboolean("General", "check_update"):
            UpdateChecker(self)

    ### class bindings methods
    def highlight_checkboxes(self, event):
        txt = event.widget
        try:
            deb = cst.sorting(txt.index("sel.first"))
            fin = cst.sorting(txt.index("sel.last"))
            for ch in txt.children.values():
                try:
                    i = cst.sorting(txt.index(ch))
                    if i >= deb and i <= fin:
                        ch.configure(style="sel.TCheckbutton")
                    else:
                        ch.configure(style=txt.master.id + ".TCheckbutton")
                except TclError:
                    pass
        except TclError:
            for ch in txt.children.values():
                try:
                    i = cst.sorting(txt.index(ch))
                    ch.configure(style=txt.master.id + ".TCheckbutton")
                except TclError:
                    pass

    def select_all_entry(self, event):
        event.widget.selection_range(0, "end")

    def select_all_text(self, event):
        event.widget.tag_add("sel", "1.0", "end-1c")
        self.highlight_checkboxes(event)

#    def delete_char(self, event):
#        txt = event.widget
#        deb_line = txt.get("insert linestart", "insert")
#        tags = txt.tag_names("insert")
#        if txt.tag_ranges("sel"):
#            if txt.tag_nextrange("enum", "sel.first", "sel.last"):
#                update = True
#            else:
#                update = False
#            txt.delete("sel.first", "sel.last")
#            if update:
#                txt.master.update_enum()
#        elif txt.index("insert") != "1.0":
#            if re.match('^\t[0-9]+\.\t$', deb_line) and 'enum' in tags:
#                txt.delete("insert linestart", "insert")
#                txt.insert("insert", "\t\t")
#                txt.master.update_enum()
#            elif deb_line == "\t•\t" and 'list' in tags:
#                txt.delete("insert linestart", "insert")
#                txt.insert("insert", "\t\t")
#            elif deb_line == "\t\t":
#                txt.delete("insert linestart", "insert")
#            elif "todolist" in tags and txt.index("insert") == txt.index("insert linestart+1c"):
#                try:
#                    ch = txt.window_cget("insert-1c", "window")
#                    txt.delete("insert-1c")
#                    txt.children[ch.split('.')[-1]].destroy()
#                    txt.insert("insert", "\t\t")
#                except TclError:
#                    txt.delete("insert-1c")
#            else:
#                txt.delete("insert-1c")
#
#    def insert_newline(self, event):
#        mode = event.widget.master.mode.get()
#        if mode == "list":
#            event.widget.insert("insert", "\n\t•\t")
#            event.widget.tag_add("list", "1.0", "end")
#        elif mode == "todolist":
#            event.widget.insert("insert", "\n")
#            ch = Checkbutton(event.widget, takefocus=False,
#                             style=event.widget.master.id + ".TCheckbutton")
#            event.widget.window_create("insert", window=ch)
#            event.widget.tag_add("todolist", "1.0", "end")
#        elif mode == "enum":
##            event.widget.configure(autoseparators=False)
##            event.widget.edit_separator()
#            event.widget.insert("insert", "\n\t0.\t")
#            event.widget.master.update_enum()
##            event.widget.edit_separator()
#            event.widget.configure(autoseparators=True)
#        else:
#            event.widget.insert("insert", "\n")

    def make_notes_sticky(self):
        for w in self.ewmh.getClientList():
            if w.get_wm_name()[:7] == 'mynotes':
                self.ewmh.setWmState(w, 1, '_NET_WM_STATE_STICKY')
        self.ewmh.display.flush()

    def add_note_to_menu(self, nb, note_title, category):
        """ add note to 'show notes' menu. """

        try:
            name = self.menu_notes.entrycget(category.capitalize(), 'menu')
            if not isinstance(name, str):
                name = str(name)
            menu = self.menu_notes.children[name.split('.')[-1]]
            end = menu.index("end")
            if end is not None:
                # le menu n'est pas vide
                titles = self.hidden_notes[category].values()
                titles = [t for t in titles if t.split(" ~#")[0] == note_title]
                if titles:
                    title = "%s ~#%i" % (note_title, len(titles) + 1)
                else:
                    title = note_title
            else:
                title = note_title
        except TclError:
            # cat is not in the menu
            menu = Menu(self.menu_notes, tearoff=False)
            self.menu_notes.add_cascade(label=category.capitalize(), menu=menu)
            title = note_title
        menu.add_command(label=title, command=lambda: self.show_note(nb))
        self.icon.menu.entryconfigure(4, state="normal")
        self.hidden_notes[category][nb] = title

    def backup(self):
        """ create a backup at the location indicated by user """
        initialdir, initialfile = os.path.split(PATH_DATA_BACKUP % 0)
        fichier = asksaveasfilename(defaultextension=".backup",
                                    filetypes=[],
                                    initialdir=initialdir,
                                    initialfile="notes.backup0",
                                    title=_('Backup Notes'))
        if fichier:
            try:
                with open(fichier, "wb") as fich:
                    dp = pickle.Pickler(fich)
                    dp.dump(self.note_data)
            except Exception as e:
                report_msg = e.strerror != 'Permission denied'
                showerror(_("Error"), _("Backup failed."),
                          traceback.format_exc(), report_msg)

    def restore(self, fichier=None, confirmation=True):
        """ restore notes from backup """
        if confirmation:
            rep = askokcancel(_("Warning"),
                              _("Restoring a backup will erase the current notes."),
                              icon="warning")
        else:
            rep = True
        if rep:
            if fichier is None:
                fichier = askopenfilename(defaultextension=".backup",
                                          filetypes=[],
                                          initialdir=LOCAL_PATH,
                                          initialfile="",
                                          title=_('Restore Backup'))
            if fichier:
                try:
                    keys = list(self.note_data.keys())
                    for key in keys:
                        self.delete_note(key)
                    if not os.path.samefile(fichier, PATH_DATA):
                        copy(fichier, PATH_DATA)
                    with open(PATH_DATA, "rb") as myfich:
                        dp = pickle.Unpickler(myfich)
                        note_data = dp.load()
                    for i, key in enumerate(note_data):
                        data = note_data[key]
                        note_id = "%i" % i
                        self.note_data[note_id] = data
                        cat = data["category"]
                        if not CONFIG.has_option("Categories", cat):
                            CONFIG.set("Categories", cat, data["color"])
                        if data["visible"]:
                            self.notes[note_id] = Sticky(self, note_id, **data)
                    self.nb = len(self.note_data)
                    self.update_menu()
                    self.update_notes()
                except FileNotFoundError:
                    showerror(_("Error"), _("The file {filename} does not exists.").format(filename=fichier))
                except Exception as e:
                    showerror(_("Error"), str(e), traceback.format_exc(), True)

    def show_all(self):
        """ Show all notes """
        for cat in self.hidden_notes.keys():
            keys = list(self.hidden_notes[cat].keys())
            for key in keys:
                self.show_note(key)

    def show_cat(self, category):
        """ Show all notes belonging to category """
        keys = list(self.hidden_notes[category].keys())
        for key in keys:
            self.show_note(key)

    def hide_all(self):
        """ Hide all notes """
        keys = list(self.notes.keys())
        for key in keys:
            self.notes[key].hide()

    def hide_cat(self, category):
        """ Hide all notes belonging to category """
        keys = list(self.notes.keys())
        for key in keys:
            if self.note_data[key]["category"] == category:
                self.notes[key].hide()

    def manage(self):
        """ Launch note manager """
        Manager(self)

    def config(self):
        """ Launch the setting manager """
        conf = Config(self)
        self.wait_window(conf)
        col_changes, name_changes = conf.get_changes()
        if col_changes or name_changes:
            self.update_notes(col_changes, name_changes)
            self.update_menu()
            alpha = CONFIG.getint("General", "opacity")/100
            for note in self.notes.values():
                note.attributes("-alpha", alpha)
                note.update_title_font()
                note.update_text_font()
                note.update_titlebar()

    def delete_cat(self, category):
        """ Delete all notes belonging to category """
        keys = list(self.notes.keys())
        for key in keys:
            if self.note_data[key]["category"] == category:
                self.notes[key].delete(confirmation=False)

    def delete_note(self, nb):
        if self.note_data[nb]["visible"]:
            self.notes[nb].delete(confirmation=False)
        else:
            cat = self.note_data[nb]["category"]
            name = self.menu_notes.entrycget(cat.capitalize(), 'menu')
            if not isinstance(name, str):
                name = str(name)
            menu = self.menu_notes.children[name.split('.')[-1]]
            index = menu.index(self.hidden_notes[cat][nb])
            menu.delete(index)
            if menu.index("end") is None:
                # the menu is empty
                self.menu_notes.delete(cat.capitalize())
                if self.menu_notes.index('end') is None:
                   self.icon.menu.entryconfigure(4, state="disabled")
            del(self.hidden_notes[cat][nb])
            del(self.note_data[nb])
            self.save()

    def show_note(self, nb):
        """ Display the note corresponding to the 'nb' key in self.note_data """
        self.note_data[nb]["visible"] = True
        cat = self.note_data[nb]["category"]
        name = self.menu_notes.entrycget(cat.capitalize(), 'menu')
        if not isinstance(name, str):
            name = str(name)
        menu = self.menu_notes.children[name.split('.')[-1]]
        index = menu.index(self.hidden_notes[cat][nb])
        del(self.hidden_notes[cat][nb])
        self.notes[nb] = Sticky(self, nb, **self.note_data[nb])
        menu.delete(index)
        if menu.index("end") is None:
            # the menu is empty
            self.menu_notes.delete(cat.capitalize())
            if self.menu_notes.index('end') is None:
               self.icon.menu.entryconfigure(4, state="disabled")
        self.make_notes_sticky()

    def update_notes(self, col_changes={}, name_changes={}):
        """ Update the notes after changes in the categories """
        categories = CONFIG.options("Categories")
        categories.sort()
        self.menu_notes.delete(0, "end")
        self.hidden_notes = {cat: {} for cat in categories}
        for key in self.note_data:
            cat = self.note_data[key]["category"]
            if cat in name_changes:
                cat = name_changes[cat]
                self.note_data[key]["category"] = cat
                if self.note_data[key]["visible"]:
                    self.notes[key].change_category(cat)
            elif not cat in categories:
                default = CONFIG.get("General", "default_category")
                default_color = CONFIG.get("Categories", default)
                if self.note_data[key]["visible"]:
                    self.notes[key].change_category(default)
                self.note_data[key]["category"] = default
                self.note_data[key]["color"] = default_color
                cat = default
            if cat in col_changes:
                old_color, new_color = col_changes[cat]
                if self.note_data[key]["color"] == old_color:
                    self.note_data[key]["color"] = new_color
                    if self.note_data[key]["visible"]:
                        self.notes[key].change_color(cst.INV_COLORS[new_color])
            if not self.note_data[key]['visible']:
                self.add_note_to_menu(key, self.note_data[key]["title"],
                                      self.note_data[key]['category'])
            else:
                self.notes[key].update_menu_cat(categories)
        self.save()
        if self.menu_notes.index("end")is not None:
            self.icon.menu.entryconfigure(4, state="normal")
        else:
            self.icon.menu.entryconfigure(4, state="disabled")

    def update_menu(self):
        """ Populate self.menu_show_cat and self.menu_hide_cat with the categories """
        self.menu_hide_cat.delete(0, "end")
        self.menu_show_cat.delete(0, "end")
        categories = CONFIG.options("Categories")
        categories.sort()
        for cat in categories:
            self.menu_show_cat.add_command(label=cat.capitalize(),
                                           command=lambda c=cat: self.show_cat(c))
            self.menu_hide_cat.add_command(label=cat.capitalize(),
                                           command=lambda c=cat: self.hide_cat(c))

    def save(self):
        """ Save the data """
        with open(PATH_DATA, "wb") as fich:
            dp = pickle.Pickler(fich)
            dp.dump(self.note_data)

    def new(self):
        """ Create a new note """
        key = "%i" % self.nb
        self.notes[key] = Sticky(self, key)
        data = self.notes[key].save_info()
        data["visible"] = True
        self.note_data[key] = data
        self.nb += 1
        self.make_notes_sticky()

    def export_notes(self):
        export = Export(self)
        self.wait_window(export)
        categories_to_export, only_visible = export.get_export()
        if categories_to_export:
            initialdir, initialfile = os.path.split(PATH_DATA_BACKUP % 0)
            fichier = asksaveasfilename(defaultextension=".html",
                                        filetypes=[(_("HTML file (.html)"), "*.html"),
                                                   (_("Text file (.txt)"), "*.txt"),
                                                   (_("All files"), "*")],
                                        initialdir=initialdir,
                                        initialfile="",
                                        title=_('Export Notes As'))
            if fichier:
                try:
                    if os.path.splitext(fichier)[-1] == ".html":
        ### html export
                        cats = {cat: [] for cat in categories_to_export}
                        for key in self.note_data:
                            cat = self.note_data[key]["category"]
                            if cat in cats and ((not only_visible) or self.note_data[key]["visible"]):
                                cats[cat].append((self.note_data[key]["title"],
                                                  cst.note_to_html(self.note_data[key], self)))
                        text = ""
                        for cat in cats:
                            cat_txt = "<h1 style='text-align:center'>" + _("Category: {category}").format(category=cat) + "<h1/>\n"
                            text += cat_txt
                            text += "<br>"
                            for title, txt in cats[cat]:
                                text += "<h2 style='text-align:center'>%s</h2>\n" % title
                                text += txt
                                text += "<br>\n"
                                text += "<hr />"
                                text += "<br>\n"
                            text += '<hr style="height: 8px;background-color:grey" />'
                            text += "<br>\n"
                        with open(fichier, "w") as fich:
                            fich.write('<body style="max-width:30em">\n')
                            fich.write(text.encode('ascii', 'xmlcharrefreplace').decode("utf-8"))
                            fich.write("\n</body>")
#                if os.path.splitext(fichier)[-1] == ".txt":
                    else:
        ### txt export
                        # export notes to .txt: all formatting is lost
                        cats = {cat: [] for cat in categories_to_export}
                        for key in self.note_data:
                            cat = self.note_data[key]["category"]
                            if cat in cats and ((not only_visible) or self.note_data[key]["visible"]):
                                cats[cat].append((self.note_data[key]["title"],
                                                  cst.note_to_txt(self.note_data[key])))
                        text = ""
                        for cat in cats:
                            cat_txt = _("Category: {category}").format(category=cat) + "\n"
                            text += cat_txt
                            text += "="*len(cat_txt)
                            text += "\n\n"
                            for title, txt in cats[cat]:
                                text += title
                                text += "\n"
                                text += "-"*len(title)
                                text += "\n\n"
                                text += txt
                                text += "\n\n"
                                text += "-"*30
                                text += "\n\n"
                            text += "#"*30
                            text += "\n\n"
                        with open(fichier, "w") as fich:
                            fich.write(text)


#                    else:
#        ### pickle export
#                        note_data = {}
#                        for key in self.note_data:
#                            if self.note_data[key]["category"] in categories_to_export:
#                                if (not only_visible) or self.note_data[key]["visible"]:
#                                    note_data[key] = self.note_data[key]
#
#                        with open(fichier, "wb") as fich:
#                            dp = pickle.Pickler(fich)
#                            dp.dump(note_data)
                except Exception as e:
                    report_msg = e.strerror != 'Permission denied'
                    showerror(_("Error"), str(e), traceback.format_exc(),
                              report_msg)

    def import_notes(self):
        fichier = askopenfilename(defaultextension=".backup",
                                  filetypes=[(_("Notes (.notes)"), "*.notes"),
                                             (_("All files"), "*")],
                                  initialdir=LOCAL_PATH,
                                  initialfile="",
                                  title=_('Import'))
        if fichier:
            try:
                with open(fichier, "rb") as fich:
                    dp = pickle.Unpickler(fich)
                    note_data = dp.load()
                for i, key in enumerate(note_data):
                    data = note_data[key]
                    note_id = "%i" % (i + self.nb)
                    self.note_data[note_id] = data
                    cat = data["category"]
                    if not CONFIG.has_option("Categories", cat):
                        CONFIG.set("Categories", cat, data["color"])
                        self.hidden_notes[cat] = {}
                    if data["visible"]:
                        self.notes[note_id] = Sticky(self, note_id, **data)
                self.nb = int(max(self.note_data.keys(), key=lambda x: int(x))) + 1
                self.update_menu()
                self.update_notes()
            except Exception:
                message = _("The file {file} is not a valid .notes file.").format(file=fichier)
                showerror(_("Error"), message, traceback.format_exc())

    def cleanup(self):
        """ Remove unused latex images """
        img_stored = os.listdir(cst.PATH_LATEX)
        img_used = []
        for data in self.note_data.values():
            img_used.extend(list(data.get("latex", {}).keys()))
        for img in img_stored:
            if not img in img_used:
                os.remove(os.path.join(cst.PATH_LATEX, img))

    def quit(self):
        self.destroy()
