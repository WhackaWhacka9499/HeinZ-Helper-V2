import frida
import sys

sys.stdout.reconfigure(encoding='utf-8')

session = frida.attach('Survival.exe')
scr = session.create_script('''
const ws2 = Process.getModuleByName('WS2_32.dll');
const wsaRecv = ws2.getExportByName('WSARecv');
const recvFn = ws2.getExportByName('recv');

let wsaRecvCalls = 0;
let recvCalls = 0;

Interceptor.attach(wsaRecv, {
    onEnter(args) {
        wsaRecvCalls++;
    }
});

Interceptor.attach(recvFn, {
    onEnter(args) {
        recvCalls++;
    }
});

setInterval(() => {
    send({wsaRecv: wsaRecvCalls, recv: recvCalls});
}, 1000);
''')

res = []
scr.on('message', lambda m, d: print(m['payload']))
scr.load()
import time; time.sleep(3)
session.detach()
