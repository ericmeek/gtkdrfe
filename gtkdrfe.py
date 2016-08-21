import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Pango
import telnetlib
import sys
import re

class MyWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="ListBox Demo")
		self.resize( 640, 480)

		box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
			spacing = 6)
		self.add(box_outer)

		listbox = Gtk.VBox()
		box_outer.pack_start(listbox, True, True, 0)

		hb = Gtk.HeaderBar()
		hb.set_show_close_button(False)
		hb.props.title = "Lukrani"
		label1 = Gtk.Label("Left Hand", xalign=0)
		label2 = Gtk.Label("Right Hand", xalign=0)
		label3 = Gtk.Label("Spell", xalign=0)

		btn1 = Gtk.Button(label="Macro Set")
		btn2 = Gtk.Button(label="Options")

		hb.pack_start(label1)
		hb.pack_start(label2)
		hb.pack_start(label3)
		hb.pack_end(btn1)
		hb.pack_end(btn2)

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
		tag_bold = roombuffer.create_tag(weight=Pango.Weight.BOLD)
		roombuffer.insert_with_tags(roombuffer.get_end_iter(),
			"This is a bold line\n", tag_bold)
		tag_yellow = roombuffer.create_tag(foreground="#FF0000")
		roombuffer.insert_with_tags(roombuffer.get_end_iter(),
			"This is a red line\n", tag_yellow)
		roomwindow.add(roomview)
		subbox.pack_start(thoughtwindow, True, True, 0)
		subbox.pack_start(roomwindow, True, True, 0)


		storybox = Gtk.Box(spacing=6)
		scrolledwindow2 = Gtk.ScrolledWindow()
		scrolledwindow2.set_hexpand(True)
		scrolledwindow2.set_vexpand(True)
		storybox.pack_start(scrolledwindow2, True, True, 0)
		textview2 = Gtk.TextView()
		textview2.set_editable(False)
		textview2.set_cursor_visible(False)
		textview2.set_wrap_mode(Gtk.WrapMode.WORD)
		self.textbuffer2 = textview2.get_buffer()
		self.textbuffer2.set_text("This is the story window\n")
		scrolledwindow2.add(textview2)

		entrybox = Gtk.Box(spacing=6)
		stancelbl = Gtk.Label("S", xalign=0)
		bleedlbl = Gtk.Label("N", xalign=0)
		stunlbl = Gtk.Label("N", xalign=0)
		dirlbl = Gtk.Label("NSEW", xalign=0)
		rtbox = Gtk.ListBox()
		rtpbar = Gtk.ProgressBar()
		rtbox.add(rtpbar)
		sppbar = Gtk.ProgressBar()
		rtbox.add(sppbar)
		entrytext = Gtk.Entry()
		entrytext.connect('activate', self.entrytext_activate)
		entrybox.pack_start(stancelbl, False, False, 0)
		entrybox.pack_start(bleedlbl, False, False, 0)
		entrybox.pack_start(stunlbl, False, False, 0)
		entrybox.pack_start(dirlbl, False, False, 0)
		entrybox.pack_start(rtbox, False, False, 0)
		entrybox.pack_start(entrytext, True, True, 0)

		
		listbox.pack_start(hb, False, False, 0)
		paned = Gtk.VPaned()
		paned.add(subbox)
		paned.add(storybox)
		listbox.pack_start(paned, True, True, 0)
		listbox.pack_start(entrybox, False, False, 0)
		listbox.show_all()

		scrolledwindow2.connect('size-allocate', self.scrolledwindow2_changed)

		self.unmatched = open("/home/eric/Documents/drunmatched.txt", "w")
		self.matched = open("/home/eric/Documents/drmatched.txt", "w")

		self.tn = telnetlib.Telnet('localhost', 8000)
		GLib.io_add_watch(self.tn.fileno(), GLib.IO_IN|GLib.IO_PRI|GLib.IO_ERR|GLib.IO_HUP, self.read_input)

		self.count = 0

	def entrytext_activate(self, widget):
		text = widget.get_text().strip()
		print("{}".format(text))
		self.tn.write("{}\n".format(text))
		widget.set_text("")

	def read_input(self, source, condition):
		line = self.tn.read_very_eager()
		line = line.strip("\r\n")
		line = line.replace('"','\'')
		lines = line.split('\n')
		for line in lines:
			line = TextLine(line, self.unmatched)
			if line.lines:
				for line in line.lines:
					if re.match("^<color=", line):
						color = re.match("^<color=(.+?)>", line).group(1)
						text = re.match("^<color=.+?>(.+)</color>", line).group(1)
						if color == "yellow":
							tag_yellow = self.textbuffer2.create_tag(foreground="#FFFF00")
							self.textbuffer2.insert_with_tags(self.textbuffer2.get_end_iter(),
								text, tag_yellow)
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

class TextLine:
	def __init__(self, line, unmatched):
		self.text = ''
		self.style = ''
		self.preset = ''
		self.lines = None
		line = line.strip()
		while len(line) > 0:
			print("Processing: {}".format(line))
			line = re.sub("<pushBold/>","<color=yellow>",line)
			line = re.sub("<popBold/>","</color>",line)
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