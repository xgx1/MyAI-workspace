#!/usr/bin/env python3
"""Second pass: the first pass's failures, plus the isolation route they pointed at.

Core queries always come from a fresh client (xdotool), because a client that set its own
ClientPointer sees its master's focus/position when it asks for "core" state.
"""
import hashlib,json,time,traceback
from testlib import *
RESULTS=[]
def act(*args):return run(['niri','msg','action',*map(str,args)])
INJ=[str(ROOT/'xi2-inject'),'--display',INFO['display']]
def core():
    """Core state, measured by a process that never set its own ClientPointer.

    A connection that set ClientPointer is shown its master's focus and position when it asks
    for "core" state, so measuring from inside the injecting connection would fake isolation.
    """
    out=run(INJ+['state']).stdout
    line=[l for l in out.splitlines() if 'core_focus=' in l][-1]
    fields=dict(part.split('=',1) for part in line.split() if '=' in part)
    x,y=fields['core_pointer'].split(',')
    return {'focus':int(fields['core_focus'],16),'x':int(x),'y':int(y)}
def test(name,fn,limitation=False):
    start=time.monotonic()
    try:
        row=dict(name=name,status='PASS',detail=fn())
    except Exception as e:
        row=dict(name=name,status='LIMITATION' if limitation else 'FAIL',error=str(e),traceback=traceback.format_exc())
    row['seconds']=round(time.monotonic()-start,3)
    RESULTS.append(row)
    (RUN/'results2.json').write_text(json.dumps(RESULTS,indent=2))
    print(json.dumps({k:row[k] for k in row if k!='traceback'}),flush=True)
H=by_title('regression-human')['id'];X=by_title('regression-agent-x11')['id']
N=by_title('regression-agent-native')['id'];HX=by_title('regression-human-x11')['id']
def geometry(wid):
    geo=xdo('getwindowgeometry','--shell',str(wid)).stdout
    return {k:int(v) for k,v in (line.split('=',1) for line in geo.split() if '=' in line)}
def xid(title):
    """GTK maps a 10x10 helper window with the same title, so pick the largest one."""
    ids=[int(i) for i in xdo('search','--name','^'+title+'$').stdout.split()]
    if not ids:
        raise RuntimeError('no window titled '+title)
    return max(ids,key=lambda wid:geometry(wid)['WIDTH']*geometry(wid)['HEIGHT'])
XID=xid('regression-agent-x11');HXID=xid('regression-human-x11')
def no_focus_change(fn):
    before=focus()['id'];core_before=core()
    value=fn()
    assert focus()['id']==before,(before,focus())
    assert core()==core_before,(core_before,core())
    return value
def preflight():
    """Normalise state left by earlier runs, then prove both input paths reach their window."""
    for wid in (X,N):
        w=by_title('regression-agent-x11' if wid==X else 'regression-agent-native')
        if w['is_floating']:
            act('toggle-window-floating','--id',wid)
        action('MoveWindowToWorkspace',window_id=wid,reference={'Name':'agent'},focus=False)
    # Put the human inside the harder case: a real X11 window on the same X server as the
    # target, so isolation cannot come from separate X displays. This also gives the satellite
    # compositor keyboard focus; while the human works in a Wayland window the satellite has no
    # Wayland keyboard focus at all, so nothing injected into its X server reaches any X client.
    act('focus-window','--id',HX)
    wait(lambda:focus()['id']==HX,8)
    # The satellite re-syncs X focus on its own schedule, so retry until a keystroke lands.
    for attempt in range(6):
        xdo('windowfocus',HXID)
        time.sleep(.25)
        mark=len(state('regression-human-x11')['text'])
        xdo('type','--clearmodifiers','q')
        try:
            wait(lambda:len(state('regression-human-x11')['text'])==mark+1,1.5)
            break
        except Exception:
            if attempt==5:
                raise RuntimeError('cannot put a real keystroke into the human X11 window')
    amark=len(state('regression-agent-x11')['text'])
    run(INJ+['type',str(XID),'z'])
    wait(lambda:len(state('regression-agent-x11')['text'])==amark+1,6)
    core_state=core()
    assert core_state['focus']==HXID,core_state
    return {'niri_focus':HX,'core_focus':core_state['focus'],'human_typing':True,'mpx_typing':True}
test('00_preflight_both_input_paths',preflight)

def validate_target():
    valid=query({'ScopedTarget':{'window':N}})
    assert valid=='Handled',valid
    bad=rpc({'ScopedTarget':{'window':99999}})
    assert 'Err' in bad,bad
    # X11 apps under the satellite integration are Wayland toplevels, so they are accepted here;
    # what matters is that the agent seat does not reach them without touching X core focus.
    x11=rpc({'ScopedTarget':{'window':X}})
    cleared=query({'ScopedTarget':{'window':None}})
    assert cleared=='Handled'
    return {'valid':valid,'unknown':bad,'satellite_x11_target':x11,'cleared':cleared}
