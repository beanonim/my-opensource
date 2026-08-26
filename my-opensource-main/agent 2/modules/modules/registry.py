import os
from modules.modules.config import MODULES_DIR
from modules.modules.meta import get_meta

FUNCTION_START_CODE = 30
RESERVED_CODES = set(range(1, 29)) | {55, 66, 77, 88, 99}


def list_module_files():
    os.makedirs(MODULES_DIR, exist_ok=True)
    return [f for f in sorted(os.listdir(MODULES_DIR)) if f.endswith('.lw')]


def _read_source(filename):
    path = os.path.join(MODULES_DIR, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ''


def get_modules_by_type(mod_type):
    result = []
    for fname in list_module_files():
        meta = get_meta(_read_source(fname))
        if meta.get('type') == mod_type:
            result.append((fname, meta))
    return result


def get_script_modules():
    return get_modules_by_type('script')


def get_visual_modules():
    return get_modules_by_type('visual')


def get_function_modules():
    result = []
    code = FUNCTION_START_CODE
    for fname, meta in get_modules_by_type('function'):
        while code in RESERVED_CODES:
            code += 1
        result.append((str(code), fname, meta))
        code += 1
    return result


def get_function_map():
    return {code: (fname, meta) for code, fname, meta in get_function_modules()}


FUNCTIONS_PER_PAGE = 4
STATIC_PAGES = 3
STATIC_LEFTOVER_COUNT = 3


def get_function_pages():
    mods = get_function_modules()
    if not mods:
        return []
    pages = [mods[:8 - STATIC_LEFTOVER_COUNT]]
    rest = mods[8 - STATIC_LEFTOVER_COUNT:]
    for i in range(0, len(rest), FUNCTIONS_PER_PAGE):
        pages.append(rest[i:i + FUNCTIONS_PER_PAGE])
    return pages


def get_total_pages():
    return STATIC_PAGES + len(get_function_pages())
