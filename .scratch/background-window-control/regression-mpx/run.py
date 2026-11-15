#!/usr/bin/env python3
"""Only starts and inputs into this process's own nested compositor; cleans that exact PID.

原版用 Xvfb 当"独立 X 服务器"：Xvfb 已经从本机卸掉，改成起一个**嵌套 niri**
（生产合成器的 Wayland 客户端），用它自己拉起的 xwayland-satellite 当那台独立的
X 服务器。每轮一台新的，既不共享人的 :0，也不需要任何裸 X server。
"""
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
PROD_RUNTIME = '/run/user/1000'
NIRI = os.environ.get('NIRI_BIN', '/home/sx/projects/niri/target/debug/niri')
ENV = dict(os.environ, DISPLAY='', WAYLAND_DISPLAY='', XDG_RUNTIME_DIR=PROD_RUNTIME)
ENV.pop('NIRI_SOCKET', None)
ENV.pop('WAYLAND_SOCKET', None)
owned = []


def prod_wayland():
    out = subprocess.run(['systemctl', '--user', 'show-environment'],
                         capture_output=True, text=True, timeout=10).stdout
    for line in out.splitlines():
        if line.startswith('WAYLAND_DISPLAY='):
            name = line.split('=', 1)[1].strip()
            if os.path.exists(os.path.join(PROD_RUNTIME, name)):
                return name
    for cand in sorted(Path(PROD_RUNTIME).glob('wayland-*')):
        if not cand.name.endswith('.lock'):
            return cand.name
    raise RuntimeError('production Wayland socket not found')


def start_x_server(iteration):
    """一台只有本进程在用的 X 服务器：嵌套 niri + 它自带的 satellite。"""
    log = (ROOT / f'nested-{iteration}.log').open('w')
    env = dict(ENV, WAYLAND_DISPLAY=prod_wayland())
    p = subprocess.Popen([NIRI, '-c', str(ROOT / 'mpx.kdl')], env=env,
                         stdout=log, stderr=subprocess.STDOUT)
    deadline = time.monotonic() + 25
    display = ipc = None
    while time.monotonic() < deadline and p.poll() is None:
        try:
            text = (ROOT / f'nested-{iteration}.log').read_text()
        except OSError:
            text = ''
        m = re.search(r'listening on X11 socket: (:\d+)', text)
        if m:
            display = m.group(1)
        m = re.search(r'IPC listening on: (\S+)', text)
        if m:
            ipc = m.group(1)
        if display and ipc:
            return p, display, ipc, log
        time.sleep(.1)
    p.terminate()
    raise RuntimeError(f'nested niri PID {p.pid}: no X11 socket within 25s')


with (ROOT / 'commands.log').open('w') as transcript:
    def run(argv, expected=0, env=ENV, log=None):
        transcript.write('$ ' + shlex.join(map(str, argv)) + '\n')
        transcript.flush()
        p = subprocess.run(argv, env=env, text=True, capture_output=True, timeout=20)
        text = p.stdout + p.stderr
        if p.returncode != expected:
            (ROOT / 'failure.log').write_text(text)
        transcript.write(text + f'EXIT {p.returncode}\n')
        transcript.flush()
        if log:
            (ROOT / log).write_text(text)
        if p.returncode != expected:
            raise RuntimeError(f'{argv!r}: expected {expected}, got {p.returncode}\n{text[-2500:]}')
        return text

    run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-O2', 'xi2-tool.c', '-o', 'xi2-tool', '-lXi', '-lX11'])
    # satellite 上的结构性检查；裸 Xvfb 时代的完整 selftest 已不适用（见 selftest.c 注释）。
    run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-O2', 'satellite-check.c',
         '-o', 'satellite-check', '-lXi', '-lX11'])
    tool = str(ROOT / 'xi2-tool')
    for invalid in (':0', ':0.0', ':00', 'localhost:0', ':garbage'):
        run([tool, '--display', invalid, 'query'], expected=2)
    run([tool], expected=2, env=dict(ENV, DISPLAY=':0'))
    if not Path('/tmp/.X11-unix/X0').is_socket():
        raise RuntimeError('X0 socket absent; the production display check would be meaningless')
    try:
        for iteration in range(1, 4):
            p, display, ipc, log = start_x_server(iteration)
            owned.append({'iteration': iteration, 'pid': p.pid, 'display': display, 'ipc': ipc})
            try:
                if display == ':0':
                    raise RuntimeError(f'Refusing display {display!r}')
                env = dict(ENV, DISPLAY=display, MPX_NESTED_NIRI_PID=str(p.pid),
                           NIRI_SOCKET=ipc)
                transcript.write(f'ENV DISPLAY={display} WAYLAND_DISPLAY=<production> '
                                 f'OWN_NIRI_PID={p.pid}\n')
                run([tool, '--display', display, 'query'], env=env)
                created = run([tool, '--display', display, 'create', 'mpx-helper'], env=env)
                pointer = next(int(line.split()[0].split('=')[1]) for line in created.splitlines()
                               if 'name=mpx-helper pointer' in line)
                run([tool, '--display', display, 'remove', str(pointer)], env=env)
                run([str(ROOT / 'satellite-check'), display], env=env, log=f'run-{iteration}.log')
                owned[-1]['selftest_rc'] = 0
                print(f'PASS run={iteration} display={display} owned_niri_pid={p.pid}', flush=True)
            finally:
                if p.poll() is None:
                    p.terminate()
                    try:
                        p.wait(timeout=8)
                    except subprocess.TimeoutExpired:
                        p.kill()
                        p.wait(timeout=5)
                log.close()
                owned[-1]['niri_exit'] = p.returncode
                owned[-1]['reaped'] = p.poll() is not None
                (ROOT / 'owned-processes.json').write_text(json.dumps(owned, indent=2) + '\n')
                transcript.write(f'CLEANUP exact_pid={p.pid} exit={p.returncode} '
                                 f'reaped={p.poll() is not None}\n')
                transcript.flush()
    finally:
        (ROOT / 'owned-processes.json').write_text(json.dumps(owned, indent=2) + '\n')
print('PASS all 3 fresh-server runs on nested niri satellites; all owned compositors reaped')
