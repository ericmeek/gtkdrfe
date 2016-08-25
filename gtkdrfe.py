#!/usr/bin/python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Pango, Gdk, GObject
import telnetlib
import sys
import re


class MyWindow(Gtk.Window):
    def __init__(self):
        self.CTRL_ON = False
        self.SHIFT_ON = False
        self.ALT_ON = False
        self.rtmax = 0
        self.rtcounter = 0
        self.spmax = 0
        self.spcounter = 0
        self.currenttime = 0
        self.server_time = 0
        self.ICON_HIDDEN = 1001
        self.statusgrid = None
        self.blankimg = None
        self.hideimg = None
        self.posimg = None
        self.invstream = []
        self.stream = False

        Gtk.Window.__init__(self, title="ListBox Demo")

        self.resize( 640, 480)

        mainwindow = self.setup_mainwindow()
        self.add(mainwindow)
        self.show_all()

        self.unmatched = open("/home/eric/Documents/drunmatched.txt", "w")
        self.matched = open("/home/eric/Documents/drmatched.txt", "w")

        self.tn = telnetlib.Telnet('localhost', 8000)
        GLib.io_add_watch(self.tn.fileno(), GLib.IO_IN|GLib.IO_PRI|GLib.IO_ERR|GLib.IO_HUP, self.read_input)

        self.count = 0

        self.connect("key-press-event", self.on_key_press)
        self.connect("key-release-event", self.on_key_release)

        GObject.timeout_add_seconds(1, self.server_tick, None)

    def do_macro(self, macro):
        print("Doing Macro: {}".format(macro))
        self.textbuffer2.insert(self.textbuffer2.get_end_iter(), "{}\n".format(macro))
        self.tn.write("{}\n".format(macro))     

    def on_key_press(self, widget, ev, data=None):
        print("Key: {}".format(ev.keyval))

        SPECIAL_KEYS = [Gdk.KEY_semicolon, Gdk.KEY_slash, Gdk.KEY_comma]

        macros_ctrl = {Gdk.KEY_o:"north",
                       Gdk.KEY_l:"south",
                       Gdk.KEY_semicolon:"east",
                       Gdk.KEY_k:"west",
                       Gdk.KEY_slash:"southeast",
                       Gdk.KEY_comma:"southwest",
                       Gdk.KEY_p:"northeast",
                       Gdk.KEY_i:"northwest"}

        if ev.keyval == Gdk.KEY_Control_L:
            self.CTRL_ON = True
        elif ev.keyval == Gdk.KEY_Alt_L:
            self.ALT_ON = True
        elif ev.keyval == Gdk.KEY_Shift_L:
            self.SHIFT_ON = True
        elif ev.keyval in range(Gdk.KEY_A,Gdk.KEY_Z+1) or ev.keyval in range(Gdk.KEY_a,Gdk.KEY_z+1) or ev.keyval in SPECIAL_KEYS:
            ## Ctrl
            if self.CTRL_ON and not self.SHIFT_ON and not self.ALT_ON:
                if ev.keyval in macros_ctrl:
                    self.do_macro(macros_ctrl[ev.keyval])
                print("Ctrl + {}".format(ev.keyval))
            ## Alt
            if not self.CTRL_ON and not self.SHIFT_ON and self.ALT_ON:
                print("Alt + {}".format(ev.keyval))
            ## Ctrl Shift
            if self.CTRL_ON and self.SHIFT_ON and not self.ALT_ON:
                print("Ctrl Shift + {}".format(ev.keyval))
            ## Ctrl Alt
            if self.CTRL_ON and not self.SHIFT_ON and self.ALT_ON:
                print("Ctrl Alt + {}".format(ev.keyval))
            ## Alt Shift
            if not self.CTRL_ON and self.SHIFT_ON and self.ALT_ON:
                print("Alt Shift + {}".format(ev.keyval))
            ## Ctrl Shift Alt
            if self.CTRL_ON and self.SHIFT_ON and self.ALT_ON:
                print("Ctrl Alt Shift + {}".format(ev.keyval))

    def on_key_release(self, widget, ev, data=None):
        # Left-Ctrl 65507
        # Right-Ctrl 65508
        # Left-Alt 65513
        # Right-Alt 65514
        # Left-Shift 65505
        # Right-Shift 65506
        # Super 65515
        if ev.keyval == Gdk.KEY_Control_L:
            self.CTRL_ON = False
        elif ev.keyval == Gdk.KEY_Alt_L:
            self.ALT_ON = False
        elif ev.keyval == Gdk.KEY_Shift_L:
            self.SHIFT_ON = False

    def send_macro(self, macro):
        self.tn.write("{}\n".format(macro))

    def setup_headerbar(self):
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(False)
        hb.props.title = "Lukrani"
        imgleft = Gtk.Image.new_from_file("images/lefthand.png")
        imgright = Gtk.Image.new_from_file("images/righthand.png")
        imgwand = Gtk.Image.new_from_file("images/wand.png")
        self.lbllefthand = Gtk.Label("Empty", xalign=0)
        self.lblrighthand = Gtk.Label("Empty", xalign=0)
        self.lblspell = Gtk.Label("None", xalign=0)

        btn1 = Gtk.Button(label="Macro Set")
        btn2 = Gtk.Button(label="Options")
        hb.pack_start(imgleft)
        hb.pack_start(self.lbllefthand)
        hb.pack_start(imgright)
        hb.pack_start(self.lblrighthand)
        hb.pack_start(imgwand)
        hb.pack_start(self.lblspell)
        hb.pack_end(btn1)
        hb.pack_end(btn2)
        return hb

    def setup_topwindow(self):
        subbox = Gtk.HBox(spacing=6)        

        thoughtwindow = Gtk.ScrolledWindow()
        thoughtwindow.set_hexpand(True)
        thoughtwindow.set_vexpand(True)
        thoughtview = Gtk.TextView()
        thoughtview.set_editable(False)
        thoughtview.set_cursor_visible(False)
        thoughtview.set_wrap_mode(Gtk.WrapMode.WORD)
        thoughtbuffer = thoughtview.get_buffer()
        thoughtbuffer.set_text("This is the thought window")
        thoughtwindow.add(thoughtview)

        roomwindow = Gtk.ScrolledWindow()
        roomwindow.set_hexpand(True)
        roomwindow.set_vexpand(True)
        roomview = Gtk.TextView()
        roomview.set_editable(False)
        roomview.set_cursor_visible(False)
        roomview.set_wrap_mode(Gtk.WrapMode.WORD)
        roombuffer = roomview.get_buffer()
        roombuffer.set_text("This is the room window\n")
        roomwindow.add(roomview)

        subbox.pack_start(thoughtwindow, True, True, 0)
        subbox.pack_start(roomwindow, True, True, 0)
        return subbox

    def setup_bottomwindow(self):
        storybox = Gtk.Box(spacing=6)
        scrolledwindow2 = Gtk.ScrolledWindow()
        scrolledwindow2.set_hexpand(True)
        scrolledwindow2.set_vexpand(True)
        scrolledwindow2.connect('size-allocate', self.scrolledwindow2_changed)

        storybox.pack_start(scrolledwindow2, True, True, 0)
        textview2 = Gtk.TextView()
        textview2.set_editable(False)
        textview2.set_cursor_visible(False)
        textview2.set_wrap_mode(Gtk.WrapMode.WORD)
        textview2.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0,0,0))
        textview2.modify_fg(Gtk.StateType.NORMAL, Gdk.Color(65535,65535,65535))
        self.textbuffer2 = textview2.get_buffer()
        self.textbuffer2.set_text("This is the story window\n")
        scrolledwindow2.add(textview2)
        return storybox

    def setup_entrybox(self):
        entrybox = Gtk.Box(spacing=6)
        stancelbl = Gtk.Label("S", xalign=0)
        bleedlbl = Gtk.Label("N", xalign=0)
        stunlbl = Gtk.Label("N", xalign=0)

        self.statusgrid = Gtk.Grid()
        self.blankimg = Gtk.Image.new_from_file("images/blank.xpm")
        self.hideimg = Gtk.Image.new_from_file("images/blank.xpm")
        self.posimg = Gtk.Image.new_from_file("images/stand.xpm")
        self.statusgrid.add(self.posimg)
        self.statusgrid.attach_next_to(self.hideimg, self.posimg, Gtk.PositionType.LEFT, 1, 1)

        dirgrid = Gtk.Grid()
        self.dirnorth = Gtk.Image.new_from_file("images/north.xpm")
        self.dirsouth = Gtk.Image.new_from_file("images/south.xpm")
        self.direast = Gtk.Image.new_from_file("images/east.xpm")
        self.dirwest = Gtk.Image.new_from_file("images/west.xpm")
        self.dirnortheast = Gtk.Image.new_from_file("images/northeast.xpm")
        self.dirsoutheast = Gtk.Image.new_from_file("images/southeast.xpm")
        self.dirnorthwest = Gtk.Image.new_from_file("images/northwest.xpm")
        self.dirsouthwest = Gtk.Image.new_from_file("images/southwest.xpm")
        self.dirup = Gtk.Image.new_from_file("images/up.xpm")
        self.dirdown = Gtk.Image.new_from_file("images/down.xpm")
        self.dirout = Gtk.Image.new_from_file("images/out.xpm")
        self.compassdict= {"north": self.dirnorth, "south": self.dirsouth, "east": self.direast,
                       "west": self.dirwest, "northeast": self.dirnortheast, "southeast": self.dirsoutheast,
                       "northwest": self.dirnorthwest, "southwest": self.dirsouthwest, "up": self.dirup,
                       "down": self.dirdown, "out": self.dirout}
        dirgrid.add(self.dirnorth)
        dirgrid.attach_next_to(self.dirnorthwest, self.dirnorth, Gtk.PositionType.LEFT, 1, 1)
        dirgrid.attach_next_to(self.dirnortheast, self.dirnorth, Gtk.PositionType.RIGHT, 1, 1)
        dirgrid.attach_next_to(self.dirwest, self.dirnorthwest, Gtk.PositionType.BOTTOM, 1, 1)
        dirgrid.attach_next_to(self.direast, self.dirnortheast, Gtk.PositionType.BOTTOM, 1, 1)
        dirgrid.attach_next_to(self.dirsouthwest, self.dirwest, Gtk.PositionType.BOTTOM, 1, 1)
        dirgrid.attach_next_to(self.dirsouth, self.dirsouthwest, Gtk.PositionType.RIGHT, 1, 1)
        dirgrid.attach_next_to(self.dirsoutheast, self.dirsouth, Gtk.PositionType.RIGHT, 1, 1)
        dirgrid.attach_next_to(self.dirup, self.dirnortheast, Gtk.PositionType.RIGHT, 1, 1)
        dirgrid.attach_next_to(self.dirout, self.direast, Gtk.PositionType.RIGHT, 1, 1)
        dirgrid.attach_next_to(self.dirdown, self.dirsoutheast, Gtk.PositionType.RIGHT, 1, 1)

        rtbox = Gtk.ListBox()
        self.rtpbar = Gtk.ProgressBar()
        rtbox.add(self.rtpbar)
        self.sppbar = Gtk.ProgressBar()
        rtbox.add(self.sppbar)
        entrytext = Gtk.Entry()
        entrytext.connect('activate', self.entrytext_activate)
        entrytext.connect('realize', self.entrytext_realize)
        #entrybox.pack_start(stancelbl, False, False, 0)
        #entrybox.pack_start(bleedlbl, False, False, 0)
        #entrybox.pack_start(stunlbl, False, False, 0)
        entrybox.pack_start(self.statusgrid, False, False, 0)
        entrybox.pack_start(dirgrid, False, False, 0)
        entrybox.pack_start(rtbox, False, False, 0)
        entrybox.pack_start(entrytext, True, True, 0)
        return entrybox

    def setup_mainwindow(self):
        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
            spacing = 6)
        listbox = Gtk.VBox()
        
        hb = self.setup_headerbar()
        topwindow = self.setup_topwindow()
        bottomwindow = self.setup_bottomwindow()
        entrybox = self.setup_entrybox()
        
        listbox.pack_start(hb, False, False, 0)
        paned = Gtk.VPaned()
        paned.add(topwindow)
        paned.add(bottomwindow)
        listbox.pack_start(paned, True, True, 0)
        listbox.pack_start(entrybox, False, False, 0)

        box_outer.pack_start(listbox, True, True, 0)

        return box_outer

    def entrytext_activate(self, widget):
        text = widget.get_text().strip()
        print("{}".format(text))
        self.tn.write("{}\n".format(text))
        self.textbuffer2.insert(self.textbuffer2.get_end_iter(), "{}\n".format(text))
        widget.set_text("")

    def entrytext_realize(self, widget):
        widget.grab_focus()

    def read_input(self, source, condition):
        line = self.tn.read_very_eager()
        line = line.strip("\r\n")
        line = line.replace('"','\'')
        lines = line.split('\n')
        for line in lines:
            line = TextLine(line, self.unmatched, self)
            print("RETURNED")
            if line.prompt:
                self.textbuffer2.insert(self.textbuffer2.get_end_iter(), ">\n")
            elif self.stream:
                pass
            elif line.lines:
                for line in line.lines:
                    if line:
                        if re.match("^<color=", line):
                            color = re.match("^<color=(.+?)>", line).group(1)
                            text = re.match("^<color=.+?>(.+)</color>", line).group(1)
                            if color == "yellow":
                                tag_yellow = self.textbuffer2.create_tag(foreground="#FFFF00")
                                self.textbuffer2.insert_with_tags(self.textbuffer2.get_end_iter(),
                                    text, tag_yellow)
                            elif color == "red":
                                tag_red = self.textbuffer2.create_tag(foreground="#FF0000")
                                self.textbuffer2.insert_with_tags(self.textbuffer2.get_end_iter(),
                                    text, tag_red)
                        elif re.match("^<d>", line):
                            text = re.match("^<d>(.+?)</d>", line).group(1)
                            tag_red = self.textbuffer2.create_tag(foreground="#FF0000")
                            self.textbuffer2.insert_with_tags(self.textbuffer2.get_end_iter(),
                                text, tag_red)
                        else:
                            self.textbuffer2.insert(self.textbuffer2.get_end_iter(),
                                "{}".format(line))
                self.textbuffer2.insert(self.textbuffer2.get_end_iter(),"\n")   
            elif len(line.text) > 0:
                self.textbuffer2.insert(self.textbuffer2.get_end_iter(), "{}\n".format(line.text))
                
        return True

    def scrolledwindow2_changed(self, widget, event, data=None):
        adj = widget.get_vadjustment()
        adj.set_value( adj.get_upper() - adj.get_page_size() )

    def on_updatebar(self, data):
        self.rtcounter -= 1
        fraction = float(self.rtcounter) / float(self.rtmax)
        self.rtpbar.set_fraction(fraction)
        print("COUNTER: {}/{} = {}".format(self.rtcounter, self.rtmax, fraction))
        if self.rtcounter > 0:
            return True
        else:
            self.rtpbar.set_fraction(0)
            return False
        return True

    def on_updatespbar(self, data):
        self.spcounter -= 1
        fraction = float(self.spcounter) / float(self.spmax)
        self.sppbar.set_fraction(fraction)
        print("COUNTER: {}/{} = {}".format(self.spcounter, self.spmax, fraction))
        if self.spcounter > 0:
            return True
        else:
            self.sppbar.set_fraction(0)
            return False
        return True

    def server_tick(self, data):
        self.server_time += 1
        return True

    def set_hand(self, hand, item):
        if hand == "right":
            self.lblrighthand.set_label(item)
        elif hand == "left":
            self.lbllefthand.set_label(item)

    def set_compass(self, line):
        print("ALL OFF")
        for k,v in self.compassdict.items():
            print("SETTING: images/{}.xpm".format(k))
            v.set_from_file("images/{}.xpm".format(k))
        dirs = []
        print("DIRECTION LINE: {}".format(line))
        while re.match("^<dir value='([a-zA-Z]+?)'/>", line):
            match = re.match("^<dir value='([a-zA-Z]+?)'/>", line)
            direction = match.group(1)
            if direction == "n":
                dirs.append("north")
            elif direction == "s":
                dirs.append("south")
            elif direction == "e":
                dirs.append("east")
            elif direction == "w":
                dirs.append("west")
            elif direction == "ne":
                dirs.append("northeast")
            elif direction == "se":
                dirs.append("southeast")
            elif direction == "nw":
                dirs.append("northwest")
            elif direction == "sw":
                dirs.append("southwest")
            elif direction == "up":
                dirs.append("up")
            elif direction == "down":
                dirs.append("down")
            elif direction == "out":
                dirs.append("out")
            else:
                print("NO DIRECTION FOR: {}".format())
            line = re.sub("^<dir value='([a-zA-Z]+?)'/>", "", line, count=1)
        print("DIRECTIONS")
        print("----------")
        print(line)
        print(dirs)
        for k,v in self.compassdict.items():
            if k in dirs:
                v.set_from_file("images/{}_on.xpm".format(k))
            else:
                v.set_from_file("images/{}.xpm". format(k))

    def set_spell(self, spell):
        self.lblspell.set_label(spell)

    def toggle_icon(self, icon, visible):
        if icon == "HIDDEN":
            if visible == "y":
                self.hideimg.set_from_file("images/hide.xpm")
            else:
                self.hideimg.set_from_file("images/blank.xpm")
        if icon == "KNEELING":
            if visible == "y":
                self.posimg.set_from_file("images/kneel.xpm")
        if icon == "PRONE":
            if visible == "y":
                self.posimg.set_from_file("images/lie.xpm")
        if icon == "SITTING":
            if visible == "y":
                self.posimg.set_from_file("images/sit.xpm")
        if icon == "STANDING":
            if visible == "y":
                self.posimg.set_from_file("images/stand.xpm")
        
