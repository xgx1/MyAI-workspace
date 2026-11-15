#!/usr/bin/env python3
"""Public IPC/real GUI regression, with full focus history and explicit expected limitations."""
import hashlib,json,select,socket,time,traceback
from testlib import *
RESULTS=[]
class Monitor:
    def __init__(self):
        self.s=socket.socket(socket.AF_UNIX);self.s.connect(INFO['ipc'])
        self.s.sendall(b'"EventStream"\n');self.buf=b'';self.drain()
    def drain(self):
        events=[]
        while select.select([self.s],[],[],.04)[0]:
            part=self.s.recv(1<<20)
            if not part:break
            self.buf+=part
            while b'\n' in self.buf:
                line,self.buf=self.buf.split(b'\n',1)
                if line:events.append(json.loads(line))
        return events
MON=Monitor()
def act(*args):return run(['niri','msg','action',*map(str,args)])
def test(name,fn,limitation=False):
    MON.drain();start=time.monotonic()
    try:
        detail=fn()
        row=dict(name=name,status='PASS',detail=detail)
    except Exception as e:
        row=dict(name=name,status='LIMITATION' if limitation else 'FAIL',error=str(e),traceback=traceback.format_exc())
    row['seconds']=round(time.monotonic()-start,3)
    row['events']=MON.drain()
    RESULTS.append(row)
    (RUN/'results.json').write_text(json.dumps(RESULTS,indent=2))
    print(json.dumps(row),flush=True)
def preserved(call,baseline=None):
    baseline=baseline or focus()['id'];MON.drain()
    value=call()
    assert focus()['id']==baseline,(baseline,focus())
    events=MON.drain()
    transitions=[e['WindowFocusChanged'] for e in events if 'WindowFocusChanged' in e]
    assert all(e.get('id')==baseline for e in transitions),transitions
    return dict(result=value,focus=baseline,focus_transitions=transitions)
H=by_title('regression-human')['id'];X=by_title('regression-agent-x11')['id'];N=by_title('regression-agent-native')['id'];HX=by_title('regression-human-x11')['id']

def wid_area(title):
    """GTK maps a tiny helper window with the same title, so take the largest one."""
    best=(0,0)
    for line in xdo('search','--name','^'+title+'$').stdout.split():
        geometry={}
        for row in xdo('getwindowgeometry','--shell',line).stdout.splitlines():
            if '=' in row:
                key,value=row.split('=',1);geometry[key]=value
        area=int(geometry['WIDTH'])*int(geometry['HEIGHT'])
        if area>best[0]:best=(area,int(line))
    assert best[1],('no X window named '+title)
    return best[1]

def initial():
    assert focus()['id']==H
    assert by_title('regression-agent-x11')['workspace_id']!=focus()['workspace_id']
    assert len({H,X,N,HX})==4
    return {'ids':[H,X,N,HX],'focus':H,'isolated_display':INFO['display'],
            'parent_wayland':INFO['parent_wayland'],'parent_window':INFO['parent_window'],
            'park_workspace':INFO['park_workspace']}
test('01_original_windows_map_without_activation',initial)

def floating():
    def op():
        act('move-window-to-floating','--id',X)
        assert by_title('regression-agent-x11')['is_floating']
        return by_title('regression-agent-x11')
    return preserved(op)
test('02_background_X11_convert_to_floating',floating)

def move_here():
    def op():
        ws=focus()['workspace_id']
        action('MoveWindowToWorkspace',window_id=X,reference={'Id':ws},focus=False)
        act('set-window-width','--id',X,400)
        act('set-window-height','--id',X,320)
        act('move-floating-window','--id',X,'-x',800,'-y',80)
        assert by_title('regression-agent-x11')['workspace_id']==ws
        return by_title('regression-agent-x11')
    result=preserved(op)
    # 以前抓父 X display 证明"内容确实出现了"；现在父表面是生产 Wayland，
    # 用这个嵌套桌面自己的 grim 抓同一屏（父 X server 已经没有了）。
    run(['grim',str(RUN/'03-visible.png')])
    return result