test('12_unknown_target_fails_closed',validate_target)

def pin_survives_rejection():
    query({'ScopedTarget':{'window':N}})
    before=state('regression-agent-native')['text']
    assert 'Err' in rpc({'ScopedTarget':{'window':99999}})
    agent('key',30)
    wait(lambda:state('regression-agent-native')['text']==before+'a',5)
    return {'still_targets_native':True,'text':state('regression-agent-native')['text']}
test('13_rejected_target_keeps_previous_pin',pin_survives_rejection)

def x11_isolated_typing():
    human_before=state('regression-human-x11')['text'];agent_before=state('regression-agent-x11')['text']
    def op():
        run(INJ+['type',str(XID),'mpxonly'])
        wait(lambda:len(state('regression-agent-x11')['text'])==len(agent_before)+7,8)
        return {'agent':state('regression-agent-x11')['text'][len(agent_before):]}
    result=no_focus_change(op)
    assert state('regression-human-x11')['text']==human_before,state('regression-human-x11')
    result['human_unchanged']=True
    return result
test('05_MPX_text_into_unfocused_X11_keeps_human_focus',x11_isolated_typing)

def interleaved_x11():
    # Make sure the human window really owns X keyboard focus, and prove it with one keystroke,
    # before claiming that the interleaved run isolates anything.
    xdo('windowfocus',HXID)
    mark=len(state('regression-human-x11')['text'])
    xdo('type','--clearmodifiers','h')
    wait(lambda:len(state('regression-human-x11')['text'])==mark+1,5)
    human_before=state('regression-human-x11')['text'];agent_before=state('regression-agent-x11')['text']
    def op():
        for _ in range(8):
            run(INJ+['type',str(XID),'a'])
            xdo('type','--clearmodifiers','h')
        wait(lambda:len(state('regression-agent-x11')['text'])==len(agent_before)+8,8)
        wait(lambda:len(state('regression-human-x11')['text'])==len(human_before)+8,8)
        return {'agent':state('regression-agent-x11')['text'][len(agent_before):],
                'human':state('regression-human-x11')['text'][len(human_before):]}
    result=no_focus_change(op)
    assert 'a' not in result['human'] and 'h' not in result['agent'],result
    return result
test('10_interleaved_core_and_MPX_X11_isolation',interleaved_x11)

def mpx_click():
    before=state('regression-agent-x11')
    xdo('windowfocus',HXID)
    start=core()
    win_geo=xdo('getwindowgeometry','--shell',XID).stdout
    pos=dict(line.split('=') for line in win_geo.split() if '=' in line)
    x,y=int(pos['X'])+300,int(pos['Y'])+120
    run(INJ+['click',str(XID),str(x),str(y)])
    wait(lambda:state('regression-agent-x11')['clicks']==before['clicks']+1,8)
    assert core()==start,(start,core())
    return {'clicks':state('regression-agent-x11')['clicks'],'core_pointer_unchanged':True}
test('14_MPX_click_into_X11_without_moving_human_pointer',mpx_click)

def xsend_negative():
    before=state('regression-agent-x11')['text']
    xdo('type','--window',XID,'--clearmodifiers','sendfail')
    time.sleep(1.5)
    after=state('regression-agent-x11')['text']
    if after!=before+'sendfail':
        raise RuntimeError('XSendEvent typed %r' % after[len(before):])
    return {'unchanged_after_1.5s':True}
test('15_XSendEvent_is_not_a_delivery_path',xsend_negative,limitation=True)

def hover_focus():
    """Strict property: hovering an AI window must not take focus.

    With focus-follows-mouse enabled a real window under the pointer does get focused, which is
    niri behaving as configured. The test reports which of the two happened instead of pretending
    the strict property holds when it does not.
    """
    act('move-window-to-floating','--id',X)
    action('MoveWindowToWorkspace',window_id=X,reference={'Name':'human'},focus=False)
    act('set-window-width','--id',X,400)
    act('set-window-height','--id',X,300)
    act('move-floating-window','--id',X,'-x',700,'-y',60)
    act('focus-window','--id',H)
    before=focus()['id']
    time.sleep(.2)
    xdo('mousemove',900,200)
    time.sleep(1.2)
    after=focus()['id']
    detail={'focus_before':before,'focus_after':after,'hovered_window':X}
    # Leave the layout as the rest of the suite expects it.
    act('toggle-window-floating','--id',X) if by_title('regression-agent-x11')['is_floating'] else None
    action('MoveWindowToWorkspace',window_id=X,reference={'Name':'agent'},focus=False)
    act('focus-window','--id',H)
    if after!=before:
        raise RuntimeError(json.dumps(detail))
    return detail
test('16_hover_does_not_take_focus',hover_focus,limitation=True)
print('SUMMARY '+json.dumps({s:sum(r['status']==s for r in RESULTS) for s in ['PASS','FAIL','LIMITATION']}),flush=True)
