from modules.imports import *
from modules.config import *
from modules.theme_manager import *
from modules.console import *
from modules.input import *
from functions.hidder import block

import base64
import gzip
import json
import hmac
import binascii
import os
import re
import time
import urllib.parse
from hashlib import md5
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_der_public_key


def flatten_dict(d: dict, parent_key: str = "") -> dict:
    items = []
    for key, value in d.items():
        new_key = f"{parent_key}.{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key).items())
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        for k, v in item.items():
                            items.append((f"{new_key}[{i}].{k}", v))
                    else:
                        items.append((f"{new_key}[{i}]", item))
            else:
                items.append((new_key, json.dumps(value, ensure_ascii=False)))
        else:
            items.append((new_key, value))
    return dict(items)


def clean_phone(phone: str) -> str:
    return re.sub(r"\D", "", phone)


def _base64_encode_bytes(data: bytearray) -> str:
    length = len(data)
    out_size = (length // 3) * 4 + (4 if length % 3 > 0 else 0)
    out = bytearray(out_size)
    pos = 0
    i = 0
    while i < length - 2:
        chunk = base64.b64encode(data[i:i + 3])
        out[pos:pos + len(chunk)] = chunk
        i += 3
        pos += 4
    if i < length:
        chunk = base64.b64encode(data[i:length])
        out[pos:pos + len(chunk)] = chunk
        pos += 4
    return out[:pos].decode("utf-8")


def _transform(s: str) -> str:
    result = []
    for idx, ch in enumerate(s):
        code = ord(ch)
        if 48 <= code <= 57 or 65 <= code <= 90 or 97 <= code <= 122:
            shifted = idx % 5 + code
            if shifted > 122:
                code = shifted - 122 + 47
            elif code <= 90 and shifted > 90:
                code = shifted - 90 + 96
            elif code <= 57 and shifted > 57:
                code = shifted - 57 + 65
            else:
                code = shifted
        result.append(chr(code))
    return "".join(result)


def _reverse_transform(s: str) -> str:
    result = []
    for idx, ch in enumerate(s):
        code = ord(ch)
        if 48 <= code <= 57 or 65 <= code <= 90 or 97 <= code <= 122:
            shifted = code - idx % 5
            if shifted < 48:
                shifted = 122 - (47 - shifted)
            elif code >= 97 and shifted < 97 and shifted > 57:
                shifted = 90 - (96 - shifted)
            elif code >= 65 and shifted < 65 and shifted > 47:
                shifted = 57 - (64 - shifted)
            code = shifted
        result.append(str(code))
    return ",".join(result)


class GetcontactLookup:
    RSA_PUBLIC_KEY_B64 = (
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        "YOUR_API_KEY_HERE"
        "YOUR_API_KEY_HERE"
        "YOUR_API_KEY_HERE"
        "YOUR_API_KEY_HERE"
        "YOUR_API_KEY_HERE"
        "r7HwIDAQAB"
    )

    def __init__(self):
        self.results: dict = {}
        self._sessions = {
            "callapp_1": requests.Session(),
            "callapp_2": requests.Session(),
            "eyecon_1":  requests.Session(),
            "eyecon_2":  requests.Session(),
            "syncme":    requests.Session(),
        }

    def __enter__(self):
        return self

    def __exit__(self, *_):
        for s in self._sessions.values():
            s.close()

    @staticmethod
    def _translate_key(key: str) -> str:
        translations = {
            'status': 'Статус',
            'tel_number': 'Номер телефона',
            'old_tel_number': 'Старый номер',
            'format_tel_number': 'Форматированный номер',
            'operator': 'Оператор',
            'type': 'Тип',
            'type_label': 'Тип метки',
            'report_count': 'Количество отчетов',
            'name': 'Имя',
            'error_log': 'Лог ошибок',
            'faild_error_log': 'Проваленные ошибки',
            'area_error_log': 'Ошибки области',
            'length_error_log': 'Ошибки длины',
            'belong_area': 'Регион',
            'address': 'Адрес',
            'avatar': 'Аватар',
            'website': 'Веб-сайт',
            'soft_comments': 'Комментарии',
            'categories': 'Категории',
            't_p': 'Телефонный префикс',
            'e164_tel_number': 'E164 номер',
            'cc': 'Код страны',
            'error_code': 'Код ошибки',
            'error_description': 'Описание ошибки',
            'priority': 'Приоритет',
            'picture_url': 'URL картинки',
            'facebook_id': 'Facebook ID',
            'facebook_profile': 'Профиль Facebook',
        }
        return translations.get(key, key)

    @staticmethod
    def _print_section(title: str, data: dict):
        if not data:
            return
        console.print(f"\n[success]━━━ {title} ━━━[/success]")
        for key, value in flatten_dict(data).items():
            translated_key = GetcontactLookup._translate_key(key)
            console.print(f"  [success]•[/success] [secondary]{translated_key: <20}[/secondary] {value}")

    def print_results(self):
        self._print_section("GETCONTACT", self.results.get("callerid_aunumber", {}))
        self._print_section("GETCONTACT (CENTRALEVENTS)", self.results.get("centralevents", {}))
        console.print(f"\n[success]✓ Проверка завершена[/success]\n")

    def _check_callerid(self, number: str):
        try:
            ts = str(int(time.time()) + 1)
            phone_e164 = "+" + number
            stamp_raw = f"{phone_e164}{ts}com.callblocker.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
            stamp = md5(stamp_raw.encode()).hexdigest()
            encoded = _base64_encode_bytes(bytearray(phone_e164, "utf-8"))
            transformed = _transform(encoded)
            tel_param = urllib.parse.quote(transformed[0] + "0" + transformed[2:])
            payload = (
                f"cc=972&uid=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
                f"&tel_number={tel_param}&stamp={stamp}"
                f"&device=android&version=1.7.1&default_cc=972&cid="
            )
            headers = {
                "Content-Type":    "application/x-www-form-urlencoded",
                "Content-Length":  str(len(payload)),
                "Accept-Encoding": "gzip",
                "User-Agent":      "okhttp/3.14.9",
            }
            resp = requests.post(
                "https://app.aunumber.com/api/v1/sea.php",
                data=payload, headers=headers, timeout=10,
            )
            ordinals = _reverse_transform(resp.text)
            decoded_chars = "".join(chr(int(c)) for c in ordinals.split(","))
            final_json = base64.b64decode(decoded_chars).decode("utf-8")
            self.results["callerid_aunumber"] = json.loads(final_json)
        except Exception as exc:
            self.results["callerid_aunumber"] = {"error": str(exc)}


    def _check_centralevents(self, number: str):
        try:
            CENTRAL_AES_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' 
            CENTRAL_TOKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
            CENTRAL_HMAC_KEY = b'2Wq7)qkX~cp7)H|n_tc&o+:G_USN3/-uIi~>M+c ;Oq]E{t9)RC_5|lhAA_Qq%_4'

            class CentralAESCipher(object):
                def __init__(self, key_hex):
                    self.bs = 16
                    self.key = binascii.unhexlify(key_hex)
            
                def encrypt(self, raw):
                    raw = self._pad(raw)
                    cipher = Cipher(algorithms.AES(self.key), modes.ECB())
                    enc = cipher.encryptor()
                    return base64.b64encode(enc.update(raw.encode()) + enc.finalize())
            
                def decrypt(self, enc):
                    enc = base64.b64decode(enc)
                    cipher = Cipher(algorithms.AES(self.key), modes.ECB())
                    dec = cipher.decryptor()
                    return self._unpad(dec.update(enc) + dec.finalize()).decode('utf-8')
            
                def _pad(self, s):
                    return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)
            
                @staticmethod
                def _unpad(s):
                    return s[:-ord(s[len(s)-1:])]

            aes = CentralAESCipher(CENTRAL_AES_KEY)
            
            phone_with_plus = "+" + number
            ts = str(int(time.time()))
            
            req_profile = f'"countryCode":"RU","source":"search","token":"{CENTRAL_TOKEN}","phoneNumber":"{phone_with_plus}"'
            req_profile = '{' + req_profile + '}'
            string_profile = str(ts) + '-' + req_profile
            sig_profile = base64.b64encode(hmac.new(CENTRAL_HMAC_KEY, string_profile.encode(), hashlib.sha256).digest()).decode()
            crypt_data_profile = aes.encrypt(req_profile)
            
            headers = {
                'X-App-Version': '4.9.1',
                'X-Token': CENTRAL_TOKEN,
                'X-Os': 'android 5.0',
                'X-Client-Device-Id': '14130e29cebe9c39',
                'Content-Type': 'application/json; charset=utf-8',
                'Accept-Encoding': 'deflate',
                'X-Req-Timestamp': ts,
                'X-Req-Signature': sig_profile,
                'X-Encrypted': '1'
            }
            
            r_profile = requests.post(
                'https://pbssrv-centralevents.com/v2.5/search',
                data=b'{"data":"'+crypt_data_profile+b'"}',
                headers=headers,
                timeout=10,
                verify=True
            )
            data_profile = json.loads(aes.decrypt(r_profile.json()['data']))
            
            res = {}
            if data_profile and 'result' in data_profile and 'profile' in data_profile['result']:
                prof = data_profile['result']['profile']
                if prof.get('displayName'):
                    res['Имя (Centralevents)'] = prof['displayName']
                    res['Количество тегов'] = prof.get('tagCount', 0)
            
            req_tags = f'"countryCode":"RU","source":"details","token":"{CENTRAL_TOKEN}","phoneNumber":"{phone_with_plus}"'
            req_tags = '{' + req_tags + '}'
            string_tags = str(ts) + '-' + req_tags
            sig_tags = base64.b64encode(hmac.new(CENTRAL_HMAC_KEY, string_tags.encode(), hashlib.sha256).digest()).decode()
            crypt_data_tags = aes.encrypt(req_tags)
            
            headers['X-Req-Signature'] = sig_tags
            r_tags = requests.post(
                'https://pbssrv-centralevents.com/v2.5/number-detail',
                data=b'{"data":"'+crypt_data_tags+b'"}',
                headers=headers,
                timeout=10,
                verify=True
            )
            data_tags = json.loads(aes.decrypt(r_tags.json()['data']))
            if data_tags and 'result' in data_tags and 'tags' in data_tags['result']:
                tags = [i['tag'] for i in data_tags['result']['tags']]
                if tags:
                    res['Теги (Centralevents)'] = tags

            if res:
                self.results["centralevents"] = res
        except Exception as exc:
            pass

    def _check_syncme(self, number: str):
        try:
            payload_obj = {
                "phone":               number,
                "manufacturer":        "Asus",
                "model":               "ASUS_Z01QD",
                "version_code":        28,
                "action":              "search",
                "locale":              "en_US",
                "get_hints":           True,
                "is_search":           True,
                "ACCESS_TOKEN":        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                "APPLICATION_ID":      "8a078650-5acd-11e1-b86c-0800200c9a66",
                "X-device-info":       "Asus,ASUS_Z01QD,9",
                "APPLICATION_VERSION": "4.44.6.2",
                "version_number":      497,
                "phone_number":        number,
            }
            raw = json.dumps(payload_obj, separators=(",", ":")).encode("utf-8")
            body = gzip.compress(raw) if len(raw) >= 200 else raw
            aes_key = os.urandom(16)
            iv      = os.urandom(16)
            cipher  = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
            enc     = cipher.encryptor()
            padder  = padding.PKCS7(128).padder()
            padded  = padder.update(body) + padder.finalize()
            ciphertext = enc.update(padded) + enc.finalize()
            wire_body = ciphertext + iv
            pub_key = load_der_public_key(base64.b64decode(self.RSA_PUBLIC_KEY_B64))
            enc_key = pub_key.encrypt(
                aes_key,
                asymmetric_padding.OAEP(
                    mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            headers = {
                "X-SyncME-gzip":           "true",
                "X-SyncME-Key":            base64.b64encode(enc_key).decode(),
                "X-SyncME-Android-Number": "497",
                "Content-Length":          str(len(wire_body)),
                "Host":                    "api.sync.me",
                "Connection":              "Keep-Alive",
                "Accept-Encoding":         "gzip",
                "User-Agent":              "Sync.ME Android 4.44.6.2",
            }
            resp = self._sessions["syncme"].post(
                "https://api.sync.me/api/caller_id/caller_id/v2",
                headers=headers, data=wire_body, timeout=10,
            )
            data = json.loads(resp.content.decode("utf-8"))
            if isinstance(data, list) and data:
                data = data[0]
            self.results["syncme"] = data or {}
        except Exception as exc:
            self.results["syncme"] = {"error": str(exc)}

    def _check_callapp(self, number: str):
        result = None
        try:
            params = {
                "cpn": f"+{number}",
                "myp": "fb.1122543675802814",
                "ibs": "3",
                "tk":  "0017356813",
                "cvc": 2038,
            }
            resp = self._sessions["callapp_1"].get(
                "https://s.callapp.com/callapp-server/csrch",
                params=params, timeout=10,
            )
            if resp.status_code == 200:
                result = resp.json()
        except Exception:
            pass
        if not result:
            try:
                url = (
                    f"https://s.callapp.com/callapp-server/csrch"
                    f"?cpn=%2B{number}&myp=gp.106898501948939491020"
                    f"&ibs=0&cid=0&tk=0011243853&cvc=2206"
                )
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Host":       "s.callapp.com",
                    "Connection": "Keep-Alive",
                }
                resp = self._sessions["callapp_2"].get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    result = resp.json()
            except Exception:
                pass
        self.results["callapp"] = result or {}

    def _check_eyecon(self, number: str):
        data = {}
        auth_headers = {
            "e-auth-v": "e1",
            "e-auth":   "d9889e1c-521c-4ded-9b15-f64bb069148b",
            "e-auth-c": "46",
            "e-auth-k": "PgdtSBeR0MumR7fO",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        cv = "vc_742_vn_4.2026.02.24.1801_a"
        try:
            resp = self._sessions["eyecon_1"].get(
                "https://api.eyecon-app.com/app/getnames.jsp",
                headers={**auth_headers, "accept": "application/json",
                         "accept-charset": "UTF-8",
                         "content-type": "application/x-www-form-urlencoded; charset=utf-8",
                         "Host": "api.eyecon-app.com"},
                params={"cli": number, "lang": "ru", "is_callerid": "true",
                        "is_ic": "true", "cv": cv,
                        "requestApi": "URLconnection", "source": "MenifaFragment"},
                timeout=10,
            )
            if resp.status_code == 200:
                names = resp.json()
                if names:
                    data = names[0]
            resp_pic = self._sessions["eyecon_2"].get(
                "https://api.eyecon-app.com/app/pic",
                headers=auth_headers,
                params={"cli": number, "is_callerid": "true", "size": "big",
                        "type": "0", "src": "MenifaFragment",
                        "cancelfresh": "0", "cv": cv},
                allow_redirects=False,
                timeout=10,
            )
            if resp_pic.status_code in (200, 302):
                location = resp_pic.headers.get("Location", "")
                if location:
                    data["picture_url"] = location
                    m = re.search(r"graph\.facebook\.com/(\d+)/picture", location)
                    if m:
                        fb_id = m.group(1)
                        data["facebook_id"]      = fb_id
                        data["facebook_profile"] = f"https://www.facebook.com/profile.php?id={fb_id}"
        except Exception as exc:
            data["error"] = str(exc)
        self.results["eyecon"] = data

    def search(self, raw_number: str) -> dict | None:
        number = clean_phone(raw_number)
        if not number.isdigit():
            console.print(f"Неверный номер телефона: {raw_number!r}")
            return None
        self._check_callerid(number)
        self._check_centralevents(number)
        return self.results


def getcontact_search(phone: str):
    if block(phone, 'phone'): return
    console.print(f'\n[secondary]Поиск Getcontact:[/secondary] [bold]{phone}[/bold]\n')
    
    with GetcontactLookup() as lookup:
        result = lookup.search(phone)
        if result is not None:
            lookup.print_results()
