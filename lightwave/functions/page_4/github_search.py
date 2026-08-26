from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from functions.hidder import block

GITHUB_API = 'https://api.github.com'

def _print_field(label, value):
    if value is None or value == '' or value == 0:
        return
    console.print(f"  [success]•[/success] [secondary]{label:.<25}[/secondary] {value}")

def _print_fields(data: dict):
    for key, value in data.items():
        _print_field(key, value)

def github_search(username):
    if block(username, 'username'): return
    if not username:
        console.print('[error]Введите username GitHub[/error]')
        return

    username = username.strip().replace('https://github.com/', '').replace('http://github.com/', '').strip('/')

    headers = {'Accept': 'application/vnd.github.v3+json'}
    session = requests.Session()
    session.headers.update(headers)

    # профиль
    console.print('[secondary]Загрузка профиля...[/secondary]')
    try:
        r = session.get(f'{GITHUB_API}/users/{username}', timeout=15)
        if r.status_code == 404:
            console.print(f'[error]Пользователь {username} не найден[/error]')
            return
        if r.status_code == 403:
            console.print('[error]Rate limit GitHub API. Попробуйте позже[/error]')
            return
        if r.status_code != 200:
            console.print(f'[error]HTTP {r.status_code}[/error]')
            return
        profile = r.json()
    except Exception as e:
        console.print(f'[error]Ошибка подключения: {e}[/error]')
        return

    console.print('[success]━━━ ПРОФИЛЬ ━━━[/success]\n')
    _print_fields({
        'Username': profile.get('login'),
        'Имя': profile.get('name'),
        'ID': profile.get('id'),
        'Node ID': profile.get('node_id'),
        'Bio': profile.get('bio'),
        'Локация': profile.get('location'),
        'Компания': profile.get('company'),
        'Blog/Site': profile.get('blog'),
        'Email': profile.get('email'),
        'Twitter': profile.get('twitter_username'),
        'Аватар': profile.get('avatar_url'),
        'Тип аккаунта': profile.get('type'),
        'Admin': 'Да' if profile.get('site_admin') else 'Нет',
        'Публичных репозиториев': profile.get('public_repos'),
        'Публичных гистов': profile.get('public_gists'),
        'Подписчиков': profile.get('followers'),
        'Подписок': profile.get('following'),
        'Создан': profile.get('created_at'),
        'Обновлён': profile.get('updated_at'),
        'Pro': 'Да' if profile.get('plan') else 'Нет',
    })
    console.print()

    # репозитории
    console.print('[secondary]Загрузка репозиториев...[/secondary]')
    repos = []
    page = 1
    while True:
        try:
            r = session.get(f'{GITHUB_API}/users/{username}/repos', params={'per_page': 100, 'page': page}, timeout=15)
            if r.status_code != 200:
                break
            page_data = r.json()
            if not page_data:
                break
            repos.extend(page_data)
            if len(page_data) < 100:
                break
            page += 1
        except Exception:
            break

    if repos:
        console.print(f'[success]━━━ РЕПОЗИТОРИИ ({len(repos)}) ━━━[/success]\n')
        for i, repo in enumerate(repos, 1):
            stars = repo.get('stargazers_count', 0)
            forks = repo.get('forks_count', 0)
            watchers = repo.get('watchers_count', 0)
            size_kb = repo.get('size', 0)
            size_str = f'{size_kb} KB' if size_kb < 1024 else f'{size_kb/1024:.1f} MB'

            console.print(f'  [success]#{i}[/success] [bold]{repo.get("name")}[/bold]')
            if repo.get('description'):
                console.print(f'      [secondary]Описание:[/secondary] {repo["description"]}')
            console.print(f'      [secondary]URL:[/secondary] [primary][link={repo.get("html_url")}]{repo.get("html_url")}[/link][/primary]')
            console.print(f'      [secondary]Язык:[/secondary] {repo.get("language") or "N/A"}')
            console.print(f'      [secondary]Статус:[/secondary] {"Приватный" if repo.get("private") else "Публичный"}')
            console.print(f'      [secondary]Форк:[/secondary] {"Да" if repo.get("fork") else "Нет"}')
            console.print(f'      [secondary]Stars:[/secondary] {stars}  [secondary]Forks:[/secondary] {forks}  [secondary]Watchers:[/secondary] {watchers}')
            console.print(f'      [secondary]Размер:[/secondary] {size_str}')
            if repo.get('license') and isinstance(repo['license'], dict):
                console.print(f'      [secondary]Лицензия:[/secondary] {repo["license"].get("name")}')
            if repo.get('topics'):
                console.print(f'      [secondary]Топики:[/secondary] {", ".join(repo["topics"])}')
            if repo.get('homepage'):
                console.print(f'      [secondary]Homepage:[/secondary] {repo["homepage"]}')
            console.print(f'      [secondary]Создан:[/secondary] {repo.get("created_at")}  [secondary]Обновлён:[/secondary] {repo.get("updated_at")}')
            console.print()
    else:
        console.print('[warning]Репозитории не найдены[/warning]')

    # почта из коммитов
    console.print('[secondary]Сканирование коммитов для поиска email...[/secondary]')
    emails_found = set()
    scanned_repos = 0

    for repo in repos[:20]:
        repo_name = repo.get('name')
        if not repo_name:
            continue
        try:
            r = session.get(f'{GITHUB_API}/repos/{username}/{repo_name}/commits', params={'per_page': 100}, timeout=10)
            if r.status_code != 200:
                continue
            scanned_repos += 1
            for commit in r.json():
                author = commit.get('commit', {}).get('author', {})
                committer = commit.get('commit', {}).get('committer', {})
                for person in [author, committer]:
                    email = person.get('email')
                    if email and not email.endswith('noreply@github.com') and not email.endswith('users.noreply.github.com'):
                        emails_found.add(email)
                if len(emails_found) >= 50:
                    break
            if len(emails_found) >= 50:
                break
        except Exception:
            continue

    if emails_found:
        console.print(f'\n[success]━━━ НАЙДЕННЫЕ EMAIL ({len(emails_found)}) ━━━[/success]\n')
        for email in sorted(emails_found):
            console.print(f'  [success]•[/success] {email}')
    else:
        console.print('[warning]Email не найден в коммитах[/warning]')

    # events (последняя активность)
    console.print('\n[secondary]Загрузка последних событий...[/secondary]')
    try:
        r = session.get(f'{GITHUB_API}/users/{username}/events/public', params={'per_page': 10}, timeout=10)
        if r.status_code == 200:
            events = r.json()
            if events:
                console.print(f'[success]━━━ ПОСЛЕДНИЕ СОБЫТИЯ ({len(events)}) ━━━[/success]\n')
                for ev in events:
                    ev_type = ev.get('type', '').replace('Event', '')
                    repo_name = ev.get('repo', {}).get('name', 'N/A')
                    date = ev.get('created_at', '')
                    console.print(f'  [success]•[/success] [secondary]{date}[/secondary] {ev_type} → {repo_name}')
    except Exception:
        pass

    console.print(f'\n[success]━━━ СТАТИСТИКА ━━━[/success]')
    console.print(f'  [secondary]Репозиториев:[/secondary] {len(repos)}')
    console.print(f'  [secondary]Email найдено:[/secondary] {len(emails_found)}')
    console.print(f'  [secondary]Репозиториев сканировано:[/secondary] {scanned_repos}')
    console.print()
