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
        self.currenttime = 0
        self.server_time = 0
        self.ICON_HIDDEN = 1001
        self.statusgrid = None
        self.blankimg = None
        self.hideimg = None
        self.posimg = None


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
        image = Gtk.Image.new_from_file("images/lefthand.png")

        label1 = Gtk.Label("Left Hand", xalign=0)
        label2 = Gtk.Label("Right Hand", xalign=0)
        label3 = Gtk.Label("Spell", xalign=0)

        btn1 = Gtk.Button(label="Macro Set")
        btn2 = Gtk.Button(label="Options")
        hb.pack_start(image)
        hb.pack_start(label1)
        hb.pack_start(label2)
        hb.pack_start(label3)
        hb.pack_end(btn1)
        hb.pack_end(btn2)
        return hb

    def setup_topwindow(self):
        subbox = Gtk.HBox(spacing=6)        

        thoughtwindow = Gtk.ScrolledWindow()
        thoughtwindow.set_hexpand(True)
        thoughtwindow.set_vexpand(True)
        thoughtview = Gtk.TextView()
        thoughtbuffer = thoughtview.get_buffer()
        thoughtbuffer.set_text("This is the thought window")
        thoughtwindow.add(thoughtview)

        roomwindow = Gtk.ScrolledWindow()
        roomwindow.set_hexpand(True)
        roomwindow.set_vexpand(True)
        roomview = Gtk.TextView()
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
        dirnorth = Gtk.Image.new_from_file("images/north.xpm")
        dirsouth = Gtk.Image.new_from_file("images/south.xpm")
        direast = Gtk.Image.new_from_file("images/east.xpm")
        dirwest = Gtk.Image.new_from_file("images/west.xpm")
        dirnortheast = Gtk.Image.new_from_file("images/northeast.xpm")
        dirsoutheast = Gtk.Image.new_from_file("images/southeast.xpm")
        dirnorthwest = Gtk.Image.new_from_file("images/northwest.xpm")
        dirsouthwest = Gtk.Image.new_from_file("images/southwest.xpm")
        dirup = Gtk.Image.new_from_file("images/up.xpm")
        dirdown = Gtk.Image.new_from_file("images/down.xpm")
        dirout = Gtk.Image.new_from_file("images/out.xpm")
        dirgrid.add(dirnorth)
        dirgrid.attach_next_to(dirnorthwest, dirnorth, Gtk.PositionType.LEFT, 1, 1)
        dirgrid.attach_next_to(dirnortheast, dirnorth, Gtk.PositionType.RIGHT, 1, 1)
        dirgrid.attach_next_to(dirwest, dirnorthwest, Gtk.PositionType.BOTTOM, 1, 1)
        dirgrid.attach_next_to(direast, dirnortheast, Gtk.PositionType.BOTTOM, 1, 1)
        dirgrid.attach_next_to(dirsouthwest, dirwest, Gtk.PositionType.BOTTOM, 1, 1)
        dirgrid.attach_next_to(dirsouth, dirsouthwest, Gtk.PositionType.RIGHT, 1, 1)
        dirgrid.attach_next_to(dirsoutheast, dirsouth, Gtk.PositionType.RIGHT, 1, 1)
        dirgrid.attach_next_to(dirup, dirnortheast, Gtk.PositionType.RIGHT, 1, 1)
        dirgrid.attach_next_to(dirout, direast, Gtk.PositionType.RIGHT, 1, 1)
        dirgrid.attach_next_to(dirdown, dirsoutheast, Gtk.PositionType.RIGHT, 1, 1)

        rtbox = Gtk.ListBox()
        self.rtpbar = Gtk.ProgressBar()
        rtbox.add(self.rtpbar)
        sppbar = Gtk.ProgressBar()
        rtbox.add(sppbar)
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

    def server_tick(self, data):
        self.server_time += 1
        return True

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
                    #<right>Empty</right><left exist='54756194' noun='quarterstaff'>ironwood quarterstaff</left><clearStream id='inv' ifClosed=''/><pushStream id='inv'/>
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

