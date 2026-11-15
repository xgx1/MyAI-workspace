/* Regression harness for per-device X11 input. Refuses :0 and never touches a Wayland seat.
 *
 * The point is isolation inside one X server: an extra master pair carries the agent's
 * keyboard and pointer, the target window's client uses that master, and the human's core
 * devices keep their own focus and position. Everything runs on one X connection, because
 * XTest routes through the master of the client that sent the request.
 */
#include <X11/XKBlib.h>
#include <X11/Xlib.h>
#include <X11/extensions/XInput2.h>
#include <X11/extensions/XTest.h>
#include <X11/keysym.h>
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int errors;
static int on_error(Display *d, XErrorEvent *e) {
    char text[256];
    XGetErrorText(d, e->error_code, text, sizeof text);
    fprintf(stderr, "XERROR %s code=%u request=%u minor=%u resource=0x%lx\n", text,
            e->error_code, e->request_code, e->minor_code, e->resourceid);
    errors++;
    return 0;
}

static int find_master(Display *d, int use, const char *name, int *ids, int max) {
    int n = 0, found = 0;
    XIDeviceInfo *info = XIQueryDevice(d, XIAllDevices, &n);
    if (!info) return 0;
    for (int i = 0; i < n && found < max; ++i)
        /* A master pair reports itself as NAME pointer / NAME keyboard, so match the prefix. */
        if (info[i].use == use && !strncmp(info[i].name, name, strlen(name)))
            ids[found++] = info[i].deviceid;
    XIFreeDeviceInfo(info);
    return found;
}

/* Creates the master pair if absent. Returns 0 on success. */
static int ensure_master(Display *d, const char *name, int *pointer, int *keyboard) {
    int ptr = 0, kbd = 0;
    if (find_master(d, XIMasterPointer, name, &ptr, 1) &&
        find_master(d, XIMasterKeyboard, name, &kbd, 1)) {
        *pointer = ptr;
        *keyboard = kbd;
        return 0;
    }
    XIAddMasterInfo add = {XIAddMaster, name, True, True};
    XIChangeHierarchy(d, (XIAnyHierarchyChangeInfo *)&add, 1);
    XSync(d, False);
    if (errors) return 1;
    if (!find_master(d, XIMasterPointer, name, &ptr, 1) ||
        !find_master(d, XIMasterKeyboard, name, &kbd, 1)) {
        fprintf(stderr, "master %s did not appear\n", name);
        return 1;
    }
    *pointer = ptr;
    *keyboard = kbd;
    return 0;
}

static int master_of(Display *d, Window win, int *pointer) {
    int id = 0;
    if (!XIGetClientPointer(d, win, &id) || !id) return 1;
    *pointer = id;
    return 0;
}

static void describe(Display *d, const char *stage, Window win, int pointer, int keyboard) {
    Window core_focus = None, master_focus = None;
    int revert = 0;
    XGetInputFocus(d, &core_focus, &revert);
    if (keyboard) XIGetFocus(d, keyboard, &master_focus);
    Window root = DefaultRootWindow(d), child = None;
    int rx = 0, ry = 0, wx = 0, wy = 0;
    unsigned mask = 0;
    XQueryPointer(d, root, &root, &child, &rx, &ry, &wx, &wy, &mask);
    double mx = -1, my = -1;
    if (pointer) {
        Window mroot = None, mchild = None;
        double wdx = 0, wdy = 0;
        XIButtonState buttons = {0, NULL};
        XIModifierState mods = {0, 0, 0};
        XIGroupState group = {0, 0, 0};
        XIQueryPointer(d, pointer, root, &mroot, &mchild, &mx, &my, &wdx, &wdy, &buttons,
                       &mods, &group);
        free(buttons.mask);
    }
    printf("%s core_focus=0x%lx master_focus=0x%lx core_pointer=%d,%d master_pointer=%.1f,%.1f\n",
           stage, core_focus, master_focus, rx, ry, mx, my);
    if (win) {
        int cp = 0, self = 0;
        int ok = master_of(d, win, &cp);
        Bool self_set = XIGetClientPointer(d, None, &self);
        printf("%s window=0x%lx client_pointer=%d%s self_pointer=%d explicitly_set=%d\n", stage,
               win, cp, ok ? " (unset)" : "", self, self_set);
    }
}

static int press_keysym(Display *d, KeySym want) {
    KeyCode code = XKeysymToKeycode(d, want);
    if (!code) {
        fprintf(stderr, "no keycode for keysym 0x%lx\n", want);
        return 1;
    }
    KeyCode shift = 0;
    if (XkbKeycodeToKeysym(d, code, 0, 0) != want) {
        shift = XKeysymToKeycode(d, XK_Shift_L);
        if (!shift) return 1;
        XTestFakeKeyEvent(d, shift, True, CurrentTime);
    }
    XTestFakeKeyEvent(d, code, True, CurrentTime);
    XTestFakeKeyEvent(d, code, False, CurrentTime);
    if (shift) XTestFakeKeyEvent(d, shift, False, CurrentTime);
    return 0;
}

