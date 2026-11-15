#!/usr/bin/env python3
"""GTK4 text probe: every keystroke and submission is printed so a script can assert on it."""
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


def on_changed(entry):
    print(f"text={entry.get_text()}", flush=True)


def on_activate(entry):
    print(f"submitted={entry.get_text()}", flush=True)


def build():
    app = Gtk.Application(application_id="dev.agent.SeatTextProbe")

    def activate(app):
        window = Gtk.ApplicationWindow(application=app, title="text-probe")
        window.set_default_size(600, 240)
        entry = Gtk.Entry()
        entry.connect("changed", on_changed)
        entry.connect("activate", on_activate)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(16)
        box.set_margin_end(16)
        box.set_valign(Gtk.Align.CENTER)
        box.append(entry)
        window.set_child(box)
        window.present()
        entry.grab_focus()
        print("ready", flush=True)

    app.connect("activate", activate)
    return app


if __name__ == "__main__":
    raise SystemExit(build().run(None))