class TextLine:
    def __init__(self, line, unmatched, mainwindow):
        self.text = ''
        self.style = ''
        self.preset = ''
        self.lines = None
        self.prompt = False
        line = line.strip()
        while len(line) > 0:
            print("Processing: {}".format(line))
            line = re.sub("<pushBold/>","<color=yellow>", line)
            line = re.sub("<popBold/>","</color>", line)
            line = re.sub("<d>","<color=red>", line)
            line = re.sub("</d>","</color>", line)
            if re.match("^<", line):
                if re.match("(^<resource picture='.+'/>)",line):
                    line = re.sub("<resource picture='0'/>", "", line)
                elif re.match("^<style id='(.+)' />", line):
                    objs = re.match("^<style id='(.+)' />", line)
                    self.style = objs.groups(0)
                    line = re.sub("^<style id='(.+)' />", "", line)
                elif re.match("<style id=''/>", line):
                    line = re.sub("<style id=''/>", "", line)
                    self.text = line
                elif re.match("^<preset id='([a-zA-Z]+)'>(.+)</preset>", line):
                    objs = re.match("^<preset id='([a-zA-Z]+)'>(.+)</preset>", line)
                    self.preset = objs.group(1)
                    line = re.sub("^<preset id='([a-zA-Z]+)'>", "", line)
                    line = re.sub("</preset>", "", line)
                elif re.match("^<roundTime value='([0-9]+)'/>", line):
                    mainwindow.rtpbar.set_fraction(1)
                    objs = re.match("^<roundTime value='([0-9]+)'/>", line)
                    rt = int(objs.group(1)) - mainwindow.server_time
                    print("******** RT: {} ********* ".format(rt))
                    mainwindow.rtcounter = rt
                    mainwindow.rtmax = rt
                    GObject.timeout_add_seconds(1, mainwindow.on_updatebar, None)
                    line = re.sub("^<roundTime value='([0-9]+)'/>", "", line)
                elif re.match("^<indicator id='Icon([a-z[A-Z]+?)'", line):
                    objs = re.match("<indicator id='Icon([a-z[A-Z]+?)' visible='([yn])'/>", line)
                    icon = objs.group(1)
                    status = objs.group(2)
                    print("*** ICON STATUS: {}={} ***".format(icon, status))
                    line = re.sub("<indicator id='([a-z[A-Z]+?)' visible='([yn])'/>", "", line, count=1)
                    if icon == "HIDDEN":
                        mainwindow.toggle_icon(icon, status)
                    elif status == "y":
                        mainwindow.toggle_icon(icon, status)
                elif re.match("^<prompt time='[0-9]+'>&gt;</prompt>", line):
                    objs = re.match("^<prompt time='([0-9]+)'>&gt;</prompt>", line)
                    server_time = int(objs.group(1))
                    if server_time != mainwindow.server_time:
                        print("SERVER CORRECTION: {} vs {}".format(server_time, mainwindow.server_time))
                        mainwindow.server_time = server_time
                    self.prompt = True
                    break
                elif re.match("^<right>(.+?)</right>", line):
                    match = re.match("^<right>(.+?)</right>", line)
                    mainwindow.set_hand("right", match.group(1))
                    line = re.sub("^<right>(.+?)</right>", "", line)
                elif re.match("^<left>(.+?)</left>", line):
                    match = re.match("^<left>(.+?)</left>", line)
                    mainwindow.set_hand("left", match.group(1))
                    line = re.sub("^<left>(.+?)</left>", "", line)
                elif re.match("^<right exist='[0-9]+?' noun='(.+?)'>.+?</right>", line):
                    match = re.match("^<right exist='[0-9]+?' noun='(.+?)'>.+?</right>", line)
                    mainwindow.set_hand("right", match.group(1))
                    line = re.sub("^<right exist='[0-9]+?' noun='(.+?)'>.+?</right>", "", line)
                elif re.match("^<left exist='[0-9]+?' noun='(.+?)'>.+?</left>", line):
                    match = re.match("^<left exist='[0-9]+?' noun='(.+?)'>.+?</left>", line)
                    mainwindow.set_hand("left", match.group(1))
                    line = re.sub("^<left exist='[0-9]+?' noun='(.+?)'>.+?</left>", "", line)
                elif re.match("^<spell exist='.+?'>(.+?)</spell>", line):
                    match = re.match("^<spell exist='.+?'>(.+?)</spell>", line)
                    mainwindow.set_spell(match.group(1))
                    line = re.sub("^<spell exist='.+?'>(.+?)</spell>", "", line)
                elif re.match("^<spell>(.+?)</spell>", line):
                    match = re.match("^<spell>(.+?)</spell>", line)
                    mainwindow.set_spell(match.group(1))
                    line = re.sub("^<spell>(.+?)</spell>", "", line)
                elif re.match("<castTime value='([0-9]+)'/>", line):
                    mainwindow.sppbar.set_fraction(1)
                    objs = re.match("^<castTime value='([0-9]+)'/>", line)
                    rt = int(objs.group(1)) - mainwindow.server_time
                    print("******** SP RT: {} ********* ".format(rt))
                    mainwindow.spcounter = rt
                    mainwindow.spmax = rt
                    GObject.timeout_add_seconds(1, mainwindow.on_updatespbar, None)
                    line = re.sub("^<castTime value='([0-9]+)'/>", "", line, count = 1)
                elif re.match("^<clearContainer id='stow'/>", line):
                    line = re.sub("^<clearContainer id='stow'/>", "", line, count = 1)
                elif re.match("<inv id='stow'>.+?</inv>", line):
                    line = re.sub("<inv id='stow'>.+?</inv>", "", line, count = 1)
                elif re.match("^<clearStream id='inv' ifClosed=''/>", line):
                    line = re.sub("^<clearStream id='inv' ifClosed=''/>", "", line)
                elif re.match("<pushStream id='inv'/>", line):
                    mainwindow.stream = True
                    line = re.sub("<pushStream id='inv'/>", "", line)
                elif re.match("<popStream/>", line):
                    mainwindow.stream = False
                    line = re.sub("<popStream/>", "", line)
                elif re.match("<compass>(.+)</compass>", line):
                    match = re.match("<compass>(.+)</compass>", line)
                    mainwindow.set_compass(match.group(1))
                    line = re.sub("<compass>(.+)</compass>", "", line)
                else:
                    unmatched.write("{}\n".format(line))
                    break
            else:
                self.text = line
                break
        
        if len(self.text.strip()) > 0:  
            self.lines = re.split("(<color=.+?>.*?</color>)", self.text)
        print("LINES")
        print("-----")
        print self.lines

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()

