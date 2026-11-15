#!/usr/bin/env python3
"""Repeat suite2, one freshly built owned environment per round.

A reused environment stops accepting X11 injection after a suite run, so every round gets a
new environment instead of pretending the old one is still pristine. The last round's
environment is torn down as well; nothing outside this directory is started or stopped.
"""
import json, subprocess, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parent
RUN=ROOT/'run'

def remove(*names):
    for name in names:
        path=RUN/name
        if path.exists():
            path.unlink()

def start(script,log):
    handle=open(RUN/log,'w')
    proc=subprocess.Popen([sys.executable,str(ROOT/script)],cwd=str(ROOT),stdout=handle,
                          stderr=subprocess.STDOUT,start_new_session=True)
    return proc,handle

def wait_json(name,timeout=60):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        path=RUN/name
        if path.exists():
            try:
                return json.loads(path.read_text())
            except ValueError:
                pass
        time.sleep(.1)
    raise TimeoutError(name)

def stop(marker,procs,timeout=25):
    (RUN/marker).write_text('stop')
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline and any(p.poll() is None for p in procs):
        time.sleep(.2)
    for proc in procs:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
    remove(marker)

def round_once(index,suite='suite2.py',results='results2.json'):
    remove('STOP','STOP-APPS','environment.json','apps.json',results)
    for path in list(RUN.glob('regression-*.json'))+list(RUN.glob('regression-*.log')):
        path.unlink()
    # Captures refuse to reuse an existing file, so each round starts with a clean artifact set.
    for path in list(RUN.glob('*.png')):
        path.unlink()
    env,envlog=start('environment.py','cycle-env-%d.log'%index)
    try:
        info=wait_json('environment.json')
        print('round %d environment %s' % (index,json.dumps(info)),flush=True)
        apps,appslog=start('apps.py','cycle-apps-%d.log'%index)
        try:
            wait_json('apps.json')
            time.sleep(6)
            run=subprocess.run([sys.executable,str(ROOT/suite)],cwd=str(ROOT),
                               capture_output=True,text=True,timeout=900)
            (RUN/('%s-round%d.log'%(Path(suite).stem,index))).write_text(run.stdout+run.stderr)
            rows=json.loads((RUN/results).read_text())
            summary={}
            for row in rows:
                summary[row['status']]=summary.get(row['status'],0)+1
            (RUN/('%s-round%d.json'%(Path(results).stem,index))).write_text(json.dumps(rows,indent=2))
            return {'round':index,'summary':summary,
                    'rows':[{k:row[k] for k in ('name','status')} for row in rows]}
        finally:
            stop('STOP-APPS',[apps])
            appslog.close()
    finally:
        stop('STOP',[env])
        envlog.close()

if __name__=='__main__':
    rounds=int(sys.argv[1]) if len(sys.argv)>1 else 3
    suite=sys.argv[2] if len(sys.argv)>2 else 'suite2.py'
    result_file='results2.json' if suite=='suite2.py' else 'results.json'
    results=[round_once(index,suite,result_file) for index in range(1,rounds+1)]
    print(json.dumps(results,indent=2),flush=True)