test('03_show_original_X11_no_focus',move_here)

def capture_background():
    action('MoveWindowToWorkspace',window_id=X,reference={'Name':'agent'},focus=False)
    path=shot(X,'04-background-capture')
    assert focus()['id']==H
    return {'png_bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'focus':H}
test('04_single_request_hidden_workspace_PNG_complete',capture_background)

def text_send_event():
    """Measured property: XSendEvent is not a delivery path for this toolkit, so it cannot be
    the mechanism behind background typing. The supported path is the agent X11 master."""
    xid=wid_area('regression-agent-x11')
    before=state('regression-agent-x11')['text'];human_before=state('regression-human')['text']
    result=preserved(lambda:xdo('type','--window',xid,'--clearmodifiers','quiet123').stdout)
    time.sleep(1.5)
    after=state('regression-agent-x11')['text']
    assert state('regression-human')['text']==human_before
    if after!=before:
        raise RuntimeError('XSendEvent unexpectedly delivered %r'%after[len(before):])
    raise RuntimeError('XSendEvent delivered nothing (text stayed %r, xid %d); per-window X11 '
                       'input uses the agent X11 master, see suite2 05/10/14'%(after,xid))
test('05_XSendEvent_is_not_a_delivery_path',text_send_event,limitation=True)

def native_keyboard():
    query({'ScopedTarget':{'window':N}})
    before=state('regression-agent-native')['text'];human_before=state('regression-human')['text']
    result=preserved(lambda:agent('key',30).stdout)
    wait(lambda:state('regression-agent-native')['text']==before+'a')
    assert state('regression-human')['text']==human_before
    result['text']=state('regression-agent-native')['text'];return result
test('06_native_agent_seat_keyboard_only',native_keyboard)

def x11_scoped_keyboard():
    query({'ScopedTarget':{'window':X}})
    before=state('regression-agent-x11')['text'];human_before=state('regression-human')['text']
    result=preserved(lambda:agent('key',48).stdout)
    wait(lambda:state('regression-agent-x11')['text']==before+'b')
    assert state('regression-human')['text']==human_before
    result['text']=state('regression-agent-x11')['text'];return result
test('07_X11_agent_seat_keyboard_only',x11_scoped_keyboard)

def repeated_visibility():
    def op():
        for i in range(30):
            action('MoveWindowToWorkspace',window_id=X,reference={'Name':'human'},focus=False)
            assert by_title('regression-agent-x11')['workspace_id']==focus()['workspace_id']
            action('MoveWindowToWorkspace',window_id=X,reference={'Name':'agent'},focus=False)
        return {'rounds':30,'same_id':by_title('regression-agent-x11')['id']}
    return preserved(op)
test('08_thirty_show_hide_roundtrips_no_activation',repeated_visibility)

def simultaneous_native():
    query({'ScopedTarget':{'window':N}})
    b=state('regression-agent-native')['text'];h=state('regression-human')['text']
    act('focus-window','--id',H)
    def op():
        for _ in range(12):
            human('key',35);agent('key',30)
        wait(lambda:state('regression-human')['text']==h+'h'*12)
        wait(lambda:state('regression-agent-native')['text']==b+'a'*12)
        return {'human':state('regression-human')['text'],'agent':state('regression-agent-native')['text']}
    return preserved(op)
test('09_interleaved_human_and_native_agent_keys',simultaneous_native)

def both_x11():
    """Both windows are X11 clients of the same satellite X server and the human works in one of
    them, which is what gives the satellite Wayland keyboard focus at all. Human input is real X
    input on the core pair, agent input is the extra master, so the test measures separation
    rather than assuming it."""
    INJ=[str(ROOT/'xi2-inject'),'--display',INFO['display']]
    query({'ScopedTarget':{'window':X}})
    act('focus-window','--id',HX)
    wait(lambda:focus()['id']==HX,8)
    xid=wid_area('regression-agent-x11');hxid=wid_area('regression-human-x11')
    for _ in range(6):
        xdo('windowfocus',hxid);time.sleep(.25)
        length=len(state('regression-human-x11')['text'])
        xdo('type','--clearmodifiers','h')
        if len(state('regression-human-x11')['text'])>length:break
    b=state('regression-agent-x11')['text'];h=state('regression-human-x11')['text']
    def op():
        for _ in range(8):
            xdo('type','--clearmodifiers','h')
            run(INJ+['type',str(xid),'a'])
        wait(lambda:state('regression-human-x11')['text']==h+'h'*8,6)
        wait(lambda:state('regression-agent-x11')['text']==b+'a'*8,6)
        return {'human':state('regression-human-x11')['text'],'agent':state('regression-agent-x11')['text']}
    return preserved(op,HX)
test('10_shared_X11_human_agent_key_isolation',both_x11)
act('focus-window','--id',H)

def capture_repeat():
    sizes=[]
    for i in range(12):sizes.append(shot(X,'11-single-'+str(i)).stat().st_size)
    assert focus()['id']==H
    return {'requests':len(sizes),'sizes':sizes}
test('11_twelve_unique_single_request_captures',capture_repeat)

def invalid():
    before=focus()['id']
    result=rpc({'ScopedTarget':{'window':99999}})
    assert 'Err' in result,result
    out=run([SHOT,'99999',str(RUN/'12-invalid.png')],check=False)
    assert out.returncode!=0,out.stdout+out.stderr
    assert 'no window with id 99999' in out.stdout+out.stderr,out.stdout+out.stderr
    assert not (RUN/'12-invalid.png').exists()
    assert focus()['id']==before
    return {'pin_error':result,'capture_error':out.stderr+out.stdout}
test('12_invalid_target_fails_closed',invalid)

def human_floating():
    act('move-window-to-floating','--id',H)
    def op():
        action('MoveWindowToWorkspace',window_id=X,reference={'Name':'human'},focus=False)
        act('move-floating-window','--id',X,'-x',800,'-y',80)
        return {'human_floating':focus()['is_floating'],'same_target':X}
    return preserved(op)
test('13_show_X11_above_floating_human_without_activation',human_floating)

def hover():
    """focus-follows-mouse is on in the human's config, so the pointer crossing a window normally
    focuses it. The window the agent controls is exempt: moving over it is not a request to work
    in it, and letting it take the session focus would hand the agent's keystrokes to the human
    and the human's to the agent.

    父 X server 已经没有了（Xvfb 卸载），所以"人"的指针现在走这个嵌套桌面自己的
    winit 席位：绝对坐标是输出尺寸的千分数，先把 agent 窗口铺满大半屏，再把指针对准它。"""
    query({'ScopedTarget':{'window':X}})
    act('move-window-to-floating','--id',X)
    act('set-window-width','--id',X,900)
    act('set-window-height','--id',X,700)
    act('move-floating-window','--id',X,'-x',0,'-y',0)
    act('move-floating-window','--id',H,'-x',40,'-y',760)
    human('click',500,500)
    act('focus-window','--id',H)
    before=focus()['id']
    assert before!=X,(before,'the agent window was focused before the hover')
    human_motion(500,500)
    time.sleep(1.0)
    after=focus()['id']
    assert after==before,'focus-follows-mouse activated the pinned agent window: '+str(after)
    return {'focus_before':before,'focus_after':after,'hovered_window':X,'pointer_permille':[500,500]}
test('14_strict_no_focus_when_human_hovers_real_window',hover)
act('focus-window','--id',H)
print('SUMMARY '+json.dumps({s:sum(r['status']==s for r in RESULTS) for s in ['PASS','FAIL','LIMITATION']}),flush=True)
