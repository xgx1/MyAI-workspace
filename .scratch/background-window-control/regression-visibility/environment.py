#!/usr/bin/env python3
"""Owned integration-test environment: a nested niri that is a *Wayland client* of the
production compositor -- no Xvfb anywhere.

Why: Xvfb has no DRI3, so everything inside it degrades to llvmpipe, and a bare X server
is invisible to the desktop monitor. The production compositor gives the nested niri a real
GPU-backed Wayland surface. Isolation is kept by parking that surface on the hidden
workspace 'ue' (the same rule agent desktops use), so no fixture window ever appears on the
human's screen.

The nested niri still spawns xwayland-satellite for its own X11 clients, so the suites keep
one X display to inject into -- it is just no longer the surface we render into.
"""
import json, os, pathlib, re, subprocess, time, traceback

ROOT = pathlib.Path(__file__).resolve().parent
RUN = ROOT / 'run'
RUN.mkdir(exist_ok=True)
PROD_RUNTIME = '/run/user/1000'
PARK_WORKSPACE = os.environ.get('BWC_PARK_WORKSPACE', 'ue')
NIRI = os.environ.get('NIRI_BIN', '/home/sx/projects/niri/target/debug/niri')
children = []
files = []


def spawn(argv, name, env):
    f = open(RUN / (name + '.log'), 'w')
    files.append(f)
    p = subprocess.Popen(argv, env=env, stdout=f, stderr=subprocess.STDOUT)
    children.append((name, p))
    return p


def until(fn, seconds=25):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        value = fn()
        if value:
            return value
        time.sleep(.05)
    raise TimeoutError('readiness deadline')


def systemctl_env(name):
    try:
        out = subprocess.run(['systemctl', '--user', 'show-environment'], capture_output=True,
                             text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return ''
    for line in (out or '').splitlines():
        if line.startswith(name + '='):
            return line.split('=', 1)[1].strip()
    return ''


def prod_wayland():
    name = systemctl_env('WAYLAND_DISPLAY')
    if name and os.path.exists(os.path.join(PROD_RUNTIME, name)):
        return name
    for cand in sorted(pathlib.Path(PROD_RUNTIME).glob('wayland-*')):
        if cand.name.endswith('.lock'):
            continue
        return cand.name
    return ''


def prod_socket():
    sock = systemctl_env('NIRI_SOCKET')
    if sock and os.path.exists(sock):
        return sock
    for cand in sorted(pathlib.Path(PROD_RUNTIME).glob('niri.wayland-1.*.sock')):
        pid = cand.name.rsplit('.', 2)[-2]
        try:
            os.kill(int(pid), 0)
        except (OSError, ValueError):
            continue
        return str(cand)
    return ''


def prod_windows(socket):
    p = subprocess.run(['niri', 'msg', '-j', 'windows'],
                       env={'PATH': '/usr/local/bin:/usr/bin:/bin', 'HOME': '/home/sx',
                            'XDG_RUNTIME_DIR': PROD_RUNTIME, 'NIRI_SOCKET': socket},
                       capture_output=True, text=True, timeout=15)
    return json.loads(p.stdout) if p.returncode == 0 else []


def park_window(socket, pid):
    """把人能看见的那一面搬到隐藏工作区：不抢焦点，也不切视图。"""
    for win in prod_windows(socket):
        if win.get('pid') != pid:
            continue
        subprocess.run(['niri', 'msg', 'action', 'move-window-to-workspace',
                        '--window-id', str(win['id']), '--focus', 'false', PARK_WORKSPACE],
                       env={'PATH': '/usr/local/bin:/usr/bin:/bin', 'HOME': '/home/sx',
                            'XDG_RUNTIME_DIR': PROD_RUNTIME, 'NIRI_SOCKET': socket},
                       capture_output=True, text=True, timeout=15)
        return win['id'], win.get('is_focused')
    return None, None


def read_log(name):
    try:
        return (RUN / (name + '.log')).read_text()
    except OSError:
        return ''


try:
    parent_wayland = prod_wayland()
    if not parent_wayland:
        raise RuntimeError('production compositor wayland socket not found; is niri running?')
    socket = prod_socket()
    if not socket:
        raise RuntimeError('production niri IPC socket not found')

    env = os.environ.copy()
    env.update(HOME='/home/sx', PATH='/usr/local/bin:/usr/bin:/bin',
               XDG_RUNTIME_DIR=PROD_RUNTIME, WAYLAND_DISPLAY=parent_wayland)
    for k in ['NIRI_SOCKET', 'DISPLAY', 'WAYLAND_SOCKET', 'XDG_ACTIVATION_TOKEN',
              'DESKTOP_STARTUP_ID', 'WINIT_UNIX_BACKEND']:
        env.pop(k, None)

    niri = spawn([NIRI, '-c', str(ROOT / 'poc.kdl')], 'niri', env)

    def find(pattern):
        m = re.search(pattern, read_log('niri'))
        return m.group(1) if m else None

    wayland = until(lambda: find(r'listening on Wayland socket: (\S+)'))
    ipc = until(lambda: find(r'IPC listening on: (\S+)'))
    xdisplay = until(lambda: find(r'listening on X11 socket: (:\d+)'))
    if xdisplay == ':0':
        raise RuntimeError('refusing the production X display')

    # 嵌套桌面在人的合成器上是一个窗口：必须待在 ue，且不许抢焦点。
    def locate():
        wid, focused = park_window(socket, niri.pid)
        return (wid, focused) if wid else None

    parent_window, was_focused = until(locate)
    if was_focused:
        subprocess.run(['niri', 'msg', 'action', 'focus-window', '--id', str(parent_window)],
                       env={'PATH': '/usr/local/bin:/usr/bin:/bin', 'HOME': '/home/sx',
                            'XDG_RUNTIME_DIR': PROD_RUNTIME, 'NIRI_SOCKET': socket},
                       capture_output=True, text=True, timeout=15)

    data = dict(display=xdisplay, wayland=wayland, ipc=str(ipc), runtime=PROD_RUNTIME,
                parent_wayland=parent_wayland, parent_window=parent_window,
                park_workspace=PARK_WORKSPACE, pids={name: p.pid for name, p in children})
    (RUN / 'environment.json').write_text(json.dumps(data, indent=2))
    print('READY ' + json.dumps(data), flush=True)
    until(lambda: (RUN / 'STOP').exists(), seconds=7200)
except BaseException:
    traceback.print_exc()
    raise
finally:
    for name, p in reversed(children):
        if p.poll() is None:
            p.terminate()
    for name, p in reversed(children):
        try:
            p.wait(timeout=6)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait(timeout=5)
    for f in files:
        f.close()
    (RUN / 'cleanup.json').write_text(json.dumps({name: p.returncode for name, p in children}))
    print('CLEANED', flush=True)
