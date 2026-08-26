import sys, threading, time, os, shutil

sys.dont_write_bytecode = True

def cleanup_pycache():
    for root, dirs, files in os.walk('.', topdown=False):
        for name in dirs:
            if name == "__pycache__":
                shutil.rmtree(os.path.join(root, name), ignore_errors=True)
        for name in files:
            if name.endswith(".pyc") or name.endswith(".pyo"):
                os.remove(os.path.join(root, name))

cleanup_pycache()

chars = ['|', '/', '-', '\\']
stop = False
status = "Загрузка Python"

def anim():
    i = 0
    while not stop:
        sys.stdout.write(f'\r\033[94m[\033[36m{chars[i % 4]}\033[94m]\033[0m \033[97m{status}...\033[0m\033[K')
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1

def main():
    global stop, status
    os.system('cls' if os.name == 'nt' else 'clear')
    t = threading.Thread(target=anim)
    t.daemon = True
    t.start()

    try:
        status = "Инициализация модулей"
        import loader
        status = "Пушок мяукает чтобы все запустилось последний раз.."
        stop = True
        t.join()
        sys.stdout.write('\r\033[92m[+] Загрузка завершена!\033[0m\033[K\n')
        sys.stdout.flush()
        loader.start()
    except Exception as e:
        stop = True
        t.join()
        import traceback
        tb = traceback.format_exc()
        sys.stdout.write('\r\033[K')
        sys.stdout.flush()
        time.sleep(0.3)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        panic_lines = [
            '',
            '\033[97;41m                    KERNEL PANIC                   \033[0m',
            '',
            '\033[91m  *** STOP: 0x0000DEAD  CRITICAL_PROCESS_DIED\033[0m',
            '',
            f'\033[93m  Exception Type  :\033[0m \033[97m{type(e).__name__}\033[0m',
            f'\033[93m  Error Message   :\033[0m \033[97m{e}\033[0m',
            '',
            '\033[91m  --- Traceback (cut) ---\033[0m',
        ]
        
        for tb_line in tb.strip().splitlines()[-6:]:
            panic_lines.append(f'\033[90m  {tb_line}\033[0m')
        
        panic_lines += [
            '',
            '\033[91m  --- end of stack trace ---\033[0m',
            '',
            '\033[97;41m  Ядро lightwave было сломано.            \033[0m',
            '\033[97;41m  Обратитесь к разработчику: t.me/hatedfame                    \033[0m',
            '',
        ]
        
        for line in panic_lines:
            sys.stdout.write(line + '\n')
            sys.stdout.flush()
            time.sleep(0.04)
        
        input("\033[90m  Нажмите Enter для выхода...\033[0m")
        sys.exit(1)

main()