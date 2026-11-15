#!/usr/bin/env python3
"""GTK4 slider probe: prints presses and scale changes so a script can tell
"the event never arrived" apart from "it arrived somewhere else"."""
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


def build():
    app = Gtk.Application(application_id="dev.agent.SeatDragProbe")

    def activate(app):
        window = Gtk.ApplicationWindow(application=app, title="drag-probe")
        window.set_default_size(600, 240)

        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        scale.set_value(50)
        scale.set_hexpand(True)
        scale.connect("value-changed", lambda s: print(f"value={s.get_value():.2f}", flush=True))

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_valign(Gtk.Align.CENTER)
        box.append(scale)
        window.set_child(box)

        click = Gtk.GestureClick()
        click.connect(
            "pressed",
            lambda g, n, x, y: print(f"press n={n} x={x:.0f} y={y:.0f}", flush=True),
        )
        window.add_controller(click)

        window.present()
        print(f"ready scale_top={scale.get_allocation().y}", flush=True)

    app.connect("activate", activate)
    return app


if __name__ == "__main__":
    raise SystemExit(build().run(None))
