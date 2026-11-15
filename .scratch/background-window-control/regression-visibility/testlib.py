import json,os,pathlib,socket,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parent
RUN=ROOT/'run'
INFO=json.loads((RUN/'environment.json').read_text())
# 嵌套桌面挂在生产合成器上（不再是 Xvfb）：X 显示只给 X11 客户端用，
# 人的那一面是生产 Wayland，嵌套窗口被 park 到隐藏工作区。
assert INFO['display']!=':0'
assert INFO['parent_wayland'] and INFO['park_workspace']
assert INFO['ipc'].startswith(INFO['runtime'])
ENV=os.environ.copy()
ENV.update(HOME='/home/sx',PATH='/usr/local/bin:/usr/bin:/bin',XDG_RUNTIME_DIR=INFO['runtime'],WAYLAND_DISPLAY=INFO['wayland'],NIRI_SOCKET=INFO['ipc'],GTK_USE_PORTAL='0',NO_AT_BRIDGE='1',GDK_SCALE='1')
ENV.pop('DISPLAY',None)
ENV.pop('XDG_ACTIVATION_TOKEN',None)
PROBE='/home/sx/projects/agent-seat-probe/target/debug/agent-seat-probe'
SHOT='/home/sx/projects/agent-seat-probe/target/debug/scoped-shot'
def rpc(request):
    with socket.socket(socket.AF_UNIX) as sock:
        sock.settimeout(20);sock.connect(INFO['ipc'])
        sock.sendall((json.dumps(request)+'\n').encode())
        with sock.makefile('r') as f:return json.loads(f.readline())
def query(request):
    ans=rpc(request)
    if 'Err' in ans:raise RuntimeError(ans)
    return ans['Ok']
def windows():return query('Windows')['Windows']
def focus():return query('FocusedWindow')['FocusedWindow']
def workspaces():return query('Workspaces')['Workspaces']
def action(name,**kwargs):return query({'Action':{name:kwargs}})
def act(*args):return run(['niri','msg','action',*map(str,args)])
def wait(fn,timeout=15):
    end=time.monotonic()+timeout
    last=None
    while time.monotonic()<end:
        last=fn()
        if last:return last
        time.sleep(.025)
    raise TimeoutError(str(last))
def by_title(title):return next((w for w in windows() if w['title']==title),None)
def spawn_app(name,backend):
    env=ENV.copy();env['GDK_BACKEND']=backend
    if backend=='x11':env['DISPLAY']=INFO['display']
    log=open(RUN/(name+'.log'),'w')
    p=subprocess.Popen(['python3',str(ROOT/'app.py'),name,str(RUN/(name+'.json'))],env=env,stdout=log,stderr=subprocess.STDOUT)
    wait(lambda:by_title(name))
    wait(lambda:state(name).get('ready'))
    return p

def state(name):
    p=RUN/(name+'.json')
    return json.loads(p.read_text()) if p.exists() else {}
def run(argv,env=None,check=True):
    p=subprocess.run(argv,env=env or ENV,text=True,capture_output=True,timeout=25)
    if check and p.returncode:raise RuntimeError((argv,p.returncode,p.stdout,p.stderr))
    return p
def agent(*args):return run([PROBE,'agent-0',*map(str,args)])
def human(*args):return run([PROBE,'winit',*map(str,args)])
def human_motion(x,y):
    """把嵌套桌面里"人"的指针挪到 (x,y)（千分数）：悬停测试用，不碰真实指针。"""
    return human('motion',int(x),int(y))
def xdo(*args,check=True):
    """X11 客户端那一侧的输入（satellite 的 X display）。人的那一面没有 X server 了。"""
    env=ENV.copy();env['DISPLAY']=INFO['display']
    return run(['xdotool',*map(str,args)],env=env,check=check)
def shot(wid,name):
    path=RUN/(name+'.png')
    if path.exists():raise RuntimeError('fresh capture path required')
    p=run([SHOT,str(wid),str(path)])
    assert path.exists() and path.stat().st_size>100,'reply preceded PNG write'
    assert path.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
    return path
