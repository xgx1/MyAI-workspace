/* Throwaway XI2 control helper. No key/button/motion injection commands. */
#include <X11/Xlib.h>
#include <X11/extensions/XInput2.h>
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int errors;
static int xerror(Display *d, XErrorEvent *e) {
    char text[256]; XGetErrorText(d, e->error_code, text, sizeof text);
    fprintf(stderr, "XERROR %s code=%u request=%u minor=%u resource=0x%lx\n",
            text, e->error_code, e->request_code, e->minor_code, e->resourceid);
    errors++; return 0;
}
static unsigned long number(const char *s) {
    char *end; errno = 0; unsigned long n = strtoul(s, &end, 0);
    if (errno || !*s || *s == '-' || *end || !n || n > UINT_MAX) {
        fprintf(stderr, "invalid nonzero ID: %s\n", s); exit(2);
    }
    return n;
}
static void require_device(Display *d, int id, int use, int removable) {
    int n; XIDeviceInfo *info = XIQueryDevice(d, id, &n);
    if (!info || n != 1 || info->use != use ||
        (removable && strncmp(info->name, "mpx-", 4))) {
        fprintf(stderr, "device %d has wrong type or is not mpx-owned\n", id); exit(2);
    }
    XIFreeDeviceInfo(info);
}
static void query(Display *d) {
    int n; XIDeviceInfo *info = XIQueryDevice(d, XIAllDevices, &n);
    if (!info) exit(2);
    for (int i = 0; i < n; ++i) {
        Window focus = None;
        if (info[i].use == XIMasterKeyboard) XIGetFocus(d, info[i].deviceid, &focus);
        printf("device=%d use=%d attachment=%d enabled=%d focus=0x%lx name=%s\n",
               info[i].deviceid, info[i].use, info[i].attachment,
               info[i].enabled, focus, info[i].name);
    }
    int cp = 0; Bool set = XIGetClientPointer(d, None, &cp);
    printf("caller_client_pointer=%d explicitly_set=%d\n", cp, set);
    XIFreeDeviceInfo(info);
}
int main(int argc, char **argv) {
    if (argc < 4 || strcmp(argv[1], "--display")) goto usage;
    char *end; errno = 0;
    unsigned long display = argv[2][0] == ':' ? strtoul(argv[2] + 1, &end, 10) : 0;
    if (!display || errno || display > INT_MAX ||
        (*end && (*end != '.' || !end[1] || strspn(end + 1, "0123456789") != strlen(end + 1)))) {
        fprintf(stderr, "REFUSED: explicit local nonzero display required; never :0\n"); return 2;
    }
    fprintf(stderr, "target_DISPLAY=%s env_DISPLAY=%s WAYLAND_DISPLAY=%s action=%s\n", argv[2],
            getenv("DISPLAY") ? getenv("DISPLAY") : "<unset>",
            getenv("WAYLAND_DISPLAY") ? getenv("WAYLAND_DISPLAY") : "<unset>", argv[3]);
    Display *d = XOpenDisplay(argv[2]);
    if (!d) { fprintf(stderr, "cannot open %s\n", argv[2]); return 2; }
    XSetErrorHandler(xerror);
    int major = 2, minor = 0;
    if (XIQueryVersion(d, &major, &minor) != Success) {
        fprintf(stderr, "XI2 unavailable\n"); return 2;
    }
    printf("XI=%d.%d\n", major, minor);
    if (!strcmp(argv[3], "query") && argc == 4) query(d);
    else if (!strcmp(argv[3], "create") && argc == 5) {
        if (strncmp(argv[4], "mpx-", 4) || strlen(argv[4]) > 60) goto usage;
        XIAddMasterInfo add = {XIAddMaster, argv[4], True, True};
        XIChangeHierarchy(d, (XIAnyHierarchyChangeInfo *)&add, 1);
        XSync(d, False); if (errors) return 2; query(d);
    } else if (!strcmp(argv[3], "cp") && argc == 6) {
        Window win = number(argv[4]); unsigned long id = number(argv[5]);
        if (id > INT_MAX) return 2;
        require_device(d, (int)id, XIMasterPointer, 0);
        XISetClientPointer(d, win, (int)id); XSync(d, False);
        if (errors) return 2;
        int got = 0; Bool set = XIGetClientPointer(d, win, &got);
        printf("window=0x%lx client_pointer=%d explicitly_set=%d\n", win, got, set);
        if (got != (int)id) errors++;
    } else if (!strcmp(argv[3], "focus") && argc == 6) {
        Window win = number(argv[4]); unsigned long id = number(argv[5]);
        if (id > INT_MAX) return 2;
        require_device(d, (int)id, XIMasterKeyboard, 0);
        XISetFocus(d, (int)id, win, CurrentTime); XSync(d, False);
        if (errors) return 2;
        Window got = None; XIGetFocus(d, (int)id, &got);
        printf("keyboard=%lu focus=0x%lx\n", id, got);
        if (got != win) errors++;
    } else if (!strcmp(argv[3], "remove") && argc == 5) {
        unsigned long id = number(argv[4]); if (id > INT_MAX) return 2;
        require_device(d, (int)id, XIMasterPointer, 1);
        XIRemoveMasterInfo rm = {XIRemoveMaster, (int)id, XIFloating, 0, 0};
        XIChangeHierarchy(d, (XIAnyHierarchyChangeInfo *)&rm, 1);
    } else goto usage;
    XSync(d, False); XCloseDisplay(d); return errors ? 2 : 0;
usage:
    fprintf(stderr, "usage: xi2-tool --display :NONZERO query | create mpx-NAME | cp WINDOW POINTER | focus WINDOW KEYBOARD | remove MPX_POINTER\n");
    return 2;
}
