import re

MODULE_TYPES = ('script', 'visual', 'function')


def get_meta(source):
    meta = {'name': '?', 'developer': '?', 'version': '?', 'description': '', 'type': 'script'}
    patterns = {
        'name':        r'^module_name\s*=\s*["\'](.+)["\']$',
        'developer':   r'^module_developer\s*=\s*["\'](.+)["\']$',
        'version':     r'^module_version\s*=\s*["\'](.+)["\']$',
        'description': r'^module_description\s*=\s*["\'](.{0,100})["\']$',
        'type':        r'^module_type\s*=\s*["\'](.+)["\']$',
    }
    for raw_line in source.splitlines():
        line = re.sub(r'(?<!["\'])#.*$', '', raw_line).strip()
        for key, pat in patterns.items():
            m = re.match(pat, line)
            if m:
                meta[key] = m.group(1)
    if meta['type'] not in MODULE_TYPES:
        meta['type'] = 'script'
    return meta