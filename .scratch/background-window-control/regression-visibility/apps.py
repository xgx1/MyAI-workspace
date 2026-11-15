import json,time,traceback
from testlib import *
children=[]
try:
    for name,backend in [('regression-human','wayland'),('regression-agent-x11','x11'),('regression-agent-native','wayland'),('regression-human-x11','x11')]:
        children.append(spawn_app(name,backend))
    (RUN/'apps.json').write_text(json.dumps([p.pid for p in children]))
    print(json.dumps(windows()),flush=True)
    while not (RUN/'STOP-APPS').exists():
        if any(p.poll() is not None for p in children):raise RuntimeError('fixture child exited')
        time.sleep(.1)
finally:
    for p in children:
        if p.poll() is None:p.terminate()
    for p in children:
        try:p.wait(timeout=5)
        except subprocess.TimeoutExpired:p.kill();p.wait()
