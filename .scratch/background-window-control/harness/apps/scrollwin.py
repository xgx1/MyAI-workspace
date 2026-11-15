#!/usr/bin/env python3
"""GTK4 scroll probe: a tall text view plus a window-level scroll controller."""
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


def build():
    app = Gtk.Application(application_id="dev.agent.SeatScrollProbe")

    def activate(app):
        window = Gtk.ApplicationWindow(application=app, title="scroll-probe")
        window.set_default_size(600, 400)
        view = Gtk.TextView()
        view.get_buffer().set_text("\n".join(f"line {i}" for i in range(200)))
        view.set_editable(False)
        view.set_cursor_visible(False)

        scroller = Gtk.ScrolledWindow()
        scroller.set_child(view)
        scroller.set_vexpand(True)

        controller = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.BOTH)
        controller.connect(
            "scroll",
            lambda _c, dx, dy: print(f"scrollctrl dx={dx:.2f} dy={dy:.2f}", flush=True) or False,
        )
        window.add_controller(controller)

        window.set_child(scroller)
        window.present()
        adjustment = scroller.get_vadjustment()
        adjustment.connect(
            "value-changed",
            lambda a: print(f"scroll={a.get_value():.2f}", flush=True),
        )
        print("ready", flush=True)

    app.connect("activate", activate)
    return app


if __name__ == "__main__":
    raise SystemExit(build().run(None))
