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


Dialog to delete notes
"""


from tkinter import Toplevel, PhotoImage, Text
from tkinter.ttk import Label, Frame, Button, Notebook
from mynoteslib.constantes import CONFIG, IM_MOINS
from mynoteslib.autoscrollbar import AutoScrollbar as Scrollbar

class Deleter(Toplevel):
    """ Note manager """
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.title(_("Delete"))
#        self.resizable(False, False)
        self.grab_set()
#        self.columnconfigure(0, weight=1)
        categories = CONFIG.options("Categories")
        categories.sort()

        self.im_moins = PhotoImage(file=IM_MOINS, master=self)

        notebook = Notebook(self)
        notebook.pack(fill='both', expand=True)

        self.texts = {}
        self.frames = {}
        self.notes = {}
        for cat in categories:
            frame = Frame(notebook)
            self.texts[cat] = Text(frame, width=1, height=1, bg=self.cget('bg'),
                                   relief='flat', highlightthickness=0,
                                   padx=4, pady=4, cursor='arrow')
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)

            self.texts[cat].grid(row=0, column=0, sticky='ewsn', padx=(0,2))
            scrolly = Scrollbar(frame, orient='vertical',
                                command=self.texts[cat].yview)
            scrolly.grid(row=0, column=1, sticky='ns')
            scrollx = Scrollbar(frame, orient='horizontal',
                                command=self.texts[cat].xview)
            scrollx.grid(row=1, column=0, sticky='ew')
            self.texts[cat].configure(xscrollcommand=scrollx.set,
                                      yscrollcommand=scrolly.set)
            self.frames[cat] = Frame(self.texts[cat])
            self.frames[cat].columnconfigure(0, weight=1, minsize=170)
            self.frames[cat].columnconfigure(1, weight=1, minsize=170)
            self.frames[cat].columnconfigure(2, minsize=20)
            self.texts[cat].window_create('1.0', window=self.frames[cat])

            notebook.add(frame, text=cat.capitalize(), sticky="ewsn",
                         padding=0)
        for key, note_data in self.master.note_data.items():
            cat = note_data["category"]
            c, r = self.frames[cat].grid_size()
            self.notes[key] = []
            title = note_data['title'][:20]
            title = title.replace('\t', ' ') + ' '*(20 - len(title))
            self.notes[key].append(Label(self.frames[cat], text=title,
                                         font='TkDefaultFont 10 bold'))
            txt = note_data['txt'].splitlines()
            if txt:
                txt = txt[0][:17] + '...'
            else:
                txt = ''
            txt = txt.replace('\t', ' ') + ' '*(20 - len(txt))
            self.notes[key].append(Label(self.frames[cat], text=txt))
            self.notes[key].append(Button(self.frames[cat], image=self.im_moins,
                                          command=lambda iid=key: self.delete_note(iid)))
            for i, widget in enumerate(self.notes[key]):
                widget.grid(row=r, column=i, sticky='w', padx=4, pady=4)
        for txt in self.texts.values():
            txt.configure(state='disabled')
        self.geometry('410x450')

    def delete_note(self, note_id):
#        cat = self.master.note_data[note_id]['category']
#        self.texts[cat].configure(state='normal')
        self.master.delete_note(note_id)
        for widget in self.notes[note_id]:
            widget.destroy()
#        self.texts[cat].configure(state='disabled')
