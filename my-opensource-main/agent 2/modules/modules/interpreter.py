import re
import time
import ast
import json as _json
import random as _random
import ipaddress
from urllib.parse import urlparse, urljoin
import requests as _requests
from modules.console import console
from modules.input import v2i
from modules.config import USERNAME, UUID, SUBSCRIPTION
from modules.theme_manager import save_config, DEFAULT_THEMES
from modules.console_utils import update_console_theme

_VISUAL_COLOR_ROLES = tuple(DEFAULT_THEMES['standard'].keys())

_BLOCKED_HOSTS = {
    'localhost', '127.0.0.1', '0.0.0.0', '::1',
    '169.254.169.254', 'metadata.google.internal',
    '100.100.100.200', '169.254.169.254.nip.io',
}
_ALLOWED_SCHEMES = {'http', 'https'}


def _is_private_ip(host):
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    except ValueError:
        return False


def _safe_url(url):
    try:
        parsed = urlparse(url)
    except Exception:
        raise ModuleError(f'Некорректный URL: {url}')
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise ModuleError(f'URL-схема "{parsed.scheme}" запрещена (только http/https)')
    host = (parsed.hostname or '').lower()
    if host in _BLOCKED_HOSTS:
        raise ModuleError(f'Доступ к {host} запрещён')
    if _is_private_ip(host):
        raise ModuleError(f'Доступ к приватному IP {host} запрещён')
    if host.startswith('10.') or host.startswith('192.168.') or host.startswith('172.'):
        raise ModuleError('Доступ к локальной сети запрещён')
    try:
        import socket
        resolved = socket.getaddrinfo(host, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for family, _, _, sockaddr in resolved:
            ip = sockaddr[0]
            if _is_private_ip(ip):
                raise ModuleError(f'Доступ запрещён: {host} резолвится в приватный IP {ip}')
            if ip.startswith('10.') or ip.startswith('192.168.') or ip.startswith('172.'):
                raise ModuleError(f'Доступ запрещён: {host} резолвится в локальную сеть ({ip})')
    except socket.gaierror:
        raise ModuleError(f'Не удалось разрезолвить хост: {host}')
    except ModuleError:
        raise
    except Exception:
        pass
    return url


class ModuleError(Exception):
    pass


class BreakSignal(Exception):
    pass


class _LightwaveAPI:
    def user(self, key):
        keys = {
            'uuid': UUID,
            'username': USERNAME,
            'subscription': SUBSCRIPTION,
        }
        if key in keys:
            return keys[key]
        raise ModuleError(f'lightwave.user(): неизвестный параметр "{key}". Доступные: uuid, username, subscription')

    def __repr__(self):
        return '<lightwave API>'


_MAX_LOOP_ITERATIONS = 100_000
_MAX_RECURSION_DEPTH = 100
_MAX_SLEEP_SECONDS = 300
_MAX_RANGE = 1_000_000
_MAX_LIST_SIZE = 10_000
_MAX_HTTP_RESPONSE_BYTES = 1_000_000
_MAX_REDIRECTS = 5


class LWInterpreter:
    def __init__(self, source):
        self.source = source
        self.vars = {'lightwave': _LightwaveAPI()}
        self.lines = []
        self.pos = 0
        self._depth = 0

    def run(self):
        self.lines = self._tokenize(self.source)
        self.pos = 0
        while self.pos < len(self.lines):
            self._exec(self.lines[self.pos])
            self.pos += 1

    def _tokenize(self, source):
        result = []
        for raw in source.splitlines():
            stripped = raw.rstrip()
            clean = self._strip_comment(stripped).strip()
            if clean.strip():
                result.append((raw, clean.strip()))
        return result

    def _strip_comment(self, line):
        in_single = in_double = False
        escaped = False
        for i, ch in enumerate(line):
            if escaped:
                escaped = False
                continue
            if ch == '\\':
                escaped = True
                continue
            if ch == "'" and not in_double:
                in_single = not in_single
                continue
            if ch == '"' and not in_single:
                in_double = not in_double
                continue
            if ch == '#' and not in_single and not in_double:
                return line[:i]
        return line

    def _exec(self, line_tuple):
        raw, line = line_tuple

        if line.startswith('if '):
            self._exec_if(raw)
            return
        if line.startswith('else:') or line.startswith('elif '):
            return
        if line.startswith('while '):
            self._exec_while(raw)
            return
        if line.startswith('for '):
            self._exec_for(raw)
            return
        if line == 'forever:':
            self._exec_forever(raw)
            return
        if line == 'break':
            raise BreakSignal()
        if line.startswith('print('):
            self._exec_print(line)
            return
        if line == 'clear()':
            console.clear()
            return
        if line.startswith('sleep('):
            m = re.match(r'^sleep\((.+)\)$', line)
            if m:
                val = float(self._eval(m.group(1)))
                if val < 0 or val > _MAX_SLEEP_SECONDS:
                    raise ModuleError(f'sleep(): допустимо от 0 до {_MAX_SLEEP_SECONDS} секунд')
                time.sleep(val)
            return
        if (line.startswith('set_theme(') or line.startswith('set_color(') or
                line.startswith('set_banner_style(') or line.startswith('set_banner_layout(') or
                line.startswith('set_brackets(') or line.startswith('set_input_style(') or
                line.startswith('set_banner(') or line.startswith('set_config(')):
            self._exec_visual(line)
            return
        if line.startswith('ask(') or line.startswith('ask_hidden(') or \
           line.startswith('input(') or line.startswith('request.') or \
           line.startswith('json.') or line.startswith('http.') or \
           line.startswith('list.') or line.startswith('lightwave.'):
            self._eval(line)
            return

        m = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', line)
        if m:
            self.vars[m.group(1)] = self._eval(m.group(2).strip())
            return

        raise ModuleError(f'Неизвестная инструкция: {line}')

    def _exec_if(self, raw_start):
        indent_start = len(raw_start) - len(raw_start.lstrip())
        _, condition_line = self.lines[self.pos]
        m = re.match(r'^if (.+):$', condition_line)
        if not m:
            raise ModuleError(f'Синтаксис if: {condition_line}')

        branches = []
        current_cond = m.group(1).strip()
        current_body = []
        i = self.pos + 1

        while i < len(self.lines):
            raw_next, next_line = self.lines[i]
            indent_next = len(raw_next) - len(raw_next.lstrip())

            if indent_next <= indent_start:
                if next_line.startswith('elif '):
                    branches.append((current_cond, current_body))
                    m2 = re.match(r'^elif (.+):$', next_line)
                    if not m2:
                        raise ModuleError(f'Синтаксис elif: {next_line}')
                    current_cond = m2.group(1).strip()
                    current_body = []
                    i += 1
                    continue
                if next_line == 'else:':
                    branches.append((current_cond, current_body))
                    current_cond = None
                    current_body = []
                    i += 1
                    continue
                break

            current_body.append(self.lines[i])
            i += 1

        branches.append((current_cond, current_body))

        for cond, body in branches:
            if cond is None or self._eval_condition(cond):
                self._run_body(body)
                break

        self.pos = i - 1

    def _exec_while(self, raw_start):
        indent_start = len(raw_start) - len(raw_start.lstrip())
        _, condition_line = self.lines[self.pos]
        m = re.match(r'^while (.+):$', condition_line)
        if not m:
            raise ModuleError(f'Синтаксис while: {condition_line}')

        condition = m.group(1).strip()
        body = []
        i = self.pos + 1

        while i < len(self.lines):
            raw_next, _ = self.lines[i]
            indent_next = len(raw_next) - len(raw_next.lstrip())
            if indent_next <= indent_start:
                break
            body.append(self.lines[i])
            i += 1

        iterations = 0
        while self._eval_condition(condition):
            iterations += 1
            if iterations > _MAX_LOOP_ITERATIONS:
                raise ModuleError('Превышен лимит итераций цикла (100 000)')
            try:
                self._run_body(body)
            except BreakSignal:
                break

        self.pos = i - 1

    def _exec_forever(self, raw_start):
        indent_start = len(raw_start) - len(raw_start.lstrip())
        body = []
        i = self.pos + 1
        while i < len(self.lines):
            raw_next, _ = self.lines[i]
            indent_next = len(raw_next) - len(raw_next.lstrip())
            if indent_next <= indent_start:
                break
            body.append(self.lines[i])
            i += 1
        iterations = 0
        while True:
            iterations += 1
            if iterations > _MAX_LOOP_ITERATIONS:
                raise ModuleError('Превышен лимит итераций цикла (100 000)')
            try:
                self._run_body(body)
            except BreakSignal:
                break

        self.pos = i - 1

    def _exec_for(self, raw_start):
        indent_start = len(raw_start) - len(raw_start.lstrip())
        _, cond_line = self.lines[self.pos]
        m = re.match(r'^for\s+(\w+)\s+in\s+range\((.+)\):$', cond_line)
        if not m:
            raise ModuleError(f'Синтаксис for: {cond_line}')
        var_name = m.group(1)
        args = [a.strip() for a in self._split_args(m.group(2))]
        if len(args) == 1:
            stop = int(self._eval(args[0]))
            start, step = 0, 1
        elif len(args) == 2:
            start = int(self._eval(args[0]))
            stop = int(self._eval(args[1]))
            step = 1
        elif len(args) == 3:
            start = int(self._eval(args[0]))
            stop = int(self._eval(args[1]))
            step = int(self._eval(args[2]))
        else:
            raise ModuleError('range() принимает 1-3 аргумента')
        if step == 0:
            raise ModuleError('range(): шаг не может быть 0')
        span = abs(stop - start)
        if span // max(abs(step), 1) > _MAX_RANGE:
            raise ModuleError('range(): слишком большой диапазон')
        body = []
        i = self.pos + 1
        while i < len(self.lines):
            raw_next, _ = self.lines[i]
            indent_next = len(raw_next) - len(raw_next.lstrip())
            if indent_next <= indent_start:
                break
            body.append(self.lines[i])
            i += 1
        iterations = 0
        for val in range(start, stop, step):
            iterations += 1
            if iterations > _MAX_LOOP_ITERATIONS:
                raise ModuleError('Превышен лимит итераций цикла (100 000)')
            self.vars[var_name] = val
            try:
                self._run_body(body)
            except BreakSignal:
                break
        self.pos = i - 1

    def _run_body(self, body):
        self._depth += 1
        if self._depth > _MAX_RECURSION_DEPTH:
            self._depth -= 1
            raise ModuleError('Слишком глубокая вложенность')
        saved_lines, saved_pos = self.lines, self.pos
        self.lines = body
        self.pos = 0
        try:
            while self.pos < len(self.lines):
                self._exec(self.lines[self.pos])
                self.pos += 1
        finally:
            self.lines = saved_lines
            self._depth -= 1

    def _exec_print(self, line):
        m = re.match(r'^print\((.*)\)$', line)
        if not m:
            raise ModuleError(f'Синтаксис print: {line}')
        args_str = m.group(1).strip()
        if not args_str:
            console.print()
            return
        parts = [p.strip() for p in self._split_args(args_str)]
        if len(parts) == 1:
            console.print(str(self._eval(parts[0])))
            return
        style_map = {
            'success': 'success', 'error': 'error', 'warning': 'warning',
            'primary': 'primary', 'secondary': 'secondary', 'info': 'dim',
        }
        message = str(self._eval(parts[1]))
        tag = style_map.get(parts[0])
        console.print(f'[{tag}]{message}[/{tag}]' if tag else message)

    def _exec_visual(self, line):
        m = re.match(r'^set_theme\((.+)\)$', line)
        if m:
            name = str(self._eval(m.group(1).strip()))
            save_config(USERNAME, 'theme', name)
            update_console_theme(console, USERNAME)
            return

        m = re.match(r'^set_color\((.+)\)$', line)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) != 2:
                raise ModuleError('set_color(роль, цвет)')
            role_raw = parts[0]
            if (role_raw.startswith('"') and role_raw.endswith('"')) or \
               (role_raw.startswith("'") and role_raw.endswith("'")):
                role = role_raw[1:-1]
            elif role_raw in _VISUAL_COLOR_ROLES:
                role = role_raw
            else:
                role = str(self._eval(role_raw))
            color = str(self._eval(parts[1]))
            if role not in _VISUAL_COLOR_ROLES:
                raise ModuleError(
                    f'set_color: неизвестная роль "{role}". Доступные: {", ".join(_VISUAL_COLOR_ROLES)}'
                )
            save_config(USERNAME, 'color_' + role, color)
            update_console_theme(console, USERNAME)
            return

        m = re.match(r'^set_banner_style\((.+)\)$', line)
        if m:
            style = str(self._eval(m.group(1).strip()))
            save_config(USERNAME, 'banner_style', style)
            return

        m = re.match(r'^set_banner_layout\((.+)\)$', line)
        if m:
            layout = str(self._eval(m.group(1).strip()))
            save_config(USERNAME, 'banner_layout', layout)
            return

        m = re.match(r'^set_brackets\((.+)\)$', line)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) != 2:
                raise ModuleError('set_brackets(левый, правый)')
            left = str(self._eval(parts[0]))
            right = str(self._eval(parts[1]))
            save_config(USERNAME, 'style', 'custom')
            save_config(USERNAME, 'left_bracket', left)
            save_config(USERNAME, 'right_bracket', right)
            return

        m = re.match(r'^set_input_style\((.+)\)$', line)
        if m:
            num = str(self._eval(m.group(1).strip()))
            save_config(USERNAME, 'input_style', num)
            return

        m = re.match(r'^set_banner\((.+)\)$', line)
        if m:
            text = str(self._eval(m.group(1).strip()))
            text = text.replace('\\\\n', '\\n')
            save_config(USERNAME, 'custom_banner', text)
            return

        m = re.match(r'^set_config\((.+)\)$', line)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) != 2:
                raise ModuleError('set_config(ключ, значение)')
            key = str(self._eval(parts[0]))
            value = str(self._eval(parts[1]))
            save_config(USERNAME, key, value)
            return

        raise ModuleError(f'Неизвестная визуальная инструкция: {line}')

    def _eval(self, expr):
        expr = expr.strip()

        m = re.match(r'^lightwave\.user\((.+)\)$', expr)
        if m:
            raw_key = m.group(1).strip()
            if (raw_key.startswith('"') and raw_key.endswith('"')) or \
               (raw_key.startswith("'") and raw_key.endswith("'")):
                key = raw_key[1:-1]
            elif raw_key in self.vars:
                key = str(self.vars[raw_key])
            else:
                key = raw_key
            lw = self.vars.get('lightwave')
            if lw:
                return lw.user(key)
            raise ModuleError('lightwave API недоступна')

        if (expr.startswith('"') and expr.endswith('"')) or \
           (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        if re.match(r'^-?\d+$', expr):
            return int(expr)
        if re.match(r'^-?\d+\.\d+$', expr):
            return float(expr)
        if expr == 'True': return True
        if expr == 'False': return False
        if expr == 'None': return None

        m = re.match(r'^ask\((.+)\)$', expr)
        if m:
            return v2i(str(self._eval(m.group(1))), f'{USERNAME}@{UUID}').strip()

        m = re.match(r'^ask_hidden\((.+)\)$', expr)
        if m:
            import getpass
            prompt = str(self._eval(m.group(1)))
            return getpass.getpass(f'{prompt}: ')

        m = re.match(r'^input\((.+)\)$', expr)
        if m:
            return v2i(str(self._eval(m.group(1))), f'{USERNAME}@{UUID}').strip()

        m = re.match(r'^upper\((.+)\)$', expr)
        if m:
            return str(self._eval(m.group(1))).upper()

        m = re.match(r'^lower\((.+)\)$', expr)
        if m:
            return str(self._eval(m.group(1))).lower()

        m = re.match(r'^trim\((.+)\)$', expr)
        if m:
            return str(self._eval(m.group(1))).strip()

        m = re.match(r'^len\((.+)\)$', expr)
        if m:
            val = self._eval(m.group(1))
            return len(val) if not isinstance(val, str) else len(val)

        m = re.match(r'^contains\((.+)\)$', expr)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) != 2:
                raise ModuleError('contains(строка, подстрока)')
            return str(self._eval(parts[1])) in str(self._eval(parts[0]))

        m = re.match(r'^replace\((.+)\)$', expr)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) != 3:
                raise ModuleError('replace(строка, что, на_что)')
            s = str(self._eval(parts[0]))
            return s.replace(str(self._eval(parts[1])), str(self._eval(parts[2])))

        m = re.match(r'^split\((.+)\)$', expr)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) == 1:
                return str(self._eval(parts[0])).split()
            elif len(parts) == 2:
                return str(self._eval(parts[0])).split(str(self._eval(parts[1])))
            raise ModuleError('split(строка) или split(строка, разделитель)')

        m = re.match(r'^join\((.+)\)$', expr)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) != 2:
                raise ModuleError('join(разделитель, список)')
            sep = str(self._eval(parts[0]))
            arr = self._eval(parts[1])
            if isinstance(arr, list):
                return sep.join(str(x) for x in arr)
            return sep.join(str(arr))

        m = re.match(r'^starts_with\((.+)\)$', expr)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) != 2:
                raise ModuleError('starts_with(строка, префикс)')
            return str(self._eval(parts[0])).startswith(str(self._eval(parts[1])))

        m = re.match(r'^ends_with\((.+)\)$', expr)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) != 2:
                raise ModuleError('ends_with(строка, суффикс)')
            return str(self._eval(parts[0])).endswith(str(self._eval(parts[1])))

        m = re.match(r'^slice\((.+)\)$', expr)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) == 2:
                s = str(self._eval(parts[0]))
                return s[int(self._eval(parts[1])):]
            elif len(parts) == 3:
                s = str(self._eval(parts[0]))
                return s[int(self._eval(parts[1])):int(self._eval(parts[2]))]
            raise ModuleError('slice(строка, начало) или slice(строка, начало, конец)')

        m = re.match(r'^format\((.+)\)$', expr)
        if m:
            return self._eval_format(m.group(1))

        m = re.match(r'^dict\((.*)\)$', expr)
        if m:
            return self._eval_dict(m.group(1))

        m = re.match(r'^list\((.*)\)$', expr)
        if m:
            args_str = m.group(1).strip()
            if not args_str:
                return []
            items = [self._eval(a.strip()) for a in self._split_args(args_str)]
            if len(items) > _MAX_LIST_SIZE:
                raise ModuleError('list(): слишком большой список')
            return items

        m = re.match(r'^list\.append\((.+)\)$', expr)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) != 2:
                raise ModuleError('list.append(список, значение)')
            arr = self._eval(parts[0])
            if not isinstance(arr, list):
                raise ModuleError('list.append: первый аргумент должен быть списком')
            if len(arr) >= _MAX_LIST_SIZE:
                raise ModuleError('list.append: превышен лимит размера списка')
            arr.append(self._eval(parts[1]))
            return arr

        m = re.match(r'^list\.get\((.+)\)$', expr)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) != 2:
                raise ModuleError('list.get(список, индекс)')
            arr = self._eval(parts[0])
            idx = int(self._eval(parts[1]))
            if not isinstance(arr, list):
                raise ModuleError('list.get: первый аргумент должен быть списком')
            return arr[idx]

        m = re.match(r'^list\.set\((.+)\)$', expr)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) != 3:
                raise ModuleError('list.set(список, индекс, значение)')
            arr = self._eval(parts[0])
            idx = int(self._eval(parts[1]))
            if not isinstance(arr, list):
                raise ModuleError('list.set: первый аргумент должен быть списком')
            arr[idx] = self._eval(parts[2])
            return arr

        m = re.match(r'^list\.remove\((.+)\)$', expr)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) != 2:
                raise ModuleError('list.remove(список, индекс)')
            arr = self._eval(parts[0])
            idx = int(self._eval(parts[1]))
            if not isinstance(arr, list):
                raise ModuleError('list.remove: первый аргумент должен быть списком')
            return arr.pop(idx)

        m = re.match(r'^list\.contains\((.+)\)$', expr)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) != 2:
                raise ModuleError('list.contains(список, значение)')
            arr = self._eval(parts[0])
            if not isinstance(arr, list):
                raise ModuleError('list.contains: первый аргумент должен быть списком')
            return self._eval(parts[1]) in arr

        m = re.match(r'^list\.sort\((.+)\)$', expr)
        if m:
            arr = self._eval(m.group(1).strip())
            if not isinstance(arr, list):
                raise ModuleError('list.sort: аргумент должен быть списком')
            arr.sort()
            return arr

        m = re.match(r'^list\.reverse\((.+)\)$', expr)
        if m:
            arr = self._eval(m.group(1).strip())
            if not isinstance(arr, list):
                raise ModuleError('list.reverse: аргумент должен быть списком')
            arr.reverse()
            return arr

        m = re.match(r'^str\((.+)\)$', expr)
        if m:
            return str(self._eval(m.group(1)))

        m = re.match(r'^int\((.+)\)$', expr)
        if m:
            return int(self._eval(m.group(1)))

        m = re.match(r'^float\((.+)\)$', expr)
        if m:
            return float(self._eval(m.group(1)))

        m = re.match(r'^bool\((.+)\)$', expr)
        if m:
            return bool(self._eval(m.group(1)))

        m = re.match(r'^abs\((.+)\)$', expr)
        if m:
            return abs(self._eval(m.group(1)))

        m = re.match(r'^min\((.+)\)$', expr)
        if m:
            parts = [self._eval(p.strip()) for p in self._split_args(m.group(1))]
            return min(parts)

        m = re.match(r'^max\((.+)\)$', expr)
        if m:
            parts = [self._eval(p.strip()) for p in self._split_args(m.group(1))]
            return max(parts)

        m = re.match(r'^round\((.+)\)$', expr)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            val = self._eval(parts[0])
            if len(parts) == 2:
                return round(float(val), int(self._eval(parts[1])))
            return round(float(val))

        m = re.match(r'^random\((.+)\)$', expr)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) == 1:
                return _random.randint(0, int(self._eval(parts[0])))
            elif len(parts) == 2:
                return _random.randint(int(self._eval(parts[0])), int(self._eval(parts[1])))
            raise ModuleError('random(макс) или random(мин, макс)')

        m = re.match(r'^is_number\((.+)\)$', expr)
        if m:
            try:
                float(str(self._eval(m.group(1))).strip())
                return True
            except (ValueError, TypeError):
                return False

        m = re.match(r'^is_empty\((.+)\)$', expr)
        if m:
            val = self._eval(m.group(1))
            if val is None:
                return True
            if isinstance(val, str):
                return len(val.strip()) == 0
            if isinstance(val, (list, dict)):
                return len(val) == 0
            return False

        m = re.match(r'^type\((.+)\)$', expr)
        if m:
            val = self._eval(m.group(1))
            return type(val).__name__

        m = re.match(r'^json\.get\((.+)\)$', expr)
        if m:
            return self._json_get(m.group(1))

        m = re.match(r'^json\.set\((.+)\)$', expr)
        if m:
            return self._json_set(m.group(1))

        m = re.match(r'^json\.raw\((.+)\)$', expr)
        if m:
            raw = self._eval(m.group(1).strip())
            try:
                return _json.dumps(_json.loads(raw), ensure_ascii=False, indent=2)
            except Exception:
                return str(raw)

        m = re.match(r'^http\.get\((.+)\)$', expr)
        if m:
            url = str(self._eval(m.group(1).strip()))
            _safe_url(url)
            return self._http('GET', url)

        m = re.match(r'^http\.post\((.+)\)$', expr)
        if m:
            parts = [p.strip() for p in self._split_args(m.group(1))]
            if len(parts) == 1:
                url = str(self._eval(parts[0]))
                _safe_url(url)
                return self._http('POST', url)
            elif len(parts) == 2:
                url = str(self._eval(parts[0]))
                _safe_url(url)
                return self._http('POST', url, json_body=self._eval(parts[1]))
            raise ModuleError('http.post(url) или http.post(url, data)')

        m = re.match(r'^http\.status\((.+)\)$', expr)
        if m:
            url = str(self._eval(m.group(1).strip()))
            resp = self._request_raw('GET', url)
            code = resp.status_code
            resp.close()
            return code

        m = re.match(r'^http\.headers\((.+)\)$', expr)
        if m:
            url = str(self._eval(m.group(1).strip()))
            resp = self._request_raw('GET', url)
            hdrs = dict(resp.headers)
            resp.close()
            return hdrs

        m = re.match(r'^request\.send\((.+)\)$', expr)
        if m:
            return self._req_get(m.group(1))

        m = re.match(r'^request\.get_json\((.+)\)$', expr)
        if m:
            return self._req_get_json(m.group(1))

        m = re.match(r'^request\.post_json\((.+)\)$', expr)
        if m:
            return self._req_post_json(m.group(1))

        m = re.match(r'^request\.post\((.+)\)$', expr)
        if m:
            return self._req_post(m.group(1))

        if expr in self.vars:
            return self.vars[expr]

        try:
            parsed = ast.parse(expr, mode='eval')
            return self._eval_ast(parsed.body)
        except ModuleError:
            pass
        except Exception:
            raise ModuleError(f'Ошибка вычисления: {expr}')

        raise ModuleError(f'Неизвестное выражение: {expr}')

    def _eval_format(self, args_str):
        parts = [p.strip() for p in self._split_args(args_str)]
        if not parts:
            raise ModuleError('format() требует минимум 1 аргумент')
        template = self._eval(parts[0])
        placeholders = re.findall(r'\{(\w+)\}', template)
        val_args = parts[1:]
        val_map = {}
        for idx, ph in enumerate(placeholders):
            if ph in val_map:
                continue
            if idx < len(val_args):
                val_map[ph] = str(self._eval(val_args[idx]))
            elif ph in self.vars:
                val_map[ph] = str(self.vars[ph])
            else:
                raise ModuleError(f'format(): неизвестная переменная {{{ph}}}')
        result = template
        for ph, val in val_map.items():
            result = result.replace('{' + ph + '}', val)
        return result

    def _eval_dict(self, args_str):
        pairs = self._split_args(args_str)
        result = {}
        for pair in pairs:
            km = re.match(r'^(\w+)\s*=\s*(.+)$', pair.strip())
            if not km:
                raise ModuleError(f'dict(): неверный аргумент: {pair}')
            result[km.group(1)] = self._eval(km.group(2).strip())
        return result

    def _request_raw(self, method, url, body=None, json_body=None):
        _safe_url(url)
        current_url = url
        current_method = method
        current_body = body
        current_json = json_body
        try:
            for _ in range(_MAX_REDIRECTS + 1):
                if current_method == 'POST':
                    if current_json is not None:
                        resp = _requests.post(current_url, json=current_json, timeout=10, allow_redirects=False, stream=True)
                    else:
                        resp = _requests.post(current_url, data=current_body, timeout=10, allow_redirects=False, stream=True)
                else:
                    if current_json is not None:
                        resp = _requests.get(current_url, params=current_json, timeout=10, allow_redirects=False, stream=True)
                    else:
                        resp = _requests.get(current_url, timeout=10, allow_redirects=False, stream=True)

                if resp.status_code in (301, 302, 303, 307, 308):
                    code = resp.status_code
                    location = resp.headers.get('Location')
                    resp.close()
                    if not location:
                        raise ModuleError('request: редирект без Location')
                    current_url = _safe_url(urljoin(current_url, location))
                    if code in (301, 302, 303):
                        current_method = 'GET'
                        current_body = None
                        current_json = None
                    continue
                return resp
        except _requests.exceptions.Timeout:
            raise ModuleError('request: превышено время ожидания')
        except _requests.exceptions.RequestException as e:
            raise ModuleError(f'request: ошибка — {e}')
        raise ModuleError('request: слишком много редиректов')

    def _http(self, method, url, body=None, json_body=None):
        resp = self._request_raw(method, url, body, json_body)
        try:
            resp.raise_for_status()
            content = resp.content
        except _requests.exceptions.RequestException as e:
            raise ModuleError(f'request: ошибка — {e}')
        finally:
            resp.close()
        if len(content) > _MAX_HTTP_RESPONSE_BYTES:
            raise ModuleError('request: ответ слишком большой (лимит 1 МБ)')
        return content.decode('utf-8', errors='replace')

    def _req_get(self, args_str):
        parts = [p.strip() for p in self._split_args(args_str)]
        has_wa = False
        if parts and parts[0] in ('write_answer', "'write_answer'", '"write_answer"'):
            has_wa = True
            parts.pop(0)
        
        if len(parts) == 1:
            url = str(self._eval(parts[0]))
            _safe_url(url)
            res = self._http('GET', url)
            return res if has_wa else None
        raise ModuleError('request.send(url) или request.send(write_answer, url)')

    def _req_get_json(self, args_str):
        parts = [p.strip() for p in self._split_args(args_str)]
        has_wa = False
        if parts and parts[0] in ('write_answer', "'write_answer'", '"write_answer"'):
            has_wa = True
            parts.pop(0)
            
        if len(parts) == 1:
            url = str(self._eval(parts[0]))
            _safe_url(url)
            res = self._http('GET', url)
            return res if has_wa else None
        elif len(parts) == 2:
            url = str(self._eval(parts[0]))
            _safe_url(url)
            res = self._http('GET', url, json_body=self._eval(parts[1]))
            return res if has_wa else None
        raise ModuleError('request.get_json(url, [params]) или request.get_json(write_answer, url, [params])')

    def _req_post(self, args_str):
        parts = [p.strip() for p in self._split_args(args_str)]
        has_wa = False
        if parts and parts[0] in ('write_answer', "'write_answer'", '"write_answer"'):
            has_wa = True
            parts.pop(0)
            
        if len(parts) == 1:
            url = str(self._eval(parts[0]))
            _safe_url(url)
            res = self._http('POST', url)
            return res if has_wa else None
        elif len(parts) == 2:
            url = str(self._eval(parts[0]))
            _safe_url(url)
            res = self._http('POST', url, body=str(self._eval(parts[1])))
            return res if has_wa else None
        raise ModuleError('request.post(url, [body]) или request.post(write_answer, url, [body])')

    def _req_post_json(self, args_str):
        parts = [p.strip() for p in self._split_args(args_str)]
        has_wa = False
        if parts and parts[0] in ('write_answer', "'write_answer'", '"write_answer"'):
            has_wa = True
            parts.pop(0)
            
        if len(parts) == 1:
            url = str(self._eval(parts[0]))
            _safe_url(url)
            res = self._http('POST', url)
            return res if has_wa else None
        elif len(parts) == 2:
            url = str(self._eval(parts[0]))
            _safe_url(url)
            res = self._http('POST', url, json_body=self._eval(parts[1]))
            return res if has_wa else None
        raise ModuleError('request.post_json(url, [data]) или request.post_json(write_answer, url, [data])')

    def _json_get(self, args_str):
        parts = [p.strip() for p in self._split_args(args_str)]
        if len(parts) != 2:
            raise ModuleError('json.get(ответ, "ключ")')
        raw = self._eval(parts[0])
        key_path = self._eval(parts[1])
        try:
            data = _json.loads(raw)
            for key in key_path.split('.'):
                data = data[int(key)] if isinstance(data, list) else data[key]
            return str(data)
        except (KeyError, IndexError, TypeError):
            return ''
        except Exception as e:
            raise ModuleError(f'json.get: {e}')

    def _json_set(self, args_str):
        parts = [p.strip() for p in self._split_args(args_str)]
        if len(parts) != 3:
            raise ModuleError('json.set(json_str, "ключ", значение)')
        raw = self._eval(parts[0])
        key_path = self._eval(parts[1])
        new_val = self._eval(parts[2])
        try:
            data = _json.loads(raw)
            keys = key_path.split('.')
            target = data
            for key in keys[:-1]:
                if isinstance(target, list):
                    target = target[int(key)]
                else:
                    target = target[key]
            last_key = keys[-1]
            if isinstance(target, list):
                target[int(last_key)] = new_val
            else:
                target[last_key] = new_val
            return _json.dumps(data, ensure_ascii=False)
        except Exception as e:
            raise ModuleError(f'json.set: {e}')

    def _eval_ast(self, node):
        if isinstance(node, ast.BinOp):
            left = self._eval_ast(node.left)
            right = self._eval_ast(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.FloorDiv):
                return left // right
            if isinstance(node.op, ast.Mod):
                return left % right
            if isinstance(node.op, ast.Pow):
                return left ** right
            raise ModuleError(f'Неподдерживаемая бинарная операция: {node.op}')

        if isinstance(node, ast.UnaryOp):
            value = self._eval_ast(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +value
            if isinstance(node.op, ast.USub):
                return -value
            if isinstance(node.op, ast.Not):
                return not value
            raise ModuleError(f'Неподдерживаемая унарная операция: {node.op}')

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(self._eval_ast(v) for v in node.values)
            if isinstance(node.op, ast.Or):
                return any(self._eval_ast(v) for v in node.values)
            raise ModuleError(f'Неподдерживаемая логическая операция: {node.op}')

        if isinstance(node, ast.Compare):
            left = self._eval_ast(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval_ast(comparator)
                if isinstance(op, ast.Eq) and not (left == right):
                    return False
                if isinstance(op, ast.NotEq) and not (left != right):
                    return False
                if isinstance(op, ast.Gt) and not (left > right):
                    return False
                if isinstance(op, ast.Lt) and not (left < right):
                    return False
                if isinstance(op, ast.GtE) and not (left >= right):
                    return False
                if isinstance(op, ast.LtE) and not (left <= right):
                    return False
                if isinstance(op, ast.Is) and not (left is right):
                    return False
                if isinstance(op, ast.IsNot) and not (left is not right):
                    return False
                if isinstance(op, ast.In) and not (left in right):
                    return False
                if isinstance(op, ast.NotIn) and not (left not in right):
                    return False
                left = right
            return True

        if isinstance(node, ast.Name):
            if node.id == 'True':
                return True
            if node.id == 'False':
                return False
            if node.id == 'None':
                return None
            if node.id in self.vars:
                return self.vars[node.id]
            raise ModuleError(f'Неизвестная переменная: {node.id}')

        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Str):
            return node.s

        if isinstance(node, ast.Num):
            return node.n

        if isinstance(node, (ast.Call, ast.Attribute, ast.Subscript)):
            raise ModuleError('Запрещённая операция (вызовы и доступ к атрибутам недоступны)')

        raise ModuleError(f'Неподдерживаемый вид выражения: {type(node).__name__}')

    def _eval_condition(self, cond):
        cond = cond.strip()
        try:
            parsed = ast.parse(cond, mode='eval')
            return bool(self._eval_ast(parsed.body))
        except Exception:
            pass

        for pat, op in [
            (r'^(.+?)\s+is\s+not\s+(.+)$', 'ne'),
            (r'^(.+?)\s+is\s+(.+)$', 'eq'),
            (r'^(.+?)\s*==\s*(.+)$', 'eq'),
            (r'^(.+?)\s*!=\s*(.+)$', 'ne'),
            (r'^(.+?)\s*>=\s*(.+)$', 'ge'),
            (r'^(.+?)\s*<=\s*(.+)$', 'le'),
            (r'^(.+?)\s*>\s*(.+)$', 'gt'),
            (r'^(.+?)\s*<\s*(.+)$', 'lt'),
        ]:
            m = re.match(pat, cond)
            if m:
                a, b = self._eval(m.group(1)), self._eval(m.group(2))
                return {'eq': a==b, 'ne': a!=b, 'gt': a>b, 'lt': a<b, 'ge': a>=b, 'le': a<=b}[op]
        m = re.match(r'^not\s+(.+)$', cond)
        if m:
            return not self._eval(m.group(1))
        return bool(self._eval(cond))

    def _split_args(self, s):
        args, depth, current, in_str = [], 0, '', None
        for ch in s:
            if in_str:
                current += ch
                if ch == in_str: in_str = None
            elif ch in ('"', "'"):
                in_str = ch; current += ch
            elif ch == '(':
                depth += 1; current += ch
            elif ch == ')':
                depth -= 1; current += ch
            elif ch == ',' and depth == 0:
                args.append(current.strip()); current = ''
            else:
                current += ch
        if current.strip(): args.append(current.strip())
        return args