static int type_text(Display *d, const char *text) {
    for (const unsigned char *p = (const unsigned char *)text; *p; ++p) {
        unsigned char c = *p;
        KeySym ks = XK_space;
        if (c != (unsigned char)' ') {
            if (c >= 0x20 && c < 0x7f) ks = (KeySym)c;
            else return 1;
        }
        if (press_keysym(d, ks)) return 1;
    }
    return 0;
}

static Window number_window(const char *s) {
    char *end;
    errno = 0;
    unsigned long n = strtoul(s, &end, 0);
    if (errno || *end || !n) {
        fprintf(stderr, "invalid window id: %s\n", s);
        exit(2);
    }
    return (Window)n;
}

static void usage(void) {
    fprintf(stderr,
            "usage: xi2-inject --display :NONZERO [--master NAME] COMMAND\n"
            "  state [WINDOW]               core and master focus, both pointer positions\n"
            "  type WINDOW TEXT             type TEXT into WINDOW via the agent master\n"
            "  key WINDOW KEYSYM_NAME       press one keysym, e.g. Return\n"
            "  click WINDOW X Y [BUTTON]    click inside WINDOW via the agent master\n"
            "  move WINDOW X Y              move the agent pointer only\n"
            "  remove                       remove the agent master again\n");
}

int main(int argc, char **argv) {
    if (argc < 4 || strcmp(argv[1], "--display")) { usage(); return 2; }
    char *end;
    errno = 0;
    unsigned long display = argv[2][0] == ':' ? strtoul(argv[2] + 1, &end, 10) : 0;
    if (!display || errno || display > INT_MAX || *end) {
        fprintf(stderr, "REFUSED: explicit local nonzero display required; never :0\n");
        return 2;
    }
    const char *master = "mpx-agent";
    int arg = 3;
    if (!strcmp(argv[3], "--master") && argc > 5) { master = argv[4]; arg = 5; }
    if (arg < argc && !strcmp(argv[arg], "state")) { /* window argument is optional */ }
    const char *command = argv[arg];
    Display *d = XOpenDisplay(argv[2]);
    if (!d) { fprintf(stderr, "cannot open %s\n", argv[2]); return 2; }
    XSetErrorHandler(on_error);
    int major = 2, minor = 0;
    if (XIQueryVersion(d, &major, &minor) != Success) {
        fprintf(stderr, "XI2 unavailable\n");
        return 2;
    }
    int pointer = 0, keyboard = 0;
    int removed = 0;
    if (!strcmp(command, "remove")) {
        if (!find_master(d, XIMasterPointer, master, &pointer, 1)) {
            printf("no master %s\n", master);
            return 0;
        }
        XIRemoveMasterInfo rm = {XIRemoveMaster, pointer, XIFloating, 0, 0};
        XIChangeHierarchy(d, (XIAnyHierarchyChangeInfo *)&rm, 1);
        removed = 1;
    } else if (ensure_master(d, master, &pointer, &keyboard)) {
        return 2;
    }
    if (removed) { XSync(d, False); XCloseDisplay(d); return errors ? 2 : 0; }

    const char *extra = argc > arg + 1 ? argv[arg + 1] : NULL;
    Window win = 0;
    int rc = 0;
    if (!strcmp(command, "state")) {
        win = extra ? number_window(extra) : 0;
        describe(d, "before", win, pointer, keyboard);
    } else if (!strcmp(command, "prepare") || !strcmp(command, "type") || !strcmp(command, "key") ||
               !strcmp(command, "click") || !strcmp(command, "move")) {
        if (!extra) { usage(); return 2; }
        win = number_window(extra);
        describe(d, "before", win, pointer, keyboard);
        /* The target client and this injecting connection both have to use the agent master,
         * otherwise XTest would route through the core pair and reach the human's window. */
        XISetClientPointer(d, win, pointer);
        XISetClientPointer(d, None, pointer);
        XISetFocus(d, keyboard, win, CurrentTime);
        XSync(d, False);
        Window got = None;
        XIGetFocus(d, keyboard, &got);
        if (got != win) {
            fprintf(stderr, "master keyboard focus is 0x%lx, wanted 0x%lx\n", got, win);
            return 2;
        }
        if (!strcmp(command, "prepare")) {
            rc = 0;
        } else if (!strcmp(command, "type")) {
            rc = type_text(d, argv[arg + 2]);
        } else if (!strcmp(command, "key")) {
            KeySym ks = XStringToKeysym(argv[arg + 2]);
            if (ks == NoSymbol) { fprintf(stderr, "unknown keysym\n"); return 2; }
            rc = press_keysym(d, ks);
        } else if (!strcmp(command, "click")) {
            int x = atoi(argv[arg + 2]), y = atoi(argv[arg + 3]);
            int button = argc > arg + 4 ? atoi(argv[arg + 4]) : 1;
            XTestFakeMotionEvent(d, -1, x, y, CurrentTime);
            XTestFakeButtonEvent(d, button, True, CurrentTime);
            XTestFakeButtonEvent(d, button, False, CurrentTime);
        } else {
            XTestFakeMotionEvent(d, -1, atoi(argv[arg + 2]), atoi(argv[arg + 3]), CurrentTime);
        }
        XSync(d, False);
        describe(d, "after", win, pointer, keyboard);
    } else {
        usage();
        return 2;
    }
    XSync(d, False);
    XCloseDisplay(d);
    return rc || errors ? 2 : 0;
}
