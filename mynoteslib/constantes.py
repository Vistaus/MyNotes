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


The icons are modified versions of icons from the elementary project
(the xfce fork to be precise https://github.com/shimmerproject/elementary-xfce)
Copyright 2007-2013 elementary LLC.

Constants and functions
"""


import os
import gettext
from configparser import ConfigParser
from locale import getdefaultlocale, setlocale, LC_ALL
from subprocess import check_output, CalledProcessError
import pkg_resources
from tkinter import Text


VERSION = pkg_resources.require("mynotes")[0].version

SYMBOLS = 'ΓΔΘΛΞΠΣΦΨΩαβγδεζηθικλμνξοπρςστυφχψωϐϑϒϕϖæœ«»¡¿£¥$€§ø∞∀∃∄∈∉∫∧∨∩∪÷±√∝∼≃≅≡≤≥≪≫≲≳▪•✭✦➔➢✔▴▸✗✚✳☎✉✎♫⚠⇒⇔'

# --- paths
PATH = os.path.dirname(__file__)

if os.access(PATH, os.W_OK) and os.path.exists(os.path.join(PATH, "images")):
    # the app is not installed
    # local directory containing config files and sticky notes data
    LOCAL_PATH = PATH
    PATH_LOCALE = os.path.join(PATH, "locale")
    PATH_IMAGES = os.path.join(PATH, "images")
    PATH_DATA_BACKUP = os.path.join(LOCAL_PATH, "backup", "notes.backup%i")
    PATH_DATA = os.path.join(LOCAL_PATH, "backup", "notes")
    if not os.path.exists(os.path.join(LOCAL_PATH, "backup")):
        os.mkdir(os.path.join(LOCAL_PATH, "backup"))
else:
    # local directory containing config files and sticky notes data
    LOCAL_PATH = os.path.join(os.path.expanduser("~"), ".mynotes")
    if not os.path.isdir(LOCAL_PATH):
        os.mkdir(LOCAL_PATH)
    PATH_LOCALE = "/usr/share/locale"
    PATH_IMAGES = "/usr/share/mynotes/images"
    PATH_DATA_BACKUP = os.path.join(LOCAL_PATH, "notes.backup%i")
    PATH_DATA = os.path.join(LOCAL_PATH, "notes")

PATH_CONFIG = os.path.join(LOCAL_PATH, "mynotes.ini")
PATH_LATEX = os.path.join(LOCAL_PATH, "latex")

if not os.path.exists(PATH_LATEX):
    os.mkdir(PATH_LATEX)


# --- images files
IM_ICON = os.path.join(PATH_IMAGES, "mynotes.png")
IM_ICON_24 = os.path.join(PATH_IMAGES, "mynotes24.png")
IM_ICON_48 = os.path.join(PATH_IMAGES, "mynotes48.png")
IM_CLOSE = os.path.join(PATH_IMAGES, "close.png")
IM_CLOSE_ACTIVE = os.path.join(PATH_IMAGES, "close_active.png")
IM_ROLL = os.path.join(PATH_IMAGES, "roll.png")
IM_ROLL_ACTIVE = os.path.join(PATH_IMAGES, "roll_active.png")
IM_LOCK = os.path.join(PATH_IMAGES, "verr.png")
IM_PLUS = os.path.join(PATH_IMAGES, "plus.png")
IM_MOINS = os.path.join(PATH_IMAGES, "moins.png")


# --- config file
CONFIG = ConfigParser()
if os.path.exists(PATH_CONFIG):
    CONFIG.read(PATH_CONFIG)
    LANGUE = CONFIG.get("General", "language")
    if not CONFIG.has_option("General", "position"):
        CONFIG.set("General", "position", "normal")
    if not CONFIG.has_option("General", "check_update"):
        CONFIG.set("General", "check_update", "True")
    if not CONFIG.has_option("General", "buttons_position"):
        CONFIG.set("General", "buttons_position", "right")
    if not CONFIG.has_option("General", "symbols"):
        CONFIG.set("General", "symbols", SYMBOLS)
else:
    LANGUE = ""
    CONFIG.add_section("General")
    CONFIG.set("General", "language", "en")
    CONFIG.set("General", "opacity", "82")
    CONFIG.set("General", "position", "normal")
    CONFIG.set("General", "buttons_position", "right")
    CONFIG.set("General", "check_update", "True")
    CONFIG.set("General", "symbols", SYMBOLS)
    CONFIG.add_section("Font")
    CONFIG.set("Font", "text_family", "TkDefaultFont")
    CONFIG.set("Font", "text_size", "12")
    CONFIG.set("Font", "title_family", "TkDefaultFont")
    CONFIG.set("Font", "title_size", "14")
    CONFIG.set("Font", "title_style", "bold")
    CONFIG.add_section("Categories")


# --- language
setlocale(LC_ALL, '')

APP_NAME = "MyNotes"

if LANGUE not in ["en", "fr"]:
    # Check the default locale
    lc = getdefaultlocale()[0][:2]
    if lc == "fr":
        # If we have a default, it's the first in the list
        LANGUE = "fr_FR"
    else:
        LANGUE = "en_US"
    CONFIG.set("General", "language", LANGUE[:2])

gettext.find(APP_NAME, PATH_LOCALE)
gettext.bind_textdomain_codeset(APP_NAME, "UTF-8")
gettext.bindtextdomain(APP_NAME, PATH_LOCALE)
gettext.textdomain(APP_NAME)
LANG = gettext.translation(APP_NAME, PATH_LOCALE,
                           languages=[LANGUE], fallback=True)
LANG.install()


# --- default categories
if not CONFIG.has_option("General", "default_category"):
    CONFIG.set("General", "default_category", _("home"))
    CONFIG.set("Categories", _("home"), '#F9F3A9')
    CONFIG.set("Categories", _("office"), '#A7B6D6')


# --- colors
COLORS = {_("Blue"): '#A7B6D6', _("Turquoise"): "#9FC9E2",
          _("Orange"): "#E1C59A", _("Red"): "#CD9293",
          _("Grey"): "#CECECE", _("White"): "#FFFFFF",
          _("Green"): '#C6FFB4', _("Black"): "#7D7A7A",
          _("Purple"): "#B592CD", _("Yellow"): '#F9F3A9',
          _("Dark Blue"): "#4D527D"}

INV_COLORS = {col: name for name, col in COLORS.items()}

TEXT_COLORS = {_("Black"): "black", _("White"): "white",
               _("Blue"): "blue", _("Green"): "green",
               _("Red"): "red", _("Yellow"): "yellow",
               _("Cyan"): "cyan", _("Magenta"): "magenta",
               _("Grey"): "grey", _("Orange"): "orange",
               }


# --- latex (optional):  insertion of latex formulas via matplotlib
try:
    from matplotlib import rc
    rc('text', usetex=True)
    from matplotlib.mathtext import MathTextParser
    from matplotlib.image import imsave
    parser = MathTextParser('bitmap')
    LATEX = True
except ImportError:
    LATEX = False


def math_to_image(latex, image_path, **options):
    img = parser.to_rgba(latex, **options)[0]
    imsave(image_path, img)


# --- filebrowser
ZENITY = False

paths = os.environ['PATH'].split(":")
for path in paths:
    if os.path.exists(os.path.join(path, "zenity")):
        ZENITY = True

try:
    import tkFileBrowser as tkfb
except ImportError:
    tkfb = False
    from tkinter import filedialog


def askopenfilename(defaultextension, filetypes, initialdir, initialfile="",
                    title=_('Open'), **options):
    """
    File browser:
        - defaultextension: extension added if none is given
        - initialdir: directory where the filebrowser is opened
        - filetypes: [('NOM', '*.ext'), ...]
    """
    if tkfb:
        return tkfb.askopenfilename(title=title,
                                    defaultext=defaultextension,
                                    filetypes=filetypes,
                                    initialdir=initialdir,
                                    initialfile=initialfile,
                                    **options)
    elif ZENITY:
        try:
            args = ["zenity", "--file-selection",
                    "--filename", os.path.join(initialdir, initialfile)]
            for ext in filetypes:
                args += ["--file-filter", "%s|%s" % ext]
            args += ["--title", title]
            file = check_output(args).decode("utf-8").strip()
            filename, ext = os.path.splitext(file)
            if not ext:
                ext = defaultextension
            return filename + ext
        except CalledProcessError:
            return ""
        except Exception:
            return filedialog.askopenfilename(title=title,
                                              defaultextension=defaultextension,
                                              filetypes=filetypes,
                                              initialdir=initialdir,
                                              initialfile=initialfile,
                                              **options)
    else:
        return filedialog.askopenfilename(title=title,
                                          defaultextension=defaultextension,
                                          filetypes=filetypes,
                                          initialdir=initialdir,
                                          initialfile=initialfile,
                                          **options)


def asksaveasfilename(defaultextension, filetypes, initialdir=".", initialfile="",
                      title=_('Save As'), **options):
    """
    plateform specific file browser for saving a file:
        - defaultextension: extension added if none is given
        - initialdir: directory where the filebrowser is opened
        - filetypes: [('NOM', '*.ext'), ...]
    """
    if tkfb:
        return tkfb.asksaveasfilename(title=title,
                                      defaultext=defaultextension,
                                      filetypes=filetypes,
                                      initialdir=initialdir,
                                      initialfile=initialfile,
                                      **options)
    elif ZENITY:
        try:
            args = ["zenity", "--file-selection",
                    "--filename", os.path.join(initialdir, initialfile),
                    "--save", "--confirm-overwrite"]
            for ext in filetypes:
                args += ["--file-filter", "%s|%s" % ext]
            args += ["--title", title]
            file = check_output(args).decode("utf-8").strip()
            if file:
                filename, ext = os.path.splitext(file)
                if not ext:
                    ext = defaultextension
                return filename + ext
            else:
                return ""
        except CalledProcessError:
            return ""
        except Exception:
            return filedialog.asksaveasfilename(title=title,
                                                defaultextension=defaultextension,
                                                initialdir=initialdir,
                                                filetypes=filetypes,
                                                initialfile=initialfile,
                                                **options)
    else:
        return filedialog.asksaveasfilename(title=title,
                                            defaultextension=defaultextension,
                                            initialdir=initialdir,
                                            filetypes=filetypes,
                                            initialfile=initialfile,
                                            **options)


# --- miscellaneous functions
def fill(image, color):
    """Fill image with a color=#hex."""
    width = image.width()
    height = image.height()
    horizontal_line = "{" + " ".join([color] * width) + "}"
    image.put(" ".join([horizontal_line] * height))


def sorting(index):
    """ sorting key for text indexes """
    line, char = index.split(".")
    return (int(line), int(char))


def save_config():
    """ sauvegarde du dictionnaire contenant la configuration du logiciel (langue ...) """
    with open(PATH_CONFIG, 'w') as fichier:
        CONFIG.write(fichier)


def backup(nb_backup=12):
    backups = [int(f.split(".")[-1][6:])
               for f in os.listdir(os.path.dirname(PATH_DATA_BACKUP))
               if f[:12] == "notes.backup"]
    if len(backups) < nb_backup:
        os.rename(PATH_DATA, PATH_DATA_BACKUP % len(backups))
    else:
        os.remove(PATH_DATA_BACKUP % 0)
        for i in range(1, len(backups)):
            os.rename(PATH_DATA_BACKUP % i, PATH_DATA_BACKUP % (i - 1))
        os.rename(PATH_DATA, PATH_DATA_BACKUP % (nb_backup - 1))


def optionmenu_patch(om, var):
    """ variable bug patch + bind menu so that it disapear easily """
    menu = om['menu']
    last = menu.index("end")
    for i in range(0, last + 1):
        menu.entryconfig(i, variable=var)
    menu.bind("<FocusOut>", menu.unpost())


def text_ranges(widget, tag, index1="1.0", index2="end"):
    r = [i.string for i in widget.tag_ranges(tag)]
    i1 = widget.index(index1)
    i2 = widget.index(index2)
    deb = r[::2]
    fin = r[1::2]
    i = 0
    while i < len(deb) and sorting(deb[i]) < sorting(i1):
        i += 1
    j = len(fin) - 1
    while j >= 0 and sorting(fin[j]) > sorting(i2):
        j -= 1
    tag_ranges = r[2 * i:2 * j + 2]
    if i > 0 and sorting(fin[i - 1]) > sorting(i1):
        tag_ranges.insert(0, fin[i - 1])
        tag_ranges.insert(0, i1)
    if j < len(fin) - 1 and sorting(deb[j + 1]) < sorting(i2):
        tag_ranges.append(deb[j + 1])
        tag_ranges.append(i2)

    return tag_ranges


# --- export
BALISES_OPEN = {"bold": "<b>",
                "italic": "<i>",
                "underline": "<u>",
                "overstrike": "<s>",
                "list": "",
                "enum": "",
                "link": "",
                "todolist": "",
                'center': '<div style="text-align:center">',
                'left': '',
                'right': '<div style="text-align:right">'}

BALISES_CLOSE = {"bold": "</b>",
                 "italic": "</i>",
                 "underline": "</u>",
                 "overstrike": "</s>",
                 "list": "",
                 "enum": "",
                 "todolist": "",
                 "link": "",
                 'center': '</div>',
                 'left': '',
                 'right': '</div>'}

for color in TEXT_COLORS.values():
    BALISES_OPEN[color] = '<span style="color:%s">' % color
    BALISES_CLOSE[color] = '</span>'


def note_to_html(data, master):
    txt = Text(master)
    tags = data["tags"]
    obj = data["inserted_objects"]
    indexes = list(obj.keys())
    indexes.sort(reverse=True, key=sorting)
    txt.insert('1.0', data["txt"])

    b_open = BALISES_OPEN.copy()
    b_close = BALISES_CLOSE.copy()

    for key, link in data["links"].items():
        b_open["link#%i" % key] = "<a href='%s'>" % link
        b_close["link#%i" % key] = "</a>"

    for key in data['tags']:
        if key not in b_open:
            b_open[key] = ''
            b_close[key] = ''

    for index in indexes:
        txt.insert(index, " ")
    # restore tags
    for tag in tags:
        indices = tags[tag]
        if indices:
            txt.tag_add(tag, *indices)
    end = int(txt.index("end").split(".")[0])
    for line in range(1, end):
        l_end = int(txt.index("%i.end" % line).split(".")[1])
        for col in range(l_end):
            index = "%i.%i" % (line, col)
            tags = set()
            for tag in txt.tag_names(index):
                if tag not in ["center", "left", "right"]:
                    txt.tag_remove(tag, index)
                    if "-" in tag:
                        t1, t2 = tag.split("-")
                        tags.add(t1)
                        tags.add(t2)
                    else:
                        tags.add(tag)
            tags = list(tags)
            tags.sort()
            txt.tag_add("-".join(tags), index)
    right = [i.string for i in txt.tag_ranges("right")]
    center = [i.string for i in txt.tag_ranges("center")]
    left = []
    for deb, fin in zip(right[::2], right[1::2]):
        left.append(txt.index("%s-1c" % deb))
        left.append(txt.index("%s+1c" % fin))
    for deb, fin in zip(center[::2], center[1::2]):
        left.append(txt.index("%s-1c" % deb))
        left.append(txt.index("%s+1c" % fin))
    left.sort(key=sorting)
    doubles = []
    for i in left[::2]:
        if i in left[1::2]:
            doubles.append(i)
    for i in doubles:
        left.remove(i)
        left.remove(i)
    if "1.0" in left:
        left.remove("1.0")
    else:
        left.insert(0, "1.0")
    if txt.index("end") in left:
        left.remove(txt.index("end"))
    else:
        left.append(txt.index("end"))
    # html balises
    t = txt.get("1.0", "end").splitlines()
    alignments = {"left": left, "right": right, "center": center}
    # alignment
    for a, align in alignments.items():
        for deb, fin in zip(align[::2], align[1::2]):
            balises = {deb: [b_open[a]], fin: [b_close[a]]}
            tags = {t: text_ranges(txt, t, deb, fin) for t in txt.tag_names()}
            for tag in tags:
                for o, c in zip(tags[tag][::2], tags[tag][1::2]):
                    if o not in balises:
                        balises[o] = []
                    if c not in balises:
                        balises[c] = []
                    l = tag.split("-")
                    while "" in l:
                        l.remove("")
                    ob = "".join([b_open[t] for t in l])
                    cb = "".join([b_close[t] for t in l[::-1]])
                    balises[o].append(ob)
                    balises[c].insert(0, cb)
            # --- checkboxes and images
            for i in indexes:
                if sorting(i) >= sorting(deb) and sorting(i) <= sorting(fin):
                    if i not in balises:
                        balises[i] = []
                    tp, val = obj[i]
                    if tp == "checkbox":
                        if val:
                            balises[i].append('<input type="checkbox" checked />')
                        else:
                            balises[i].append('<input type="checkbox" />')
                    elif tp == "image":
                        balises[i].append('<img src="%s" style="vertical-align:middle" alt="%s" />' % (val, os.path.split(val)[-1]))
            indices = list(balises.keys())
            indices.sort(key=sorting, reverse=True)
            for index in indices:
                line, col = index.split(".")
                line = int(line) - 1
                col = int(col)
                while line >= len(t):
                    t.append("")
                l = list(t[line])
                if index in indexes:
                    del(l[col])
                l.insert(col, "".join(balises[index]))
                t[line] = "".join(l)
    txt.destroy()

    # --- list
    if data["mode"] == "list":
        for i, line in enumerate(t):
            if "\t•\t" in line:
                t[i] = line.replace("\t•\t", "<li>") + "</li>"
        t = "<br>\n".join(t)
        t = "<ul>%s</ul>" % t
    else:
        t = "<br>\n".join(t)
    return t


def note_to_txt(data):
    """ .txt export"""
    t = data["txt"].splitlines()
    obj = data["inserted_objects"]
    indexes = list(obj.keys())
    indexes.sort(reverse=True, key=sorting)
    for i in indexes:
        tp, val = obj[i]
        line, col = i.split(".")
        line = int(line) - 1
        while line >= len(t):
            t.append("")
        col = int(col)
        l = list(t[line])
        if tp == "checkbox":
            if val:
                l.insert(col, "☒ ")
            else:
                l.insert(col, "☐ ")
        elif tp == "image":
            l.insert(col, "![%s](%s)" % (os.path.split(val)[-1], val))
        t[line] = "".join(l)
    return "\n".join(t)
