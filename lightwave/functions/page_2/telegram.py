from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *

def telegram_username_checker():
    api_id = 39280214
    api_hash = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    WORDS = [
        "forever", "hate", "leak", "faded", "locked", "dream",
        "dox", "fame", "dark", "void", "shadow", "cry", "lost",
        "dead", "cold", "sick", "burn", "noise", "rage",
        "black", "white", "bloody", "toxic", "silent", "broken",
        "chaos", "pain", "scar", "evil", "doom", "grim", "night",
        "ghost", "skull", "blade", "curse", "fear", "voided",
        "numb", "damned", "trash", "killer", "brutal", "raw",
        "storm", "acid", "soul", "grave", "wound", "fury",
        "crypt", "panic", "echo", "static", "flash", "wanna",
        "rot", "decay", "ashes", "smoke", "virus", "glitch",
        "fracture", "error", "signal", "offline", "burned",
        "collapse", "zero", "null", "core", "system", "fault",
        "breach", "infected", "corrupt", "erased", "bleed",
        "choke", "scream", "whisper", "pulse", "fade",
        "terminal", "root", "access", "packet", "trace",
        "malware", "proxy", "cipher", "payload", "exploit",
        "mask", "fake", "empty", "hollow", "scarred", "lose",
        "fire", "wind", "wave", "rock", "sand", "dust", "bark", "herb", "moss", "fern",
        "reed", "vine", "pulp", "root", "soil", "land", "dawn", "dusk", "noon", "halo",
        "glare", "beam", "glow", "haze", "drop", "mist", "tide", "surf", "reef", "gulf",
        "bay", "pond", "isle", "peak", "wood", "tree", "leaf", "rose", "lily", "snow",
        "rain", "fog", "sky", "star", "moon", "cave", "hill", "lake", "ocean", "river",
        "lynx", "wolf", "bear", "lion", "puma", "deer", "buck", "fawn", "bull", "calf",
        "boar", "mule", "colt", "mare", "foal", "lamb", "goat", "owl", "hawk", "crow",
        "swan", "duck", "dove", "lark", "gull", "fish", "pike", "bass", "shad", "carp",
        "crab", "clam", "frog", "toad", "wasp", "moth", "flea", "tick", "worm", "fox",
        "blue", "cyan", "gold", "gray", "grey", "jade", "lime", "pink", "teal", "pale",
        "bright", "pure", "soft", "lush", "silk", "dark", "deep", "high", "fair", "bold",
        "vibe", "glow", "rare", "aura", "zone", "flow", "find", "seek", "keep", "stay",
        "move", "born", "true", "wild", "calm", "fast", "keen", "nice", "good", "free",
        "cool", "warm", "kind", "soul", "life", "mind", "body", "face", "time", "date",
        "vibe", "path", "gate", "link", "code", "sync", "null", "zeta", "plus", "mini"
    ]
    WORDS_4 = [w for w in WORDS if len(w) == 4]
    STRONG_WORDS = {
        "dox", "leak", "dark", "fame", "dead", "rage",
        "void", "shadow", "killer", "curse", "doom",
        "breach", "exploit", "payload", "infected", "corrupt",
        "erased", "terminal", "malware", "cipher",
        "panic", "bleed", "collapse", "virus",
        "damned", "crypt", "grave", "brutal", "lose"
    }
    MIN_SCORE = 65
    USERNAME_RE = re.compile(r"^[a-z][a-z0-9_]{3,30}[a-z0-9]$")

    async def runner():
        phone = v2i(
            "Введите ваш номер телефона (с кодом страны, например +79123456789)",
            f"{USERNAME}@{UUID}"
        ).strip()
        session_name = 'session_t_user_' + ''.join(c for c in phone if c.isdigit())
        client = TelegramClient(session_name, api_id, api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            try:
                await client.send_code_request(phone)
            except errors.SendCodeUnavailableError:
                console.print("[error]Telegram больше не может отправить код этому номеру (исчерпаны способы: flash-call, SMS). Попробуйте позже или другой номер.[/error]")
                await client.disconnect()
                return
            except errors.FloodWaitError as e:
                console.print(f"[error]Слишком много запросов. Подождите {e.seconds} сек.[/error]")
                await client.disconnect()
                return
            except Exception as e:
                console.print(f"[error]Не удалось отправить код: {e}[/error]")
                await client.disconnect()
                return
            code = v2i("Введите код из Telegram", f"{USERNAME}@{UUID}").strip()
            try:
                await client.sign_in(phone=phone, code=code)
            except errors.SessionPasswordNeededError:
                password = v2i("Введите 2FA пароль", f"{USERNAME}@{UUID}").strip()
                await client.sign_in(password=password)
        console.print("[success]Вход выполнен.[/success]\n")
        
        console.print("[primary]Выберите режим генерации:[/primary]")
        console.print("[primary][1][/primary] Стандартный (2-3 слова)")
        console.print("[primary][2][/primary] Только 2 слова (по 4 буквы)")
        
        gen_mode = v2i("Ваш выбор", f"{USERNAME}@{UUID}").strip()
        is_two_words = (gen_mode == '2')
        source_list = WORDS_4 if is_two_words else WORDS
        sample_range = [2] if is_two_words else [2, 3]
        
        mode_label = "2 СЛОВА (4x4)" if is_two_words else "СТАНДАРТ"
        console.print(f"\n[success]Запуск чекера ({mode_label})...[/success]\n")
        
        while True:
            try:
                num_words = random.choice(sample_range)
                username = "".join(random.sample(source_list, num_words)).lower()
                console.print(f"[secondary]Проверка:[/secondary] @{username}")
                if not USERNAME_RE.fullmatch(username): continue
                try:
                    available = await client(CheckUsernameRequest(username))
                except errors.FloodWaitError as e:
                    await asyncio.sleep(e.seconds)
                    continue
                except Exception: continue
                if not available:
                    console.print("[error]Занят[/error]")
                    continue
                score = 0
                length = len(username)
                if 8 <= length <= 14: score += 30
                elif 6 <= length <= 18: score += 20
                else: score += 5
                if re.fullmatch(r"[a-z]+", username): score += 15
                else: score -= 30
                if re.search(r"(.)\1\1", username): score -= 20
                hits = sum(1 for w in WORDS if w in username)
                score += {2: 25, 3: 20}.get(hits, -20 if hits > 3 else 0)
                for w in STRONG_WORDS:
                    if w in username: score += 5
                score = max(0, min(100, score))
                console.print(f"[success]Свободен[/success] | [secondary]Красота: {score}%[/secondary]")
                if score < MIN_SCORE: continue
                choice = v2i("Создать канал с этим юзернеймом? (y/N)", f"{USERNAME}@{UUID}").strip().lower()
                if choice != "y": continue
                try:
                    result = await client(CreateChannelRequest(title=username, about="", megagroup=False))
                    await client(UpdateUsernameRequest(channel=result.chats[0], username=username))
                    console.print(f"[success]ГОТОВО → https://t.me/{username}[/success]")
                except Exception:
                    console.print("[error]Ошибка создания канала[/error]")
            finally:
                console.rule()

    asyncio.run(runner())