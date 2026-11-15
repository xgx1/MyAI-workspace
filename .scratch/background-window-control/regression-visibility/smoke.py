#!/usr/bin/env python3
"""按技能里写的那几条命令走一遍：环境活着，并且文档里的每个命令都真的能跑通。

    python3 cycle.py 1 smoke.py

和 suite.py 的区别：suite 记录回归结论（含故意失败的限制项），smoke 只回答
「这套能力现在在我这台机器上还能不能用」，失败即停，一条命令一步。
"""
import json,time,traceback
from testlib import *

TARGET='/home/sx/projects/agent-seat-probe/target/debug/scoped-target'
ROWS=[]

def step(name,fn):
    start=time.monotonic()
    try:
        detail=fn()
        row=dict(name=name,status='PASS',detail=detail)
    except Exception as e:
        row=dict(name=name,status='FAIL',error=str(e),traceback=traceback.format_exc())
    row['seconds']=round(time.monotonic()-start,3)
    ROWS.append(row)
    (RUN/'results.json').write_text(json.dumps(ROWS,indent=2))
    print(json.dumps(row),flush=True)

def preflight():
    """环境里必须是人拿着焦点、agent 窗口在另一个 workspace。"""
    H=by_title('regression-human')['id']
    assert focus()['id']==H,('focus',focus())
    X=by_title('regression-agent-x11')['id']
    assert by_title('regression-agent-x11')['workspace_id']!=by_title('regression-human')['workspace_id']
    return {'focus':H,'agent_x11':X,'workspace':by_title('regression-agent-x11')['workspace_id']}
step('01_environment_alive',preflight)

def show_without_focus():
    """niri msg action：转浮窗 → 搬到人所在的 workspace（focus=false）→ 定位。焦点不许变。"""
    H=by_title('regression-human')['id'];X=by_title('regression-agent-x11')['id']
    before=focus()['id']
    act('move-window-to-floating','--id',X)
    action('MoveWindowToWorkspace',window_id=X,
           reference={'Id':by_title('regression-human')['workspace_id']},focus=False)
    act('set-window-width','--id',X,400)
    act('set-window-height','--id',X,320)
    act('move-floating-window','--id',X,'-x',800,'-y',80)
    win=by_title('regression-agent-x11')
    assert win['is_floating'],win
    assert win['workspace_id']==by_title('regression-human')['workspace_id'],win
    assert not win['is_focused'],win
    assert focus()['id']==before,('focus',before,focus())
    return {'window':X,'focus_after':focus()['id'],'floating':win['is_floating']}
step('02_show_original_window_without_focus',show_without_focus)

def unknown_target_fails_closed():
    """scoped-target 对未知 id 必须非 0 退出，否则调用方会以为已经切走了。"""
    p=run([TARGET,'99999'],check=False)
    assert p.returncode!=0,(p.returncode,p.stdout,p.stderr)
    assert 'no window with id 99999' in p.stderr,p.stderr
    return {'exit':p.returncode,'stderr':p.stderr.strip()}
step('03_unknown_target_fails_closed',unknown_target_fails_closed)

def pin_and_type():
    """scoped-target 选中窗口后，agent-0 席位的虚拟键盘只进这个窗口。"""
    X=by_title('regression-agent-x11')['id']
    # 席位只决定"生产合成器把键发给哪个顶层窗口"；嵌套合成器内部还要它自己把焦点放在 X 上，
    # 否则键会落进同一个桌面里被聚焦的另一个窗口（agent 真正接管时本来就会先聚焦目标窗口）。
    act('focus-window','--id',X)
    wait(lambda:by_title('regression-agent-x11')['is_focused'])
    p=run([TARGET,str(X)])
    assert 'handled' in p.stdout,p.stdout
    before=state('regression-agent-x11')['text'];human_before=state('regression-human')['text']
    agent('key',30)  # evdev 30 = a
    wait(lambda:state('regression-agent-x11')['text']==before+'a')
    assert state('regression-human')['text']==human_before,state('regression-human')['text']
    return {'agent_text':state('regression-agent-x11')['text'],'human_text':state('regression-human')['text']}
step('04_scoped_keyboard_into_pinned_window',pin_and_type)

def capture():
    """scoped-shot：单次请求直出 PNG，回复到达时文件已在盘上。"""
    X=by_title('regression-agent-x11')['id']
    path=shot(X,'smoke-capture')
    return {'png_bytes':path.stat().st_size,'focus':focus()['id']}
step('05_scoped_screenshot',capture)

def release():
    """收尾：解除 pin，席位不再往任何窗口投递。"""
    p=run([TARGET,'none'])
    assert 'handled' in p.stdout,p.stdout
    return {'stdout':p.stdout.strip(),'focus':focus()['id']}
step('06_release_scoped_target',release)

if any(row['status']=='FAIL' for row in ROWS):
    raise SystemExit(1)
