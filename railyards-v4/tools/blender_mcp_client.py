"""Minimal client for the Blender MCP add-on socket (localhost:9876), used when
no MCP server is registered in the session. Usage: python3 work/bmcp.py <type> [json params]"""
import json,socket,sys,os
PORT=int(os.environ.get('BMCP_PORT','9876'))
def call(kind,params=None,timeout=120):
    s=socket.create_connection(('localhost',PORT),timeout=timeout)
    s.sendall(json.dumps({'type':kind,'params':params or {}}).encode())
    buf=b''
    while True:
        chunk=s.recv(65536)
        if not chunk:break
        buf+=chunk
        try:json.loads(buf.decode());break
        except Exception:continue
    s.close();return json.loads(buf.decode())
if __name__=='__main__':
    kind=sys.argv[1];params=json.loads(sys.argv[2]) if len(sys.argv)>2 else {}
    print(json.dumps(call(kind,params))[:4000])
