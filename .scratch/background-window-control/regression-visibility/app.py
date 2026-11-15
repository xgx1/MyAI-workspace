#!/usr/bin/env python3
"""Real GTK3 integration fixture; all data belongs to this scratch run."""
import json, os, pathlib, sys, time
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,Gdk,GLib
name=sys.argv[1]
path=pathlib.Path(sys.argv[2])
GLib.set_prgname(name)
Gdk.set_program_class(name)
state=dict(name=name,pid=os.getpid(),text='',keys=[],buttons=[],motions=[],scrolls=[],ready=False)
def emit(kind,**data):
    state['last']={'kind':kind,'time':time.monotonic(),**data}
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(state));tmp.replace(path)
    print(json.dumps(state['last']),flush=True)
win=Gtk.Window(title=name)
win.set_default_size(620,400)
win.connect('destroy',Gtk.main_quit)
box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8)
box.set_border_width(20)
entry=Gtk.Entry();entry.set_placeholder_text(name)
entry.connect('changed',lambda e:(state.update(text=e.get_text()),emit('text',text=e.get_text())))
box.pack_start(Gtk.Label(label=name),False,False,0)
box.pack_start(entry,False,False,0)
button=Gtk.Button(label='increment')
state['clicks']=0
def increment(_):
    state['clicks']+=1
    emit('clicked',clicks=state['clicks'])
button.connect('clicked',increment)
box.pack_start(button,False,False,0)
scale=Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,0,100,1)
scale.set_value(50)
scale.connect('value-changed',lambda s:(state.update(value=s.get_value()),emit('value',value=s.get_value())))
box.pack_start(scale,False,False,0)
box.pack_start(Gtk.Label(label='temporary live test state'),True,True,0)
win.add(box)
win.add_events(Gdk.EventMask.POINTER_MOTION_MASK|Gdk.EventMask.BUTTON_PRESS_MASK|Gdk.EventMask.SCROLL_MASK|Gdk.EventMask.KEY_PRESS_MASK)
def key(_,e):
    state['keys'].append(int(e.keyval));emit('key',keyval=int(e.keyval),string=e.string)
def motion(_,e):
    state['motions'].append([round(e.x,2),round(e.y,2)])
    state['motions']=state['motions'][-200:]
    emit('motion',x=e.x,y=e.y)
def press(_,e):
    state['buttons'].append([int(e.button),round(e.x,2),round(e.y,2)])
    emit('button',button=int(e.button),x=e.x,y=e.y)
win.connect('key-press-event',key)
win.connect('motion-notify-event',motion)
win.connect('button-press-event',press)
win.connect('scroll-event',lambda _,e:(state['scrolls'].append(int(e.direction)),emit('scroll',direction=int(e.direction)),False)[-1])
win.show_all();entry.grab_focus()
def ready():
    state['ready']=True
    state['size']=[win.get_allocated_width(),win.get_allocated_height()]
    state['entry']=[entry.get_allocation().x,entry.get_allocation().y,entry.get_allocated_width(),entry.get_allocated_height()]
    state['button']=[button.get_allocation().x,button.get_allocation().y,button.get_allocated_width(),button.get_allocated_height()]
    state['scale']=[scale.get_allocation().x,scale.get_allocation().y,scale.get_allocated_width(),scale.get_allocated_height()]
    emit('ready')
    return False
GLib.timeout_add(200,ready)
Gtk.main()
