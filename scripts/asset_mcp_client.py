import socket,json,sys
code=open(sys.argv[1]).read() if len(sys.argv)>1 else 'import bpy\nresult={"scene":bpy.context.scene.name,"file":bpy.data.filepath,"objects":[o.name for o in bpy.context.scene.objects]}'
s=socket.create_connection(('127.0.0.1',9881),10);s.settimeout(1800)
s.sendall(json.dumps({'type':'execute','code':code,'strict_json':True}).encode()+b'\0')
b=b''
while b'\0' not in b:
 c=s.recv(65536)
 if not c:break
 b+=c
print(b.rstrip(b'\0').decode())
