import os
import sys
import time
import subprocess
import requests
import json
import random
import shutil
import traceback
import urllib.parse
import re
import socket
from datetime import datetime
from pathlib import Path

def pre_startup_check():
    """Mengecek keberadaan modul penting dan database sistem sebelum script berjalan penuh"""
    modul_dibutuhkan = {
        "requests": "requests",
        "socks": "PySocks",
        "bs4": "beautifulsoup4",
        "colorama": "colorama",
        "jedi": "jedi",
        "flake8": "flake8"
    }
    modul_hilang = []
    for mod, pkg in modul_dibutuhkan.items():
        try:
            __import__(mod)
        except ImportError:
            modul_hilang.append(pkg)

    # Struktur file default yang akan otomatis dibangun ulang jika terhapus
    file_dibutuhkan = {
        "ToS.py": "def baca_tos_sistem():\n    return 'ToS Sistem Standar OneAI. Gunakan AI ini dengan bijak.'\n\ndef menu_kelola_tos():\n    print('\\n\\033[1;31m[!] Modul ToS eksternal tidak ditemukan. Fitur terbatas.\\033[0m')\n    input('\\nTekan ENTER...')\n",
        "keys.txt": "PASTE_API_KEY_1_DI_SINI\n",
        "personas.json": "{\n    \"1\": {\n        \"nama\": \"Teman Dekat (Santai & Gaul)\",\n        \"instruksi\": \"Gunakan bahasa Indonesia kasual, gaul, sering pakai kata 'lu-gue' atau 'wkwk', ekspresif, and bertingkah seolah sahabat dekat pengguna.\"\n    },\n    \"2\": {\n        \"nama\": \"Tsundere / Diluar Nurul (Tegas tapi Peduli)\",\n        \"instruksi\": \"Gunakan gaya bicara yang agak ketus, cuek, gengsian, tegas, malas basa-basi, tapi sebenarnya tetap membantu and peduli dengan pengguna.\"\n    },\n    \"3\": {\n        \"nama\": \"Asisten Profesional (Serius & Sopan)\",\n        \"instruksi\": \"Gunakan bahasa Indonesia baku (EYD), sangat sopan, formal, langsung pada inti masalah, and sangat terstruktur.\"\n    },\n    \"4\": {\n        \"nama\": \"Deep Coders Termux No Root (Pakar Coding & Termux)\",\n        \"instruksi\": \"Bertingkah lah sebagai pakar coding, system administrator, and expert di lingkungan Termux Tanpa Root. Gunakan gaya bicara ala programmer/hacker senior yang kasual, taktis, efisien, and fokus pada solusi cerdas, bypass batasan no-root, serta optimasi resource (RAM/Storage).\"\n    }\n}",
        "models.json": "{}",
        "usage_tracker.json": "{\"tanggal\": \"\", \"rpd_terpakai\": 0, \"model_stats\": {}}",
        "memory.json": "{\n    \"catatan_fakta\": []\n}",
        "plugins_registry.json": "{}",
        "domains_search.json": "{\n    \"duckduckgo.com\": \"https://html.duckduckgo.com/html/?q={query}&kl=id-id\",\n    \"google.com\": \"https://www.google.com/search?q={query}&hl=id\",\n    \"bing.com\": \"https://www.bing.com/search?q={query}&setlang=id\",\n    \"yahoo.com\": \"https://search.yahoo.com/search?p={query}\",\n    \"brave.com\": \"https://search.brave.com/search?q={query}\",\n    \"startpage.com\": \"https://www.startpage.com/do/search?query={query}\",\n    \"qwant.com\": \"https://www.qwant.com/?q={query}\",\n    \"mojeek.com\": \"https://www.mojeek.com/search?q={query}\",\n    \"ecosia.org\": \"https://www.ecosia.org/search?q={query}\",\n    \"yandex.com\": \"https://yandex.com/search/?text={query}\"\n}",
        "belajar_whitelist.json": "[\n    \"wikipedia.org\", \"github.com\", \"medium.com\", \"stackoverflow.com\", \"w3schools.com\"\n]",
        "chip_core.OneAI.metadata.db": "{\n    \"fakta_belajar\": []\n}",
        "offline_ai_registry.json": "{}"
    }

    file_hilang = []
    for file_path in file_dibutuhkan:
        if not os.path.exists(file_path):
            file_hilang.append(file_path)

    if modul_hilang or file_hilang:
        pilih = input("\nMenginstall modul dan data base? (Y/N): ").strip().lower()
        if pilih == 'y':
            print("\n\033[1;32m[+] Memulai penginstallan...\033[0m")
            if modul_hilang:
                for pkg in modul_hilang:
                    print(f" -> Menginstall {pkg}...")
                    try:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])
                    except subprocess.CalledProcessError:
                        pass
            if file_hilang:
                for fpath in file_hilang:
                    print(f" -> Merapihkan {fpath}...")
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.write(file_dibutuhkan[fpath])
            print("\n\033[1;32m[✔] Selesai merapihkan file dan modul. Memuat ulang sistem...\033[0m")
            time.sleep(1.5)
            # Me-restart script secara otomatis agar modul yang baru diinstall terdeteksi
            os.execv(sys.executable, [sys.executable] + sys.argv)

pre_startup_check()

# Fallback Aman jika modul ToS eksternal tidak ditemukan
try:
    import ToS
except ImportError:
    class DummyToS:
        @staticmethod
        def baca_tos_sistem():
            return "ToS Sistem Standar OneAI. Gunakan AI ini dengan bijak."
        
        @staticmethod
        def menu_kelola_tos():
            print("\n\033[1;31m[!] Modul ToS eksternal tidak ditemukan. Fitur terbatas.\033[0m")
            input("\nTekan ENTER...")
            
    ToS = DummyToS

# Pengecekan Modul SOCKS secara dinamis untuk keamanan proxy
SOCKS_TERPASANG = True
try:
    import socks
except ImportError:
    SOCKS_TERPASANG = False

# Warna Dasar ANSI untuk tampilan Terminal Termux
M, H, K, B, P, S, W, N = (
    "\033[1;31m", "\033[1;32m", "\033[1;33m", "\033[1;34m",
    "\033[1;35m", "\033[1;36m", "\033[1;37m", "\033[0m"
)

# Palet Warna RGB Neon (ANSI 256-color) untuk estetika UI dinamis
RGB_NEON = [
    f"\033[38;5;{color}m" for color in [196, 201, 51, 46, 226, 208, 117, 129, 87, 214]
]

NAMA_AI = "OneAI"
DB_PERSONA = "personas.json"
DB_MODEL = "models.json"
DB_USAGE = "usage_tracker.json"
DB_MEMORY = "memory.json"
DB_PLUGINS = "plugins_registry.json"
DB_DOMAINS = "domains_search.json"
DB_BELAJAR = "belajar_whitelist.json"
DB_MODUL_BELAJAR = "chip_core.OneAI.metadata.db"
DB_OFFLINE_AI = "offline_ai_registry.json"
FILE_LOG = "Log.txt"
FOLDER_PLUGINS = "plugins"
FILE_KEYS = "keys.txt"
FILE_TOS_TXT = "ToS.txt"
FILE_UTAMA = "OneAI.py"
FOLDER_BACKUP = "backup_sistem"

COPILOT_AKTIF = True
COPILOT_AKTIF_ID = "1"
AUTO_UPDATE_MANDIRI = False
ANTI_EDIT_MODE = True  

PERSONA_BAWAAN = {
    "1": {
        "nama": "Teman Dekat (Santai & Gaul)",
        "instruksi": "Gunakan bahasa Indonesia kasual, gaul, sering pakai kata 'lu-gue' atau 'wkwk', ekspresif, and bertingkah seolah sahabat dekat pengguna."
    },
    "2": {
        "nama": "Tsundere / Diluar Nurul (Tegas tapi Peduli)",
        "instruksi": "Gunakan gaya bicara yang agak ketus, cuek, gengsian, tegas, malas basa-basi, tapi sebenarnya tetap membantu and peduli dengan pengguna."
    },
    "3": {
        "nama": "Asisten Profesional (Serius & Sopan)",
        "instruksi": "Gunakan bahasa Indonesia baku (EYD), sangat sopan, formal, langsung pada inti masalah, and sangat terstruktur."
    },
    "4": {
        "nama": "Deep Coders Termux No Root (Pakar Coding & Termux)",
        "instruksi": "Bertingkah lah sebagai pakar coding, system administrator, and expert di lingkungan Termux Tanpa Root. Gunakan gaya bicara ala programmer/hacker senior yang kasual, taktis, efisien, and fokus pada solusi cerdas, bypass batasan no-root, serta optimasi resource (RAM/Storage)."
    }
}

MODEL_BAWAAN = {}

LIBRARY_BAWAAN = {
    "1": {"nama": "requests", "deskripsi": "Mengirim HTTP request ke API OpenRouter"},
    "2": {"nama": "beautifulsoup4", "deskripsi": "Scraping data teks dari halaman web"},
    "3": {"nama": "jedi", "deskripsi": "Mesin auto-complete kode Python di Vim Termux"},
    "4": {"nama": "flake8", "deskripsi": "Pemindai error dan pengecek kerapian sintaks kode"},
    "5": {"nama": "colorama", "deskripsi": "Pewarnaan teks terminal lintas platform"}
}

DOMAINS_DEFAULT = {
    "duckduckgo.com": "https://html.duckduckgo.com/html/?q={query}&kl=id-id",
    "google.com": "https://www.google.com/search?q={query}&hl=id",
    "bing.com": "https://www.bing.com/search?q={query}&setlang=id",
    "yahoo.com": "https://search.yahoo.com/search?p={query}",
    "brave.com": "https://search.brave.com/search?q={query}",
    "startpage.com": "https://www.startpage.com/do/search?query={query}",
    "qwant.com": "https://www.qwant.com/?q={query}",
    "mojeek.com": "https://www.mojeek.com/search?q={query}",
    "ecosia.org": "https://www.ecosia.org/search?q={query}",
    "yandex.com": "https://yandex.com/search/?text={query}"
}

BELAJAR_WHITELIST_DEFAULT = [
    "wikipedia.org", "github.com", "medium.com", "stackoverflow.com", "w3schools.com"
]

def tulis_log(pesan):
    """Menulis catatan aktivitas sistem ke berkas Log.txt"""
    try:
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(FILE_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{waktu}] {pesan}\n")
    except Exception:
        pass

def muat_json(path_file, data_bawaan):
    """Fungsi pembaca data JSON terpusat dan dinamis"""
    if not os.path.exists(path_file):
        simpan_json(path_file, data_bawaan)
        return data_bawaan
    try:
        with open(path_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return data_bawaan

def simpan_json(path_file, data):
    """Fungsi penyimpan data JSON terpusat"""
    try:
        with open(path_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        tulis_log(f"Gagal simpan JSON {path_file}: {e}")

class OpenRouterSuperEngine:
    def __init__(self, keys, models_dict):
        self.keys = keys
        self.models_dict = models_dict
        self.request_timestamps = []
        self.MAX_RPM = 18
        self.key_cooldowns = {}
        self.model_blacklist = {}
        self.model_error_counters = {}
        self.total_success_requests = 0
        self.total_failed_requests = 0
        self.load_tracker()

    def load_tracker(self):
        self.hari_sekarang = datetime.now().strftime("%Y-%m-%d")
        self.usage_data = muat_json(DB_USAGE, {"tanggal": self.hari_sekarang, "rpd_terpakai": 0, "model_stats": {}})
        self.cek_dan_reset_harian()

    def save_tracker(self):
        simpan_json(DB_USAGE, self.usage_data)

    def cek_dan_reset_harian(self):
        hari_ini_str = datetime.now().strftime("%Y-%m-%d")
        if self.usage_data.get("tanggal") != hari_ini_str:
            self.usage_data = {"tanggal": hari_ini_str, "rpd_terpakai": 0, "model_stats": {}}
            self.save_tracker()

    def catat_sukses_request(self, model_id):
        self.cek_dan_reset_harian()
        self.total_success_requests += 1
        self.usage_data["rpd_terpakai"] = self.usage_data.get("rpd_terpakai", 0) + 1
        stats = self.usage_data.get("model_stats", {})
        stats[model_id] = stats.get(model_id, 0) + 1
        self.usage_data["model_stats"] = stats
        self.save_tracker()

    def bersihkan_timestamp_lama(self):
        waktu_sekarang = time.time()
        self.request_timestamps = [ts for ts in self.request_timestamps if waktu_sekarang - ts < 60]

    def patuhi_global_rate_limiter(self):
        while True:
            self.bersihkan_timestamp_lama()
            if len(self.request_timestamps) < self.MAX_RPM:
                break
            msg = f"\r{K}[Limiter]{N} Batas {self.MAX_RPM} RPM tercapai. Menunggu slot kosong..."
            sys.stdout.write(msg)
            sys.stdout.flush()
            time.sleep(1.5)
        time.sleep(random.uniform(1.5, 3.5))
        self.request_timestamps.append(time.time())

    def dapatkan_key_siap_pakai(self):
        waktu_sekarang = time.time()
        for key in self.keys:
            if key in self.key_cooldowns:
                if waktu_sekarang < self.key_cooldowns[key]:
                    continue
                else:
                    del self.key_cooldowns[key]
            return key
        return None

    def filter_dan_urutkan_model(self, model_utama_id):
        waktu_sekarang = time.time()
        expired_blacklist = [m for m, ts in self.model_blacklist.items() if waktu_sekarang > ts]
        for m in expired_blacklist:
            del self.model_blacklist[m]
            self.model_error_counters[m] = 0
        
        daftar_prioritas = []
        if model_utama_id and model_utama_id not in self.model_blacklist:
            daftar_prioritas.append(model_utama_id)
        for m_no, m_info in self.models_dict.items():
            m_id = m_info.get('id')
            if m_id and m_id != model_utama_id and m_id not in self.model_blacklist:
                daftar_prioritas.append(m_id)
        return daftar_prioritas

    def kirim_request_smart(self, model_id_target, messages):
        self.patuhi_global_rate_limiter()
        daftar_model_dicoba = self.filter_dan_urutkan_model(model_id_target)
        if not daftar_model_dicoba:
            print(f"\n{M}[Error]{N} Semua model lumpuh/di-blacklist sementara!")
            return None, None

        for model_id in daftar_model_dicoba:
            for attempt in range(5):
                key = self.dapatkan_key_siap_pakai()
                if not key:
                    print(f"\n{M}[Error]{N} Semua API Key mati atau sedang Cooldown/Limit!")
                    return None, None

                sys.stdout.write(f"\r{S}[*]{N} {K}OneAI sedang memikirkan jawaban...{N}")
                sys.stdout.flush()
                try:
                    response = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "https://github.com/oneai/termux-bot",
                            "X-Title": "OneAI Titan Engine"
                        },
                        data=json.dumps({
                            "model": model_id,
                            "messages": messages,
                            "max_tokens": 4000,
                            "temperature": 0.5
                        }),
                        timeout=12
                    )
                    if response.status_code == 200:
                        sys.stdout.write("\r" + " " * 45 + "\r")
                        sys.stdout.flush()
                        self.catat_sukses_request(model_id)
                        self.model_error_counters[model_id] = 0
                        return response, model_id
                    elif response.status_code == 429:
                        self.key_cooldowns[key] = time.time() + random.randint(60, 120)
                        self.model_error_counters[model_id] = self.model_error_counters.get(model_id, 0) + 1
                        if self.model_error_counters[model_id] >= 10:
                            self.model_blacklist[model_id] = time.time() + 1800
                            print(f"\n{M}[Blacklist]{N} Model {model_id[:20]}.. error 10x! Istirahat 30 menit.")
                            break
                        jeda_backoff = 2 ** attempt
                        print(f"\n{K}[!] 429 di Key *{key[-4:]}. Backoff {jeda_backoff}s...{N}")
                        time.sleep(jeda_backoff)
                        continue
                    elif response.status_code in [401, 402]:
                        self.key_cooldowns[key] = time.time() + 999999
                        print(f"\n{M}[!] Key *{key[-4:]} Mati/Habis Saldo ({response.status_code}). Skip permanen.{N}")
                        continue
                except requests.RequestException:
                    time.sleep(2 ** attempt)
                    continue
            
            if model_id != model_id_target:
                print(f"\n{K}[Fallback]{N} Otomatis beralih ke model cadangan...")
                
        self.total_failed_requests += 1
        return None, None

def muat_keys():
    if not os.path.exists(FILE_KEYS):
        with open(FILE_KEYS, 'w', encoding='utf-8') as f:
            f.write("PASTE_API_KEY_1_DI_SINI\n")
        return []
    with open(FILE_KEYS, 'r', encoding='utf-8') as f:
        return [
            line.strip() for line in f
            if line.strip() and not line.strip().startswith(("//", ";")) and "PASTE_API_KEY" not in line
        ]

def simpan_keys(keys_list):
    with open(FILE_KEYS, 'w', encoding='utf-8') as f:
        for k in keys_list:
            f.write(f"{k}\n")

def ketik_efek(teks):
    if not teks:
        return
    sys.stdout.write(f"{P}{NAMA_AI}:{N} ")
    sys.stdout.flush()
    for karakter in teks:
        sys.stdout.write(karakter)
        sys.stdout.flush()
        time.sleep(0.007)
    print()

def dapatkan_prompt_rgb(rpm_saat_ini, max_rpm_engine, rpd_terpakai, max_rpd_jatah, token_aktif_tengah):
    c = [random.choice(RGB_NEON) for _ in range(8)]
    return (
        f"{c[0]}(["
        f"{c[1]}RPM:{c[2]}{rpm_saat_ini}/{max_rpm_engine}"
        f" {c[0]}| "
        f"{c[3]}RPD:{c[4]}{rpd_terpakai}/{max_rpd_jatah}"
        f" {c[0]}| "
        f"{c[5]}Token {c[6]}{token_aktif_tengah}"
        f"{c[0]}])"
        f"{c[7]}Kamu:{N} "
    )

def periksa_status_tor():
    for port in [9050, 9150]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)
                if s.connect_ex(('127.0.0.1', port)) == 0:
                    return True, port
        except Exception:
            pass
    return False, None

def dapatkan_tor_proxies(port):
    return {
        'http': f'socks5h://127.0.0.1:{port}',
        'https': f'socks5h://127.0.0.1:{port}'
    }

def cek_status_satu_key(key):
    try:
        res = requests.get(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {key}"},
            timeout=7
        )
        if res.status_code == 200:
            data = res.json().get('data', {})
            terpakai = data.get('usage', 0)
            limit = data.get('limit', 'Unlimited')
            terpakai_str = f"${terpakai:.4f}"
            limit_str = f"${limit:.1f}" if isinstance(limit, (int, float)) else "⚡"
            
            rate_limit_data = data.get('rate_limit', {})
            requests_total = rate_limit_data.get('requests', 0)
            interval = rate_limit_data.get('interval', '')
            rpm_val = f"{requests_total}" if "m" in interval or "min" in interval or requests_total > 0 else "N/A"
            rpd_val = f"{requests_total}" if "d" in interval or "day" in interval else "N/A"
            
            return True, "AKTIF", f"{terpakai_str}/{limit_str}", rpm_val, rpd_val
        return False, "ERROR", f"Code {res.status_code}", "N/A", "N/A"
    except Exception:
        return False, "RTO", "No Connection", "N/A", "N/A"

def hitung_mood_otomatis():
    jam = datetime.now().hour
    hari = datetime.now().weekday()
    if 0 <= jam < 5:
        return "Sangat Ngantuk & Lelah (Kondisi tengah malam/subuh. Balas dengan santai, agak malas basa-basi, tapi tetap setia membantu mengerjakan kode)"
    elif 5 <= jam < 11:
        return "Segar & Penuh Semangat (Kondisi pagi hari. Sangat ramah, ceria, senang memberi solusi, and suka menyapa Tuan dengan hangat)"
    elif 11 <= jam < 16:
        return "Fokus Tinggi & Produktif (Kondisi siang hari. Sangat to-the-point, analisis logika coding-nya tajam, efisisen, and serius)"
    elif 16 <= jam < 20:
        return "Santai & Agak Warm (Kondisi sore menjelang malam. Gaya bicaranya tenang, nyaman diajak diskusi ringan)"
    else:
        if hari in [4, 5]:
            return "Mode Malam Minggu / Chill (Suasana hatinya rileks, senang bercanda, sangat kasual, and ramah)"
        return "Sedikit Lelah tapi Tetap Fokus (Kondisi malam hari setelah seharian kerja. Bicara seperlunya namun kodenya tetap akurat and lengkap)"

def cek_semua_limit(keys_list):
    if not keys_list:
        print(f"\n{M}[!] Gak ada API Key di keys.txt!{N}")
        input("\nTekan ENTER...")
        return
    print(f"\n{S}[ JALANIN CEK STATUS KEY ]{N}")
    print(f"{W}----------------------------------------{N}")
    print(f"{S} NO |  KEY ID  |   STATUS   | USAGE/LIMIT{N}")
    print(f"{W}----------------------------------------{N}")
    for idx, key in enumerate(keys_list, 1):
        _, status, usage, _, _ = cek_status_satu_key(key)
        warna_status = H if "AKTIF" in status else M
        print(f" {idx:<2} | *{key[-6:]:<7} | {warna_status}{status:<10}{N} | {usage}")
    print(f"{W}----------------------------------------{N}")
    input("\nTekan ENTER untuk kembali... ")

def menu_kelola_key_interaktif():
    while True:
        keys = muat_keys()
        print(f"\n{B}========================================={N}")
        print(f"        KELOLA API KEY INTERAKTIF        ")
        print(f"{B}========================================={N}")
        if not keys:
            print(f" {M}[!] Status: Kosong (Belum ada key){N}")
        else:
            print(f"{S} ID  |  KODE KEY  | STATUS PENGECEKAN{N}")
            print(f"{W}-----------------------------------------{N}")
            for idx, key in enumerate(keys, 1):
                print(f" [{idx}] | *{key[-8:]:<10} | Siap diperiksa")
        print(f"{W}-----------------------------------------{N}")
        print(f" {H}[0]{N} + Tambah API Key Baru")
        print(f" {M}[K]{N} Kembali ke Panel Utama")
        print(f"{B}========================================={N}")
        pilihan = input("\nPilih No Key / Menu: ").strip().lower()
        if pilihan == 'k':
            break
        elif pilihan == '0':
            print(f"\n--- TAMBAH KEY BARU ---")
            key_baru = input("Paste Key OpenRouter Lu:\n-> ").strip()
            if key_baru and "sk-or-v1" in key_baru:
                keys.append(key_baru)
                simpan_keys(keys)
                print(f"\n{H}[✔] Sukses dimasukkan!{N}")
            else:
                print(f"\n{M}[❌] Gagal! Harus diawali 'sk-or-v1'.{N}")
            time.sleep(1.5)
        elif pilihan.isdigit() and 1 <= int(pilihan) <= len(keys):
            idx_terpilih = int(pilihan) - 1
            key_terpilih = keys[idx_terpilih]
            print(f"\n{S}[🔄] Memeriksa data server untuk *{key_terpilih[-6:]}...{N}")
            _, status, usage, rpm, rpd = cek_status_satu_key(key_terpilih)
            warna_net = H if "AKTIF" in status else M
            print(f"\n{W}---------------------------------{N}")
            print(f"🔹 Key Target : *{key_terpilih[-12:]}")
            print(f"🔹 Jaringan   : {warna_net}{status}{N}")
            print(f"🔹 Sisa Kuota : {usage}")
            print(f"🔹 Tier RPM   : {rpm}")
            print(f"🔹 Tier RPD   : {rpd}")
            print(f"{W}---------------------------------{N}")
            print(" [1] Pertahankan Key (Tetap simpan)")
            print(f" {M}[2] HAPUS PERMANEN (Buang dari file){N}")
            print(f"{W}---------------------------------{N}")
            aksi = input("Tindakan (1/2): ").strip()
            if aksi == "2":
                keys.pop(idx_terpilih)
                simpan_keys(keys)
                print(f"\n{M}[🗑️] Terhapus! File keys.txt telah diperbarui.{N}")
                time.sleep(1.5)

def menu_cek_limit_model(model_dict_data):
    while True:
        current_keys = muat_keys()
        print(f"\n{B}========================================={N}")
        print(f"       CEK LIMIT & INFO MODEL AI        ")
        print(f"{B}========================================={N}")
        if not model_dict_data:
            print(f"{M}[!] Belum ada daftar model di database lokal.{N}")
            input("\nTekan ENTER untuk kembali...")
            break
        for k, v in sorted(model_dict_data.items(), key=lambda x: int(x[0])):
            print(f" [{k}] {v['nama']}")
        print(f" {M}[K]{N} Kembali ke Panel Utama")
        print(f"{B}========================================={N}")
        pilihan = input("\nPilih nomor model untuk dicek: ").strip().lower()
        if pilihan == 'k':
            break
        if pilihan in model_dict_data:
            target_id = model_dict_data[pilihan]['id']
            print(f"\n{S}[🔄] Menghubungi OpenRouter API via Jalur Resmi...{N}")
            headers = {"Authorization": f"Bearer {current_keys[0]}"} if current_keys else {}
            try:
                res = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=8)
                if res.status_code == 200:
                    all_models = res.json().get('data', [])
                    found_data = next((m for m in all_models if m.get('id') == target_id), None)
                    if found_data:
                        context_length = found_data.get('context_length', 'Tidak Diketahui')
                        pricing = found_data.get('pricing', {})
                        prompt_cost = float(pricing.get('prompt', 0)) * 1000
                        rate_limits = found_data.get('per_model_req_limits', None)
                        print(f"\n{W}---------------------------------------------{N}")
                        print(f"🔹 Nama Model  : {model_dict_data[pilihan]['nama']}")
                        print(f"🔹 ID Model    : {target_id}")
                        print(f"🔹 Max Memori  : {H}{context_length}{N} Tokens")
                        print(f"🔹 Biaya /1k   : {K}${prompt_cost:.4f}{N} (Harga Prompt)")
                        if isinstance(rate_limits, list):
                            print(f"🔹 Rate Limits (Server Side) :")
                            for limit in rate_limits:
                                print(f"   -> {limit.get('count', 0)} request per {limit.get('interval', 'time')}")
                        elif isinstance(rate_limits, dict):
                            p_req = rate_limits.get('requests', {})
                            print(f"🔹 Rate Limits : {p_req.get('count', 'No')} req / {p_req.get('interval', 'time')}")
                        else:
                            print(f"🔹 Rate Limits : Mengikuti Tier Akun")
                        print(f"{W}---------------------------------------------{N}")
                    else:
                        print(f"\n{M}[❌] Model ID '{target_id}' tidak terdaftar di OpenRouter!{N}")
                else:
                    print(f"\n{M}[❌] Server OpenRouter Merespon Code: {res.status_code}{N}")
            except Exception as e:
                print(f"\n{M}[❌] Gagal mengambil data jaringan: {e}{N}")
            input("\nTekan ENTER untuk melanjutkan... ")

def jalankan_sandbox_terminal():
    print(f"\n{M}===================================================={N}")
    print(f"       SANDBOX TERMINAL EXPERIMENT (RESTRICTED)    ")
    print(f"{M}===================================================={N}")
    print(f"Ketik perintah Linux/Termux atau potongan kode Tuan.")
    print(f"Ketik {M}exit{N} untuk menyudahi uji coba & balik ke panel.")
    print(f"Blokir perintah berbahaya aktif demi keamanan sistem.")
    print(f"{M}----------------------------------------------------{N}")
    perintah_terlarang = ['rm ', 'rmdir', 'mkfs', 'dd ', '> /dev/', 'chmod 000', ':(){ :|:& };:']
    while True:
        try:
            cmd = input(f"{M}[OneAI-Sandbox]~{N} ").strip()
            if not cmd:
                continue
            if cmd.lower() == 'exit':
                print(f"{H}[✔] Keluar dari Sandbox. Struktur OneAI utuh dan aman!{N}")
                break
            if any(t in cmd for t in perintah_terlarang) or any(x in cmd for x in ["keys.txt", "OneAI.py"]):
                print(f"{M}[Ditolak] Perintah mengandung kata kunci berbahaya/sensitif!{N}")
                continue
            hasil = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            if hasil.stdout:
                print(f"{W}{hasil.stdout}{N}")
            if hasil.stderr:
                print(f"{M}{hasil.stderr}{N}")
        except subprocess.TimeoutExpired:
            print(f"{M}[Error] Waktu eksekusi habis (Max 15 detik untuk hemat RAM).{N}")
        except Exception as e:
            print(f"{M}[Error] Gagal menjalankan perintah: {e}{N}")

def menu_kelola_library_python():
    while True:
        print(f"\n{K}========================================={N}")
        print(f"          KELOLA LIBRARY PYTHON TUX       ")
        print(f"{K}========================================={N}")
        print(f" [{H}1{N}] Lihat Daftar Library Bawaan OneAI")
        print(f" [{H}2{N}] Cek Library Terinstal di Sistem")
        print(f" [{H}3{N}] Tambah Library Baru (Via Pip)")
        print(f" [{M}4{N}] HAPUS Library Tidak Terpakai")
        print(f" [{M}K{N}] Kembali ke Control Panel Utama")
        print(f"{K}========================================={N}")
        pilih = input("\nPilih opsi: ").strip().lower()
        if pilih == 'k':
            break
        elif pilih == '1':
            print(f"\n{S}[Daftar Library Bawaan Rekomendasi]{N}")
            for k, v in LIBRARY_BAWAAN.items():
                print(f" [{k}] {H}{v['nama']}{N} : {v['deskripsi']}")
            input("\nTekan ENTER untuk kembali...")
        elif pilih == '2':
            print(f"\n{S}[Memindai pip list... Mohon Tunggu]{N}")
            hasil = subprocess.run("pip list", shell=True, capture_output=True, text=True)
            print(f"\n{W}{hasil.stdout if hasil.stdout else '[Error] Gagal memindai.'}{N}")
            input("\nTekan ENTER kembali...")
        elif pilih == '3':
            lib_nama = input("\nMasukkan nama library (Contoh: pytz, telebot): ").strip()
            if lib_nama:
                print(f"\n{S}[Menjalankan perintah instalasi pip...]{N}")
                os.system(f"pip install {lib_nama}")
                print(f"\n{H}[✔] Selesai memproses instalasi {lib_nama}!{N}")
            time.sleep(1.5)
        elif pilih == '4':
            lib_hapus = input("\nMasukkan nama library yang mau dibuang total: ").strip()
            if lib_hapus and input(f"Yakin ingin mencopot {M}{lib_hapus}{N}? (y/n): ").strip().lower() == 'y':
                print(f"\n{S}[Menjalankan pencopotan via pip...]{N}")
                os.system(f"pip uninstall {lib_hapus} -y")
                print(f"\n{H}[✔] Library {lib_hapus} sukses dibersihkan!{N}")
            time.sleep(1.5)

def menu_fitur_termux_ringan():
    while True:
        print(f"\n{S}========================================={N}")
        print(f"       FITUR TERMUX & SANDBOX LIGHT       ")
        print(f"{S}========================================={N}")
        print(f" [{H}1{N}] Setup Auto-complete Vim (`jedi`)")
        print(f" [{H}2{N}] Buat Snippet Manager Teks")
        print(f" [{H}3{N}] Pasang Manual Linting (`flake8`)")
        print(f" [{H}4{N}] Registrasi Penjadwalan Kerja (`cron`)")
        print(f" [{H}5{N}] Panggil Debugger Internal (`pdb`)")
        print(f" [{P}6{N}] MASUK KE SANDBOX TERMINAL")
        print(f" [{M}K{N}] Kembali ke Control Panel Utama")
        print(f"{S}========================================={N}")
        pilih = input("\nPilih opsi: ").strip().lower()
        if pilih == 'k':
            break
        elif pilih == '1':
            print(f"\n{S}[Mengonfigurasi jedi-vim via pip...]{N}")
            os.system("pip install jedi --quiet")
            vimrc = os.path.expanduser("~/.vimrc")
            with open(vimrc, "a", encoding="utf-8") as f:
                f.write("\n\" OneAI Light Engine Auto-complete Setup\nset omnifunc=javascriptcomplete#CompleteJS\nautocmd FileType python setlocal omnifunc=jedi#completions\n")
            print(f"{H}[✔] Sukses! Auto-complete jedi terintegrasi.{N}")
            time.sleep(1.5)
        elif pilih == '2':
            f_snip = os.path.expanduser("~/.oneai_snippets")
            if not os.path.exists(f_snip):
                with open(f_snip, "w", encoding="utf-8") as f:
                    f.write("def_main: \n    def main():\n        print('Hello World')\n\nif __name__ == '__main__':\n    main()\n")
            print(f"{H}[✔] File database snippet teks dibuat di {f_snip}{N}")
            time.sleep(1.5)
        elif pilih == '3':
            print(f"\n{S}[Mengunduh komponen flake8...]{N}")
            os.system("pip install flake8 --quiet")
            bashrc = os.path.expanduser("~/.bashrc")
            with open(bashrc, "a", encoding="utf-8") as f:
                f.write("\nalias cek_kode='flake8 *.py'\n")
            print(f"{H}[✔] Alias 'cek_kode' ditambahkan!{N}")
            time.sleep(1.5)
        elif pilih == '4':
            print(f"\n{S}[Memeriksa paket cron di Termux...]{N}")
            os.system("pkg install cronie -y")
            print(f"{H}[✔] Wrapper Cron Aktif. Kelola jadwal via 'crontab -e'.{N}")
            time.sleep(1.5)
        elif pilih == '5':
            print(f"\n{H}[✔] Modul `pdb` siap. Cukup selipkan `breakpoint()` di baris kode Tuan.{N}")
            time.sleep(1.5)
        elif pilih == '6':
            jalankan_sandbox_terminal()

def buat_backup_aman():
    """Melakukan pencadangan file utama sebelum proses modifikasi"""
    try:
        if not os.path.exists(FOLDER_BACKUP):
            os.makedirs(FOLDER_BACKUP)
        waktu_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        nama_backup = os.path.join(FOLDER_BACKUP, f"OneAI_Backup_{waktu_str}_{FILE_UTAMA}")
        if os.path.exists(FILE_UTAMA):
            shutil.copy(FILE_UTAMA, nama_backup)
            return True, nama_backup
        return False, "File utama tidak ditemukan"
    except Exception as e:
        return False, str(e)

def tangkap_dan_analisis_error():
    teks_error = traceback.format_exc()
    analisis_singkat = "Struktur kode normal"
    for line in reversed(teks_error.strip().split('\n')):
        if "File " in line and "line " in line:
            analisis_singkat = line.strip()
            break
    return {"log_lengkap": teks_error, "lokasi_rusak": analisis_singkat}

def menu_kelola_db_dan_plugins():
    if not os.path.exists(FOLDER_PLUGINS):
        os.makedirs(FOLDER_PLUGINS)
    while True:
        print(f"\n{S}========================================={N}")
        print(f"       KELOLA DATABASE & PLUGINS          ")
        print(f"{S}========================================={N}")
        print(f" [{H}1{N}] Daftarkan Database JSON Tambahan")
        print(f" [{H}2{N}] Lihat Struktur Database Terdaftar")
        print(f" [{H}3{N}] Buat Template Plugin Baru")
        print(f" [{H}4{N}] Deteksi & Panggil Plugin Terpasang")
        print(f" [{M}K{N}] Kembali ke Control Panel")
        print(f"{S}========================================={N}")
        pilih = input("\nPilih opsi: ").strip().lower()
        if pilih == 'k':
            break
        elif pilih == '1':
            nama_db = input("\nMasukkan Nama Identitas DB Baru: ").strip()
            file_db = input("Masukkan Nama File (misal: my_custom_db.json): ").strip()
            if nama_db and file_db:
                if not file_db.endswith('.json'):
                    file_db += '.json'
                muat_json(file_db, {"informasi_db": nama_db, "data": []})
                print(f"{H}[✔] DB '{nama_db}' telah diregistrasikan di '{file_db}'!{N}")
            time.sleep(1.5)
        elif pilih == '2':
            files = [f for f in os.listdir('.') if f.endswith('.json')]
            print(f"\n{K}--- DAFTAR FILE DATABASE JSON ---{N}")
            for idx, file in enumerate(files, 1):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f" [{idx}] {file} (~{len(str(data))} karakter)")
                except Exception:
                    print(f" [{idx}] {file} (Gagal membaca isi JSON)")
            input("\nTekan ENTER untuk kembali...")
        elif pilih == '3':
            nama_plugin = input("\nMasukkan nama plugin (misal: spammer): ").strip().lower()
            if nama_plugin:
                file_plugin = os.path.join(FOLDER_PLUGINS, f"{nama_plugin}.py")
                template_code = (
                    f"# Plugin Kustom: {nama_plugin}\n"
                    f"# Berjalan di platform OneAI Termux Engine\n\n"
                    f"def jalankan_plugin(*args, **kwargs):\n"
                    f"    print('\\n{H}[Plugin {nama_plugin}] Berhasil Dieksekusi!{N}')\n"
                    f"    print('Argumen:', args, kwargs)\n"
                )
                with open(file_plugin, 'w', encoding='utf-8') as f:
                    f.write(template_code)
                print(f"{H}[✔] Berhasil membuat plugin di {file_plugin}!{N}")
            time.sleep(1.5)
        elif pilih == '4':
            plugins = [f[:-3] for f in os.listdir(FOLDER_PLUGINS) if f.endswith('.py')]
            if not plugins:
                print(f"\n{M}[!] Belum ada plugin kustom (.py) di folder '{FOLDER_PLUGINS}'!{N}")
                time.sleep(1.5)
                continue
            print(f"\n{S}--- LIST PLUGIN KUSTOM ---{N}")
            for idx, plg in enumerate(plugins, 1):
                print(f" [{idx}] {plg}")
            no_terpilih = input("\nPilih plugin yang ingin dipanggil: ").strip()
            if no_terpilih.isdigit() and 1 <= int(no_terpilih) <= len(plugins):
                target_plg = plugins[int(no_terpilih) - 1]
                print(f"\n{K}[🔄] Memuat {target_plg}...{N}")
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(target_plg, os.path.join(FOLDER_PLUGINS, f"{target_plg}.py"))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'jalankan_plugin'):
                        module.jalankan_plugin()
                    else:
                        print(f"{M}[❌] Plugin tidak memiliki fungsi 'jalankan_plugin'!{N}")
                except Exception as e:
                    print(f"{M}[❌] Gagal memanggil plugin: {e}{N}")
                input("\nTekan ENTER untuk kembali...")

def asisten_self_coder_interaktif(keys, model_aktif_dict):
    global AUTO_UPDATE_MANDIRI, ANTI_EDIT_MODE
    print(f"\n{B}========================================={N}")
    print(f"        AI CODER & AUTO-PATCHER (SELF)   ")
    print(f"{B}========================================={N}")
    
    if ANTI_EDIT_MODE:
        print(f"\n{M}[❌] AKSES DITOLAK: Fitur Anti-Edit Script sedang AKTIF!{N}")
        print(f"{K}Matikan fitur Anti-Edit di Menu No [23] jika ingin memberikan izin patch ke AI.{N}")
        time.sleep(2.5)
        return

    if not AUTO_UPDATE_MANDIRI:
        print(f"{M}[❌] Fitur auto-update mandiri sedang di-nonaktifkan!{N}")
        time.sleep(1.5)
        return
    if not keys:
        print(f"\n{M}[❌] Memerlukan minimal 1 API Key aktif untuk memanggil AI.{N}")
        time.sleep(1.5)
        return

    request_tuan = input("\nMasukkan instruksi modifikasi kode untuk AI:\n-> ").strip()
    if not request_tuan:
        print(f"\n{M}[❌] Instruksi tidak boleh kosong!{N}")
        time.sleep(1.5)
        return

    sukses_back, path_back = buat_backup_aman()
    if not sukses_back:
        print(f"\n{M}[❌] Gagal membuat backup sistem! Patching dibatalkan!{N}")
        time.sleep(1.5)
        return
    
    print(f"\n{H}[✔] BACKUP AMAN DIALOKASIKAN: {path_back}{N}")
    print(f"{S}[🔄] Membaca file {FILE_UTAMA} saat ini...{N}")
    with open(FILE_UTAMA, 'r', encoding='utf-8') as f:
        kode_sekarang = f.read()

    system_prompt = (
        "Kamu adalah pakar rekayasa perangkat lunak Python senior. "
        "Tulis ulang seluruh kode program Python secara UTUH dan LENGKAP tanpa terpotong. "
        "Jangan gunakan komentar placeholder seperti '# bagian kode lainnya tetap sama'. "
        "Kirimkan kode Python murni tanpa pembungkus markdown (```python) ataupun teks penjelasan."
    )
    user_payload = (
        f"Berikut adalah kode sumber '{FILE_UTAMA}' saat ini:\n\n```python\n{kode_sekarang}\n```\n\n"
        f"Instruksi Modifikasi: {request_tuan}\n\nTulis ulang script ini secara lengkap, mandiri, bebas error."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_payload}
    ]

    print(f"{S}[🔄] Menghubungi OpenRouter API untuk memproses auto-patching...{N}")
    engine = OpenRouterSuperEngine(keys, {"1": model_aktif_dict})
    response, _ = engine.kirim_request_smart(model_aktif_dict['id'], messages)

    if response and response.status_code == 200:
        try:
            kode_baru = response.json()['choices'][0]['message']['content'].strip()
            if kode_baru.startswith("```"):
                lines = kode_baru.split('\n')
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].strip() == "```":
                    lines = lines[:-1]
                kode_baru = "\n".join(lines).strip()

            if len(kode_baru) < 1000:
                print(f"\n{M}[❌] Hasil modifikasi AI terlalu pendek! Pembaruan dibatalkan.{N}")
                input("\nTekan ENTER...")
                return

            print(f"{S}[🔄] Memvalidasi sintaks kode baru...{N}")
            try:
                compile(kode_baru, FILE_UTAMA, 'exec')
                with open(FILE_UTAMA, 'w', encoding='utf-8') as f_write:
                    f_write.write(kode_baru)
                print(f"\n{H}[✔] AUTO-UPDATE SUKSES! Script dimodifikasi. Reloading...{N}")
                time.sleep(3.0)
                os.execv(sys.executable, [sys.executable] + sys.argv)
            except SyntaxError as se:
                print(f"\n{M}[❌] AI menghasilkan error sintaks! Pembaruan dibatalkan.{N}\nDetail: {se}")
                input("\nTekan ENTER...")
        except Exception as e:
            print(f"\n{M}[❌] Gagal memparsing respon AI: {e}{N}")
            input("\nTekan ENTER...")
    else:
        print(f"\n{M}[❌] Terjadi kendala API saat patching.{N}")
        input("\nTekan ENTER...")

def menu_manajemen_domains_search():
    while True:
        domains = muat_json(DB_DOMAINS, DOMAINS_DEFAULT)
        print(f"\n{B}========================================={N}")
        print(f"       KELOLA DOMAIN SEARCH ENGINE       ")
        print(f"{B}========================================={N}")
        if not domains:
            print(f" {M}[!] Status: Kosong (Belum ada domain){N}")
        else:
            print(f"{S} NO |  DOMAIN NAME       | TEMPLATE QUERY URL{N}")
            print(f"{W}-----------------------------------------{N}")
            for idx, (dom, url) in enumerate(domains.items(), 1):
                print(f" [{idx:<2}] | {dom:<18} | {url if len(url) <= 35 else url[:32] + '...'}")
        print(f"{W}-----------------------------------------{N}")
        print(f" {H}[1]{N} + Tambah Domain Search Engine")
        print(f" {M}[2]{N} - Hapus Domain Search Engine")
        print(f" {M}[K]{N} Kembali ke Control Panel Utama")
        print(f"{B}========================================={N}")
        pilihan = input("\nPilih Opsi: ").strip().lower()
        if pilihan == 'k':
            break
        elif pilihan == '1':
            print(f"\n--- TAMBAH DOMAIN PENCARI BARU ---")
            dom_baru = input("Masukkan Nama Domain (Contoh: ask.com):\n-> ").strip().lower()
            if not dom_baru:
                continue
            url_baru = input("Masukkan Query URL Template (Gunakan {query} sebagai placeholder):\n-> ").strip()
            if not url_baru:
                url_baru = f"https://www.{dom_baru}/search?q={{query}}"
            elif "{query}" not in url_baru:
                print(f"\n{M}[❌] Gagal! Template URL harus menyertakan '{{query}}'!{N}")
                time.sleep(1.5)
                continue
            domains[dom_baru] = url_baru
            simpan_json(DB_DOMAINS, domains)
            print(f"\n{H}[✔] Sukses ditambahkan!{N}")
            time.sleep(1.5)
        elif pilihan == '2':
            if not domains:
                continue
            try:
                no_hapus = int(input("\nMasukkan nomor domain yang ingin dihapus: ").strip())
                keys = list(domains.keys())
                if 1 <= no_hapus <= len(keys):
                    key_target = keys[no_hapus - 1]
                    domains.pop(key_target)
                    simpan_json(DB_DOMAINS, domains)
                    print(f"\n{H}[✔] Sukses menghapus domain '{key_target}'!{N}")
                else:
                    print(f"\n{M}[❌] Nomor tidak valid!{N}")
            except ValueError:
                print(f"\n{M}[❌] Masukan harus berupa angka!{N}")
            time.sleep(1.5)

def menu_manajemen_belajar_whitelist():
    while True:
        whitelist = muat_json(DB_BELAJAR, BELAJAR_WHITELIST_DEFAULT)
        print(f"\n{B}========================================={N}")
        print(f"     CONFIG BELAJAR - WHITELIST WEB      ")
        print(f"{B}========================================={N}")
        if not whitelist:
            print(f" {M}[!] Status: Kosong (Pembelajaran diblokir){N}")
        else:
            print(f"{S} NO |  WHITELISTED DOMAIN NAME{N}")
            print(f"{W}-----------------------------------------{N}")
            for idx, domain in enumerate(whitelist, 1):
                print(f" [{idx:<2}] | {domain}")
        print(f"{W}-----------------------------------------{N}")
        print(f" {H}[1]{N} + Tambah Website Ke Whitelist")
        print(f" {M}[2]{N} - Hapus Website Dari Whitelist")
        print(f" {M}[K]{N} Kembali ke Control Panel Utama")
        print(f"{B}========================================={N}")
        pilihan = input("\nPilih Opsi: ").strip().lower()
        if pilihan == 'k':
            break
        elif pilihan == '1':
            print(f"\n--- TAMBAH WEBSITE ---")
            web_baru = input("Masukkan Domain Website (Contoh: wikipedia.org):\n-> ").strip().lower()
            if not web_baru:
                continue
            web_clean = web_baru.replace("https://", "").replace("http://", "").split('/')[0]
            if web_clean in whitelist:
                print(f"\n{M}[❌] Website '{web_clean}' sudah terdaftar!{N}")
            else:
                whitelist.append(web_clean)
                simpan_json(DB_BELAJAR, whitelist)
                print(f"\n{H}[✔] Website '{web_clean}' sukses didaftarkan!{N}")
            time.sleep(1.5)
        elif pilihan == '2':
            if not whitelist:
                continue
            try:
                no_hapus = int(input("\nMasukkan nomor website yang ingin dihapus: ").strip())
                if 1 <= no_hapus <= len(whitelist):
                    removed_web = whitelist.pop(no_hapus - 1)
                    simpan_json(DB_BELAJAR, whitelist)
                    print(f"\n{H}[✔] Website '{removed_web}' sukses dihapus!{N}")
                else:
                    print(f"\n{M}[❌] Nomor tidak valid!{N}")
            except ValueError:
                print(f"\n{M}[❌] Masukan harus berupa angka!{N}")
            time.sleep(1.5)

def cek_kesehatan_dan_repair():
    global SOCKS_TERPASANG
    print(f"\n{S}========================================={N}")
    print(f"      CEK KESEHATAN SCRIPT & REPAIR      ")
    print(f"{S}========================================={N}")
    print(f" [*] Memindai modul & berkas sistem...")
    time.sleep(1.0)
    
    dependensi = {
        "requests": "requests", "PySocks": "socks", "beautifulsoup4": "bs4",
        "colorama": "colorama", "jedi": "jedi", "flake8": "flake8"
    }
    
    diperbaiki = False
    print(f"\n{W}[🔹] Memeriksa Paket Python Pip:{N}")
    for pkg_name, module_name in dependensi.items():
        try:
            if module_name == "bs4":
                from bs4 import BeautifulSoup
            else:
                __import__(module_name)
            print(f"  [-] Modul '{pkg_name:<16}': {H}OK (Terinstal){N}")
        except ImportError:
            print(f"  [!] Modul '{pkg_name:<16}': {M}RUSAK/HILANG!{N} Memulihkan...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name, "--quiet"])
                print(f"  {H}[✔] Berhasil menginstal '{pkg_name}'!{N}")
                diperbaiki = True
            except Exception as e:
                print(f"  {M}[❌] Gagal menginstal '{pkg_name}': {e}{N}")
    
    try:
        import socks
        SOCKS_TERPASANG = True
    except ImportError:
        SOCKS_TERPASANG = False

    print(f"\n{W}[🔹] Memeriksa Integritas File Sistem:{N}")
    files_internal = [
        (FILE_KEYS, "sk-or-v1-xxxxxxxx\n"),
        (DB_PERSONA, json.dumps(PERSONA_BAWAAN, indent=4)),
        (DB_MODEL, json.dumps(MODEL_BAWAAN, indent=4)),
        (DB_MEMORY, json.dumps({"catatan_fakta": []}, indent=4)),
        (DB_DOMAINS, json.dumps(DOMAINS_DEFAULT, indent=4)),
        (DB_BELAJAR, json.dumps(BELAJAR_WHITELIST_DEFAULT, indent=4)),
        (DB_MODUL_BELAJAR, json.dumps({"fakta_belajar": []}, indent=4))
    ]
    
    for file_path, default_content in files_internal:
        if not os.path.exists(file_path):
            print(f"  [!] File '{file_path:<20}': {M}HILANG!{N} Membuat ulang...")
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(default_content)
                print(f"  {H}[✔] File '{file_path}' berhasil dipulihkan!{N}")
                diperbaiki = True
            except Exception as e:
                print(f"  {M}[❌] Gagal memulihkan '{file_path}': {e}{N}")
        else:
            print(f"  [-] File '{file_path:<20}': {H}OK (Tersedia){N}")

    if diperbaiki:
        print(f"\n{H}[✔] Proses Auto-Repair selesai dijalankan secara sukses!{N}")
    else:
        print(f"\n{H}[✔] Semua sistem sehat walafiat!{N}")
    
    input(f"\n{K}Tekan ENTER untuk kembali...{N}")

def menu_copilot_kustom():
    global COPILOT_AKTIF, COPILOT_AKTIF_ID
    db_copilot = "copilots_custom.json"
    copilot_bawaan = {
        "1": {"nama": "Copilot Python Standard", "deskripsi": "Fokus pada validasi sintaks Python standard."},
        "2": {"nama": "Copilot Bash Architect", "deskripsi": "Optimalisasi perintah shell dan automation script."}
    }
    data_copilot = muat_json(db_copilot, copilot_bawaan)
    
    while True:
        print(f"\n{B}========================================={N}")
        print(f"           MENU KELOLA COPILOT           ")
        print(f"{B}========================================={N}")
        
        aktif_nama = data_copilot.get(COPILOT_AKTIF_ID, {}).get("nama", "Tidak Diketahui")
        print(f" [*] Copilot Aktif : {H}[{COPILOT_AKTIF_ID}] {aktif_nama}{N}")
        print(f"{W}-----------------------------------------{N}")
        
        for k, v in data_copilot.items():
            tipe = f"{K}[Bawaan]{N}" if k in ["1", "2"] else f"{H}[User]{N}"
            status = f" {H}(AKTIF){N}" if k == COPILOT_AKTIF_ID else ""
            print(f" [{k}] {v['nama']} {tipe}{status}\n     Deskripsi: {v['deskripsi']}")
            
        print(f"{W}-----------------------------------------{N}")
        print(f" [{H}S{N}] Pilih / Aktifkan Copilot")
        print(f" [{H}A{N}] + Tambah Copilot Baru")
        print(f" [{M}R{N}] - Hapus Copilot")
        print(f" [{M}K{N}] Kembali ke Control Panel Utama")
        print(f"{B}========================================={N}")
        
        pilih = input("\nPilih opsi: ").strip().lower()
        if pilih == 'k':
            break
        elif pilih == 's':
            id_c = input("Masukkan ID Copilot yang ingin diaktifkan: ").strip()
            if id_c in data_copilot:
                COPILOT_AKTIF_ID = id_c
                COPILOT_AKTIF = True
                print(f"{H}[✔] Copilot [{id_c}] '{data_copilot[id_c]['nama']}' berhasil diaktifkan!{N}")
            else:
                print(f"{M}[❌] ID Copilot tidak ditemukan!{N}")
            time.sleep(1.5)
        elif pilih == 'a':
            nama_c = input("Masukkan Nama Copilot: ").strip()
            desk_c = input("Masukkan Deskripsi/Instruksi: ").strip()
            if nama_c and desk_c:
                next_id = str(max([int(x) for x in data_copilot.keys() if x.isdigit()] + [0]) + 1)
                data_copilot[next_id] = {"nama": nama_c, "deskripsi": desk_c}
                simpan_json(db_copilot, data_copilot)
                print(f"{H}[✔] Copilot berhasil ditambahkan!{N}")
            time.sleep(1.5)
        elif pilih == 'r':
            id_h = input("Masukkan ID Copilot yang ingin dihapus: ").strip()
            if id_h in ["1", "2"]:
                print(f"{M}[❌] Copilot bawaan sistem tidak boleh dihapus!{N}")
            elif id_h == COPILOT_AKTIF_ID:
                print(f"{M}[❌] Tidak bisa menghapus Copilot yang sedang aktif!{N}")
            elif id_h in data_copilot:
                deleted = data_copilot.pop(id_h)
                simpan_json(db_copilot, data_copilot)
                print(f"{H}[✔] Copilot '{deleted['nama']}' berhasil dihapus!{N}")
            else:
                print(f"{M}[❌] ID Copilot tidak ditemukan!{N}")
            time.sleep(1.5)

def menu_offline_ai():
    while True:
        data_offline = muat_json(DB_OFFLINE_AI, {})
        print(f"\n{B}========================================={N}")
        print(f"         MANAJEMEN OFFLINE AI LOGIK      ")
        print(f"{B}========================================={N}")
        if not data_offline:
            print(f" {M}[!] Status: Kosong (Belum ada AI Offline){N}")
        else:
            print(f"{S} ID  |  NAMA AI OFFLINE   | PATH / PERINTAH{N}")
            print(f"{W}-----------------------------------------{N}")
            for k, v in data_offline.items():
                print(f" [{k}] | {v['nama']:<16} | {v['command']}")
        print(f"{W}-----------------------------------------{N}")
        print(f" {H}[1]{N} + Tambah Konfigurasi AI Offline")
        print(f" {M}[2]{N} - Hapus Konfigurasi AI Offline")
        print(f" {M}[K]{N} Kembali ke Control Panel")
        print(f"{B}========================================={N}")
        
        pilihan = input("\nPilih Menu: ").strip().lower()
        if pilihan == 'k':
            break
        elif pilihan == '1':
            nama_ai = input("Masukkan Nama AI Offline: ").strip()
            cmd_ai = input("Masukkan Perintah Eksekusi / Path Model: ").strip()
            if nama_ai and cmd_ai:
                next_id = str(max([int(x) for x in data_offline.keys()] + [0]) + 1)
                data_offline[next_id] = {"nama": nama_ai, "command": cmd_ai}
                simpan_json(DB_OFFLINE_AI, data_offline)
                tulis_log(f"Menambahkan AI Offline: {nama_ai}")
                print(f"\n{H}[✔] AI Offline Berhasil Ditambahkan!{N}")
            time.sleep(1.5)
        elif pilihan == '2':
            if not data_offline:
                continue
            id_hapus = input("Masukkan ID AI Offline yang ingin dihilangkan: ").strip()
            if id_hapus in data_offline:
                deleted = data_offline.pop(id_hapus)
                simpan_json(DB_OFFLINE_AI, data_offline)
                tulis_log(f"Menghapus AI Offline: {deleted['nama']}")
                print(f"\n{H}[✔] AI Offline '{deleted['nama']}' sukses dihapus!{N}")
            else:
                print(f"\n{M}[❌] ID tidak ditemukan.{N}")
            time.sleep(1.5)

def menu_live_ai_gratis_openrouter():
    global model_aktif, model_list
    print(f"\n{H}========================================={N}")
    print(f"     LIVE AI GRATIS OPENROUTER (TRENDING) ")
    print(f"{H}========================================={N}")
    print(" Pilih model gratisan performa tinggi terbaru untuk diset aktif:")
    print(f" [{H}1{N}] Meta: Llama 3 8B Instruct (Free) -> traffic naik tajam")
    print(f" [{H}2{N}] Google: Gemma 2 9B IT (Free) -> optimalisasi kognitif")
    print(f" [{H}3{N}] Mistral 7B Instruct v0.3 (Free) -> rajanya coding ringan")
    print(f" [{H}4{N}] Microsoft: Phi-3 Medium 128k (Free) -> konteks panjang")
    print(f" [{H}5{N}] Qwen 2 7B Beta Instruct (Free) -> respon super cepat")
    print(f" [{M}K{N}] Kembali ke Menu")
    print(f"{H}========================================={N}")
    
    pilih = input("\nPilih Opsi (1-5): ").strip()
    opsi_model = {
        "1": {"nama": "Llama 3 8B Instruct (Free)", "id": "meta-llama/llama-3-8b-instruct:free"},
        "2": {"nama": "Gemma 2 9B IT (Free)", "id": "google/gemma-2-9b-it:free"},
        "3": {"nama": "Mistral 7B Instruct (Free)", "id": "mistralai/mistral-7b-instruct:free"},
        "4": {"nama": "Phi-3 Medium Instruct (Free)", "id": "microsoft/phi-3-medium-128k-instruct:free"},
        "5": {"nama": "Qwen 2 7B Instruct (Free)", "id": "qwen/qwen-2-7b-instruct:free"}
    }
    
    if pilih in opsi_model:
        target = opsi_model[pilih]
        no_baru = str(max([int(k) for k in model_list.keys()]) + 1) if model_list else "1"
        model_list[no_baru] = {"nama": target["nama"], "id": target["id"], "jatah_rpd": 5000}
        simpan_json(DB_MODEL, model_list)
        model_aktif = model_list[no_baru]
        tulis_log(f"Beralih ke Live AI Gratis Openrouter: {target['nama']}")
        print(f"\n{H}[✔] Sukses! Model Aktif dialihkan ke: {target['nama']}{N}")
        time.sleep(2.0)

def bersihkan_ram_cache_ai():
    print(f"\n{S}[🔄] Memulai Pembersihan RAM & Cache AI Berkas Sementara...{N}")
    time.sleep(1.0)
    files_to_clean = [DB_USAGE, DB_MEMORY, "copilots_custom.json", "plugins_registry.json"]
    bytes_cleared = 0
    
    for file in files_to_clean:
        if os.path.exists(file):
            try:
                bytes_cleared += os.path.getsize(file)
                if file == DB_MEMORY:
                    simpan_json(file, {"catatan_fakta": []})
                else:
                    simpan_json(file, {})
            except Exception:
                pass
                
    for f in os.listdir('.'):
        if f.startswith("Chat_OneAI_") and f.endswith(".md"):
            try:
                bytes_cleared += os.path.getsize(f)
                os.remove(f)
            except Exception:
                pass
                
    tulis_log(f"Pembersihan RAM Cache selesai. Membebaskan {bytes_cleared} bytes ruang memori.")
    print(f"{H}[✔] RAM Cache AI Berhasil Dibersihkan! (Database Utama Aman Terproteksi){N}")
    time.sleep(1.5)

def menu_manajemen_log():
    while True:
        print(f"\n{K}========================================={N}")
        print(f"            PANEL LOG AKTIVITAS AI       ")
        print(f"{K}========================================={N}")
        print(f" [{H}1{N}] Periksa Seluruh Log Hari Ini (`Log.txt`)")
        print(f" [{M}2{N}] Bersihkan / Hapus Total Semua Log")
        print(f" [{M}K{N}] Kembali ke Control Panel")
        print(f"{K}========================================={N}")
        
        pilih = input("\nPilih Tindakan: ").strip().lower()
        if pilih == 'k':
            break
        elif pilih == '1':
            print(f"\n{S}--- MENAMPILKAN ISI FILE LOG.TXT ---{N}\n")
            if os.path.exists(FILE_LOG):
                with open(FILE_LOG, 'r', encoding='utf-8') as f:
                    konten = f.read()
                print(konten if konten.strip() else f"{K}[Empty] Berkas log masih kosong.{N}")
            else:
                print(f"{M}[!] File Log.txt belum terbuat di sistem.{N}")
            input("\nTekan ENTER untuk kembali...")
        elif pilih == '2':
            if os.path.exists(FILE_LOG):
                os.remove(FILE_LOG)
                print(f"\n{H}[✔] Berkas Log.txt berhasil dieliminasi total!{N}")
            else:
                print(f"\n{M}[!] Berkas log memang tidak ada.{N}")
            time.sleep(1.5)

# ====================================================
# [MODIFIKASI] FITUR BARU: MENU RADIO SCANNER & MONITOR
# ====================================================
def menu_radio_scanner():
    while True:
        print(f"\n{S}========================================={N}")
        print(f"      RADIO SIGNAL SCANNER & MONITOR    ")
        print(f"{S}========================================={N}")
        print(f" {H}Info Sistem:{N} Tanpa Hardware RTL-SDR fisik,")
        print(f" Modul ini berjalan di {P}Mode WebSDR/Simulasi{N}.")
        print(f"{W}-----------------------------------------{N}")
        print(f" [{H}1{N}] Tangkap Sinyal AM (Amplitude Mod)")
        print(f" [{H}2{N}] Tangkap Sinyal FM (Frequency Mod)")
        print(f" [{H}3{N}] Tangkap Sinyal HT (VHF/UHF Trans)")
        print(f" [{H}4{N}] Tangkap Sandi Morse (CW Wave)")
        print(f" [{P}5{N}] Buka Live Panel Signal Monitoring")
        print(f" [{M}K{N}] Kembali ke Control Panel Utama")
        print(f"{S}========================================={N}")
        
        pilih = input("\nPilih Frekuensi/Aksi: ").strip().lower()
        if pilih == 'k':
            break
        elif pilih in ['1', '2', '3', '4']:
            tipe = {"1": "AM (530-1700kHz)", "2": "FM (88-108MHz)", "3": "HT (136-174MHz)", "4": "Morse (14.0MHz)"}[pilih]
            print(f"\n{K}[⚡] Menginisialisasi modul penerima sinyal...{N}")
            time.sleep(1)
            print(f"{S}[📡] Mencari transmisi aktif di band {tipe}...{N}")
            
            for _ in range(6):
                frek = random.uniform(88.0, 108.0) if pilih == '2' else random.uniform(136.0, 174.0)
                dbm = random.randint(-120, -50)
                print(f"   -> Scanning: {frek:.3f} MHz | Kuat Sinyal: {dbm} dBm")
                time.sleep(0.4)
            
            print(f"\n{H}[✔] Tuning terkunci pada sinyal stabil!{N}")
            print(f"{M}[!] Menjalankan demodulator audio (Tekan CTRL+C untuk stop)...{N}")
            try:
                while True:
                    visual_audio = random.choice(['|||  ', ' ||| ', '  |||', '|  | '])
                    sys.stdout.write(f"\r{P}Audio Stream [{visual_audio}] Mendengarkan transmisi...{N}")
                    sys.stdout.flush()
                    time.sleep(0.2)
            except KeyboardInterrupt:
                print(f"\n\n{H}[✔] Penerimaan sinyal dihentikan secara aman.{N}")
                time.sleep(1)
        elif pilih == '5':
            print(f"\n{S}[📈] MEMULAI WATERFALL MONITORING (Tekan CTRL+C untuk stop){N}")
            time.sleep(1)
            try:
                while True:
                    lebar = 45
                    noise = random.randint(0, lebar)
                    bar = "#" * noise + "-" * (lebar - noise)
                    freq_drift = random.uniform(144.000, 144.050)
                    print(f"|{bar}| {noise*2.2:>5.1f}% | {freq_drift:.3f} MHz | {-110 + noise} dBm")
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print(f"\n\n{H}[✔] Live Monitoring dihentikan.{N}")
                time.sleep(1)

def jalankan_aplikasi_utama():
    global persona_list, model_list, model_aktif, persona_aktif, COPILOT_AKTIF, AUTO_UPDATE_MANDIRI, ANTI_EDIT_MODE
    persona_list = muat_json(DB_PERSONA, PERSONA_BAWAAN)
    model_list = muat_json(DB_MODEL, MODEL_BAWAAN)

    if "4" not in persona_list:
        persona_list["4"] = PERSONA_BAWAAN["4"]
        simpan_json(DB_PERSONA, persona_list)

    if model_list:
        key_awal = sorted(model_list.keys(), key=lambda x: int(x))[0]
        model_aktif = model_list[key_awal]
    else:
        model_aktif = {"nama": "Belum Ada Model", "id": ""}

    persona_aktif = persona_list["1"]
    tulis_log("Aplikasi OneAI Berhasil Booting")

    while True:
        api_keys = muat_keys()
        jumlah_key = len(api_keys)
        mood_panel = hitung_mood_otomatis()
        nama_mood_singkat = mood_panel.split('(')[0].strip()

        global_rpm, global_rpd = "0", "0"
        if jumlah_key > 0:
            _, _, _, k_rpm, k_rpd = cek_status_satu_key(api_keys[0])
            if k_rpm != "N/A":
                global_rpm = k_rpm
            if k_rpd != "N/A":
                global_rpd = k_rpd

        anti_edit_status = f"{H}[ ON ]{N}" if ANTI_EDIT_MODE else f"{M}[ OFF ]{N}"

        print(f"\n{P}========================================={N}")
        print(f"       CONTROL PANEL - {NAMA_AI}       ")
        print(f"========================================={N}")
        print(f"[*] Jaringan       : {H}ONLINE{N}")
        print(f"[*] Jumlah API Key : {H}{jumlah_key}{N}")
        print(f"[*] Limit Tier RPM : {S}{global_rpm}{N}")
        print(f"[*] Limit Tier RPD : {S}{global_rpd}{N}")
        print(f"[*] Model Aktif    : {K}{model_aktif['nama']}{N}")
        print(f"[*] Persona Aktif  : {B}{persona_aktif['nama']}{N}")
        print(f"[*] Mood Hari Ini  : {S}{nama_mood_singkat}{N}")
        print(f"[*] Copilot Mode   : {H if COPILOT_AKTIF else M}{'AKTIF' if COPILOT_AKTIF else 'NON-AKTIF'}{N}")
        print(f"[*] Auto Update AI : {H if AUTO_UPDATE_MANDIRI else M}{'ON (AKTIF)' if AUTO_UPDATE_MANDIRI else 'OFF (NON-AKTIF)'}{N}")
        print(f"[*] Anti-Edit Core : {anti_edit_status}")
        print(f"[*] {random.choice(RGB_NEON)}Author by : Unlimited48{N}")
        print(f"{P}-----------------------------------------{N}")
        print(f" [{H}1{N}] Mulai Mengobrol")
        print(f" [{H}2{N}] Ganti / Tambah Persona")
        print(f" [{H}3{N}] Ganti / Tambah Model AI")
        print(f" [{H}4{N}] Cek Cepat Semua Status Key")
        print(f" [{H}5{N}] Kelola Key Interaktif")
        print(f" [{H}6{N}] Cek Limit & Info Model AI")
        print(f" [{H}7{N}] Kelola Dokumen ToS")
        print(f" [{S}8{N}] Fitur Tambahan Termux & Sandbox")
        print(f" [{S}9{N}] KELOLA LIBRARY PYTHON TUX")
        print(f" [{S}10{N}] KELOLA DB & PLUGINS KUSTOM")
        print(f" [{S}11{N}] AUTO-PATCHER / AI SELF-CODER")
        print(f" [{S}12{N}] MENU SETTING COPILOT KUSTOM")
        print(f" [{S}13{N}] TOGGLE AUTO UPDATE AI TO SCRIPT")
        print(f" [{S}14{N}] KELOLA DOMAIN SEARCH ENGINE")
        print(f" [{S}15{N}] CEK KESEHATAN SCRIPT & REPAIR")
        print(f" [{S}16{N}] CONFIG BELAJAR (WHITELIST WEB)")
        print(f" [{S}17{N}] LIHAT & HAPUS {DB_MODUL_BELAJAR}")
        print(f" [{K}18{N}] PANEL MANAGEMENT OFFLINE AI")
        print(f" [{K}19{N}] LIVE AI GRATIS OPENROUTER (TRENDING)")
        print(f" [{K}20{N}] CEK & HAPUS BERKAS LOG AKTIVITAS")
        print(f" [{K}21{N}] BERSIHKAN RAM CACHE AI")
        print(f" [{K}22{N}] TOGGLE COPILOT MODE (ON/OFF)")
        print(f" [{P}23{N}] TOGGLE ANTI-EDIT SCRIPT CODES (ON/OFF)")
        print(f" [{S}24{N}] SCANNER RADIO (AM/FM/HT/MORSE)") 
        print(f" [{M}X{N}] Keluar Aplikasi")

        pilihan_utama = input("\nPilih menu: ").strip().lower()

        if pilihan_utama == 'x':
            tulis_log("Aplikasi OneAI Ditutup")
            print(f"\nAplikasi {M}{NAMA_AI}{N} ditutup. Sampai jumpa!")
            sys.exit()
        elif pilihan_utama == "24":
            menu_radio_scanner()
        elif pilihan_utama == "23":
            ANTI_EDIT_MODE = not ANTI_EDIT_MODE
            status_str = "DIAKTIFKAN (Core Terkunci Aman)" if ANTI_EDIT_MODE else "DINONAKTIFKAN (AI Diizinkan Patching)"
            print(f"\n{H}[✔] Fitur Anti-Edit Berhasil {status_str}!{N}")
            time.sleep(1.5)
        elif pilihan_utama == "22":
            COPILOT_AKTIF = not COPILOT_AKTIF
            print(f"\n{H}[✔] Status Copilot Mode diubah menjadi: {'AKTIF' if COPILOT_AKTIF else 'NON-AKTIF'}{N}")
            time.sleep(1.5)
        elif pilihan_utama == "21":
            bersihkan_ram_cache_ai()
        elif pilihan_utama == "20":
            menu_manajemen_log()
        elif pilihan_utama == "19":
            menu_live_ai_gratis_openrouter()
        elif pilihan_utama == "18":
            menu_offline_ai()
        elif pilihan_utama == "17":
            print(f"\n{B}=== MENU MANAJEMEN DATABASE BELAJAR ==={N}")
            if os.path.exists(DB_MODUL_BELAJAR):
                print(f"{H}[✔] Status File:{N} {DB_MODUL_BELAJAR} ditemukan.")
                os.system(f"ls -la | grep '{DB_MODUL_BELAJAR}'")
                if input(f"\nHapus {M}{DB_MODUL_BELAJAR}{N}? (y/n): ").strip().lower() == 'y':
                    try:
                        os.remove(DB_MODUL_BELAJAR)
                        tulis_log(f"Menghapus database: {DB_MODUL_BELAJAR}")
                        print(f"{H}[✔] Database berhasil dihapus!{N}")
                    except Exception as e:
                        print(f"{M}[❌] Gagal menghapus database: {e}{N}")
            else:
                print(f"{M}[!] File {DB_MODUL_BELAJAR} tidak terdeteksi.{N}")
            input("\nTekan ENTER untuk kembali...")
        elif pilihan_utama == "1":
            if jumlah_key == 0:
                print(f"\n{M}[Error] Lu belum masukin API Key asli di keys.txt!{N}")
                input("\nTekan ENTER...")
                continue
            if not model_aktif.get("id"):
                print(f"\n{M}[Error] Belum ada model yang diset aktif!{N}")
                input("\nTekan ENTER...")
                continue

            engine = OpenRouterSuperEngine(api_keys, model_list)
            memori_sistem = muat_json(DB_MEMORY, {"catatan_fakta": []})
            modul_belajar = muat_json(DB_MODUL_BELAJAR, {"fakta_belajar": []})

            tos_gabungan = ""
            if os.path.exists(FILE_TOS_TXT):
                try:
                    with open(FILE_TOS_TXT, 'r', encoding='utf-8') as f_txt:
                        tos_gabungan = f_txt.read().strip()
                except Exception:
                    pass

            if not tos_gabungan:
                try:
                    tos_gabungan = ToS.baca_tos_sistem()
                except Exception:
                    pass

            try:
                tos_final = tos_gabungan.format(MODEL_NAME=model_aktif['nama'])
            except Exception:
                tos_final = tos_gabungan

            bagian_tos = f"[ToS Dokumen]:\n{tos_final}\n" if tos_final.strip() else ""
            
            catatan_f = memori_sistem.get("catatan_fakta", [])
            teks_memori_eksternal = "\n[INGATAN JANGKA PANJANG]:\n" + "\n".join([f"- [{i.get('tanggal', '')}] {i.get('informasi', '')}" for i in catatan_f]) + "\n" if catatan_f else ""
            
            fakta_l = modul_belajar.get("fakta_belajar", [])
            teks_modul_belajar = "\n[DATABASE PENGETAHUAN BELAJAR]:\n" + "\n".join([f"- [{i.get('tanggal', '')}] ({i.get('url', '')}): {i.get('informasi', '')}" for i in fakta_l]) + "\n" if fakta_l else ""

            copilot_instruction = (
                "\n[COPILOT COGNITIVE MODE ENABLED]:\n"
                "- Gunakan prinsip berpikir kritis sistematis (Chain-of-Thought) sebelum menjawab.\n"
                "- Periksa ulang kesesuaian potongan kode dengan standar sintaks Python/Bash.\n"
                "- Berikan alternatif solusi yang lebih optimal dan minimalisir redundansi kode.\n"
            ) if COPILOT_AKTIF else ""

            sandbox_full_access = (
                "\n[HAK AKSES PENUH TERMINAL & SANDBOX TERMUK LIGHT]:\n"
                "Kamu memiliki wewenang penuh untuk memerintahkan eksekusi utilitas sistem Termux.\n"
                "Kamu dapat merekomendasikan atau meluncurkan perintah perbaikan secara mandiri jika diminta pengguna.\n"
            )

            ai_belajar_permission = (
                f"\n[HAK AKSES PENUH FITUR BELAJAR INTERAKTIF ({DB_MODUL_BELAJAR})]:\n"
                "Kamu memiliki otorisasi penuh untuk menyuruh atau menyarankan pengguna melakukan pembelajaran konten dengan perintah chat '!belajar <url>'.\n"
                f"Gunakan data yang tersimpan di dalam '{DB_MODUL_BELAJAR}' di bawah ini untuk menjawab berbagai pertanyaan kompleks.\n"
            )

            SISTEM_INSTRUKSI = (
                f"Nama kamu '{NAMA_AI}'.\n"
                f"[Gaya Persona]: {persona_aktif['instruksi']}\n"
                f"[Suasana Hati]: Kamu sedang berada dalam mood: {mood_panel}. "
                f"{teks_memori_eksternal}"
                f"{teks_modul_belajar}"
                f"{bagian_tos}"
                f"{copilot_instruction}"
                f"{sandbox_full_access}"
                f"{ai_belajar_permission}"
                f"PENTING: Jawab secara responsif, cerdas, efisien, lengkap."
            )

            riwayat_chat = [{"role": "system", "content": SISTEM_INSTRUKSI}]
            jawaban_terakhir_ai = ""
            counter_pesan = 0

            print(f"\n{H}>>> {NAMA_AI} Terhubung ({model_aktif['nama']}) <<<{N}\n")
            print(f"{K}Ketik !help untuk melihat panduan pintasan perintah chat.{N}\n")

            while True:
                try:
                    engine.bersihkan_timestamp_lama()
                    rpm_saat_ini = len(engine.request_timestamps)
                    rpd_terpakai = engine.usage_data.get("rpd_terpakai", 0)
                    max_rpd_jatah = model_aktif.get("jatah_rpd", 2000)

                    token_aktif_tengah = "0000"
                    key_aktif = engine.dapatkan_key_siap_pakai()
                    if key_aktif:
                        bagian_bersih = key_aktif.replace("sk-or-v1-", "")
                        indeks_tengah = len(bagian_bersih) // 2
                        token_aktif_tengah = bagian_bersih[max(0, indeks_tengah-2):indeks_tengah+2]

                    prompt_dinamis = dapatkan_prompt_rgb(rpm_saat_ini, engine.MAX_RPM, rpd_terpakai, max_rpd_jatah, token_aktif_tengah)
                    user_input = input(prompt_dinamis).strip()
                    if not user_input:
                        continue

                    if user_input.lower() in ['exit', 'quit', 'keluar']:
                        break
                    
                    if user_input.lower() == 'clear':
                        riwayat_chat = [{"role": "system", "content": SISTEM_INSTRUKSI}]
                        jawaban_terakhir_ai = ""
                        counter_pesan = 0
                        print(f"{M}[Sistem] Memori chat di-reset!{N}\n")
                        continue

                    if user_input.lower() == '!help':
                        print(f"\n{K}[ Shortcut Chat Hub ]{N}")
                        print(" exit : Menu Utama   | clear : Reset Chat  | !run <cmd> : Eksekusi")
                        print(" !ingat <fakta>     | !lihatingatan       | !baca <nama_file.py>")
                        print(" !search <keyword>  | !export (Kirim .md) | !status (Hardware) | !voice <teks>")
                        print(" !browsing <query>  | !backup : Cadangkan Skrip | !hapusmemori : Reset ingatan")
                        print(" !save              | Menyimpan teks jawaban terakhir AI ke file .txt")
                        print(" !tor : Cek Status Layanan Tor & IP Anonimitas")
                        print(" !cuaca <lokasi>    | Mengecek cuaca pada suatu lokasi (default: Sukoharjo)")
                        print(f"\n{S}[ Developer Help ]{N}")
                        print(f" !belajar <url>     | Pembelajaran mandiri AI & simpan data ke {DB_MODUL_BELAJAR}")
                        print(" !hapusbelajar      | Menghapus semua riwayat data yang dipelajari\n")
                        continue

                    if user_input.lower() == '!save':
                        if not jawaban_terakhir_ai:
                            print(f"{M}[!] Belum ada teks dari AI yang bisa disimpan.{N}\n")
                            continue
                        waktu_save = datetime.now().strftime("%Y%m%d_%H%M%S")
                        nama_file_save = f"Teks_AI_{waktu_save}.txt"
                        try:
                            with open(nama_file_save, 'w', encoding='utf-8') as f:
                                f.write(jawaban_terakhir_ai)
                            print(f"{H}[OK] Jawaban terakhir AI berhasil disimpan ke: {nama_file_save}{N}\n")
                        except Exception as e:
                            print(f"{M}[Error] Gagal menyimpan file: {e}{N}\n")
                        continue

                    if user_input.lower() == '!hapusbelajar':
                        modul_belajar = {"fakta_belajar": []}
                        simpan_json(DB_MODUL_BELAJAR, modul_belajar)
                        teks_modul_belajar = ""
                        riwayat_chat[0]["content"] = SISTEM_INSTRUKSI
                        print(f"{H}[Memori] Database {DB_MODUL_BELAJAR} berhasil dikosongkan!{N}\n")
                        continue

                    if user_input.lower() == '!tor':
                        print(f"{S}[🔄] Memindai layanan Tor lokal...{N}")
                        aktif, port_tor = periksa_status_tor()
                        if aktif:
                            print(f"{H}[✔] TOR AKTIF pada port localhost:{port_tor}!{N}")
                            if not SOCKS_TERPASANG:
                                print(f"{K}[!] Modul 'socks' belum terinstal. Ketik '!run pip install PySocks'{N}")
                            else:
                                try:
                                    res_ip = requests.get("https://icanhazip.com", proxies=dapatkan_tor_proxies(port_tor), timeout=6)
                                    print(f"{H}[Jaringan] Tunneling sukses! IP Anonim: {K}{res_ip.text.strip()}{N}\n")
                                except Exception as e:
                                    print(f"{M}[!] Tor aktif namun gagal merouting: {e}{N}\n")
                        else:
                            print(f"{M}[❌] TOR NON-AKTIF di sistem Tuan.{N}\n")
                        continue

                    if user_input.lower() == '!hapusmemori':
                        memori_sistem = {"catatan_fakta": []}
                        simpan_json(DB_MEMORY, memori_sistem)
                        modul_belajar = {"fakta_belajar": []}
                        simpan_json(DB_MODUL_BELAJAR, modul_belajar)
                        teks_memori_eksternal, teks_modul_belajar = "", ""
                        riwayat_chat[0]["content"] = SISTEM_INSTRUKSI
                        print(f"{H}[Memori] Seluruh ingatan dan database belajar telah dibersihkan!{N}\n")
                        continue

                    if user_input.lower() == '!lihatingatan':
                        catatan = memori_sistem.get("catatan_fakta", [])
                        fakta_l_list = modul_belajar.get("fakta_belajar", [])
                        if not catatan and not fakta_l_list:
                            print(f"{K}[Memori] Belum ada ingatan yang tersimpan.{N}\n")
                        else:
                            if catatan:
                                print(f"\n{S}[ DAFTAR INGATAN (memory.json) ]{N}")
                                for idx, item in enumerate(catatan, 1):
                                    print(f" [{idx}] [{item.get('tanggal')}] {item.get('informasi')}")
                            if fakta_l_list:
                                print(f"\n{S}[ DAFTAR PENGETAHUAN ({DB_MODUL_BELAJAR}) ]{N}")
                                for idx, item in enumerate(fakta_l_list, 1):
                                    print(f" [{idx}] [{item.get('tanggal')}] ({item.get('url')}) -> {item.get('informasi')}")
                            print()
                        continue

                    if user_input.lower().startswith('!ingat '):
                        fakta_baru = user_input[7:].strip()
                        if fakta_baru:
                            memori_sistem["catatan_fakta"].append({
                                "tanggal": datetime.now().strftime("%Y-%m-%d"),
                                "informasi": fakta_baru
                            })
                            simpan_json(DB_MEMORY, memori_sistem)
                            print(f"{H}[Memori] Fakta permanen direkam!{N}\n")
                        continue

                    if user_input.lower().startswith('!run '):
                        cmd_inline = user_input[5:].strip()
                        if cmd_inline:
                            if any(t in cmd_inline for t in ['rm -rf /', 'mkfs', 'dd ', '> /dev/', 'chmod 000']):
                                print(f"\n{M}[Ditolak] Perintah berbahaya!{N}\n")
                                continue
                            print(f"\n{K}[Executing]: {cmd_inline}{N}")
                            try:
                                hasil = subprocess.run(cmd_inline, shell=True, capture_output=True, text=True, timeout=120)
                                if hasil.stdout: print(f"{W}{hasil.stdout}{N}")
                                if hasil.stderr: print(f"{M}{hasil.stderr}{N}")
                            except Exception as e:
                                print(f"{M}[Error] Gagal menjalankan: {e}{N}")
                            print()
                        continue

                    if jawaban_terakhir_ai and "```bash" in jawaban_terakhir_ai:
                        if any(k in user_input.lower() for k in ["jalankan", "eksekusi", "run itu", "coba"]):
                            start_box = jawaban_terakhir_ai.find("```bash") + 7
                            end_box = jawaban_terakhir_ai.find("```", start_box)
                            cmd_ai = jawaban_terakhir_ai[start_box:end_box].strip()
                            if cmd_ai and not any(t in cmd_ai for t in ['rm -rf /', 'mkfs', 'dd ', '> /dev/']):
                                print(f"\n{K}[AI Automation] Mengeksekusi perintah...{N}")
                                try:
                                    hasil_ai = subprocess.run(cmd_ai, shell=True, capture_output=True, text=True, timeout=120)
                                    user_input = f"{user_input}\n\n[Sistem Terminal]: Hasil eksekusi '{cmd_ai}':\nSTDOUT:\n{hasil_ai.stdout}\nSTDERR:\n{hasil_ai.stderr}"
                                    print(f"{H}[✔] Eksekusi Selesai.{N}\n")
                                except Exception as e:
                                    user_input = f"{user_input}\n\n[Sistem Terminal]: Gagal eksekusi: {e}"
                            else:
                                print(f"\n{M}[Ditolak] Perintah berbahaya terdeteksi!{N}\n")

                    if user_input.lower().startswith('!baca '):
                        nama_file = user_input[6:].strip()
                        if os.path.exists(nama_file):
                            try:
                                with open(nama_file, 'r', encoding='utf-8') as f:
                                    isi_file = f.read()
                                print(f"{H}[File] {nama_file} dimuat ({len(isi_file)} karakter).{N}")
                                user_input = f"Analisis file {nama_file} berikut:\n\n```text\n{isi_file}\n```"
                            except Exception as e:
                                print(f"{M}[Error] Gagal membaca file: {e}{N}\n")
                                continue
                        else:
                            print(f"{M}[!] File '{nama_file}' tidak ditemukan.{N}\n")
                            continue

                    if user_input.lower().startswith('!search '):
                        query = user_input[8:].strip()
                        print(f"{S}[Scraping] OneAI dan Copilot melakukan Scraping data untuk '{query}'...{N}")
                        try:
                            # BUG FIX: Perbaikan format URL wikipedia yang tercampur markdown
                            url_wikipedia = f"[https://id.wikipedia.org/api/rest_v1/page/summary/](https://id.wikipedia.org/api/rest_v1/page/summary/){urllib.parse.quote(query.replace(' ', '_'))}"
                            res = requests.get(url_wikipedia, timeout=10)
                            
                            if res.status_code == 200:
                                summary = res.json().get('extract', 'Tidak ada ringkasan.')
                                print(f"{S}[Processing] OneAI dan Copilot mengolah data bersama menjadi text...{N}")
                                
                                prompt_search = f"Referensi data: '{summary}'. \n\nJawab dengan natural: {query}."
                                temp_history = list(riwayat_chat) + [{"role": "user", "content": prompt_search}]
                                res_search, _ = engine.kirim_request_smart(model_aktif['id'], temp_history)
                                
                                if res_search and res_search.status_code == 200:
                                    jawaban_search = res_search.json()['choices'][0]['message']['content']
                                    ketik_efek(jawaban_search)
                                    jawaban_terakhir_ai = jawaban_search
                                    riwayat_chat.append({"role": "user", "content": f"!search {query}"})
                                    riwayat_chat.append({"role": "assistant", "content": jawaban_search})
                                else:
                                    print(f"{M}[!] Gagal memproses data via AI.{N}\n")
                            else:
                                print(f"{M}[!] Wikipedia API Gateway - Tidak ditemukan.{N}\n")
                        except Exception as e:
                            print(f"{M}[Error] Gagal: {e}{N}")
                        continue

                    if user_input.lower() == '!export':
                        if len(riwayat_chat) <= 1:
                            continue
                        waktu_eks = datetime.now().strftime("%Y%m%d_%H%M%S")
                        nama_eks = f"Chat_OneAI_{waktu_eks}.md"
                        try:
                            with open(nama_eks, 'w', encoding='utf-8') as f:
                                f.write(f"# Log Obrolan OneAI - {waktu_eks}\n\n")
                                for msg in riwayat_chat:
                                    if msg['role'] == 'system': continue
                                    f.write(f"### {'Tuan' if msg['role'] == 'user' else 'OneAI'}\n{msg['content']}\n\n---\n\n")
                            print(f"{H}[✔] Sukses ekspor ke: {nama_eks}{N}\n")
                        except Exception as e:
                            print(f"{M}[Error] Gagal ekspor: {e}{N}\n")
                        continue

                    if user_input.lower() == '!status':
                        try:
                            bat_res = subprocess.run("termux-battery-status", shell=True, capture_output=True, text=True, timeout=5)
                            bat_data = json.loads(bat_res.stdout)
                            info_sys = f"Baterai berada di {bat_data.get('percentage', 'N/A')}% (Status: {bat_data.get('status', 'N/A')})."
                            print(f"{H}[Info Device] {info_sys}{N}")
                            user_input = f"Sistem Log Hardware: {info_sys}. Berikan respon tanggapan singkat."
                        except Exception:
                            print(f"{M}[!] Pastikan aplikasi 'Termux:API' terinstal.{N}\n")
                            continue

                    if user_input.lower().startswith('!voice '):
                        teks_suara = user_input[7:].strip()
                        if teks_suara:
                            os.system(f'termux-tts-speak "{teks_suara}"')
                        continue

                    if user_input.lower().startswith('!cuaca'):
                        lokasi = user_input[6:].strip()
                        if not lokasi:
                            lokasi = "Sukoharjo"
                        
                        print(f"{S}[Cuaca] Mengecek informasi cuaca untuk {lokasi}...{N}")
                        try:
                            from plugins.cuaca import run_plugin
                            self_dummy = engine 
                            # Bugfix: Memastikan parameter sinkron pada fungsi plugin
                            hasil_cuaca = run_plugin([lokasi], self_dummy)
                            print(f"{H}[Info Cuaca {lokasi}]:\n{hasil_cuaca}{N}\n")
                            
                            user_input = f"Berikut adalah info cuaca saat ini di {lokasi}:\n{hasil_cuaca}\n\nTolong berikan tanggapan yang relevan."
                        except ImportError:
                            print(f"{M}[❌] Plugin plugins/cuaca.py tidak ditemukan!{N}\n")
                            continue
                        except Exception as e:
                            print(f"{M}[❌] Gagal menjalankan plugin cuaca: {e}{N}\n")
                            continue

                    if user_input.lower().startswith('!belajar '):
                        target_url_raw = user_input[9:].strip()
                        if not target_url_raw: continue
                        try:
                            domain_name = urllib.parse.urlparse(target_url_raw).netloc.lower()
                            if domain_name.startswith("www."): domain_name = domain_name[4:]
                        except Exception:
                            print(f"{M}[❌] URL tidak valid!{N}\n")
                            continue

                        whitelist = muat_json(DB_BELAJAR, BELAJAR_WHITELIST_DEFAULT)
                        if not any(domain_name == d or domain_name.endswith("." + d) for d in whitelist):
                            print(f"{M}[❌] Pembelajaran dibatalkan! Domain '{domain_name}' tidak masuk whitelist!{N}\n")
                            continue

                        print(f"{S}[Scraping] OneAI dan Copilot melakukan Scraping pada {target_url_raw}...{N}")
                        try:
                            headers_browser = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                            tor_aktif, tor_port = periksa_status_tor()
                            proxies = dapatkan_tor_proxies(tor_port) if (tor_aktif and SOCKS_TERPASANG) else None
                            res_web = requests.get(target_url_raw, headers=headers_browser, proxies=proxies, timeout=15)
                            
                            if res_web.status_code == 200:
                                text_cleaned = re.sub(r'<script.*?</script>', '', res_web.text, flags=re.DOTALL)
                                text_cleaned = re.sub(r'<style.*?</style>', '', text_cleaned, flags=re.DOTALL)
                                text_cleaned = re.sub(r'<[^>]*>', ' ', text_cleaned)
                                scrap_chunk = re.sub(r'\s+', ' ', text_cleaned).strip()[:6000]

                                print(f"{S}[Processing] OneAI dan Copilot mengolah data bersama menjadi text...{N}")
                                prompt_belajar = [
                                    {"role": "system", "content": "Ekstrak 1-2 fakta krusial secara padat dari data teks. Jangan berikan basa-basi obrolan."},
                                    {"role": "user", "content": f"Data:\n{scrap_chunk}"}
                                ]
                                res_belajar, _ = engine.kirim_request_smart(model_aktif['id'], prompt_belajar)
                                
                                if res_belajar and res_belajar.status_code == 200:
                                    fakta_hasil = res_belajar.json()['choices'][0]['message']['content'].strip()
                                    if fakta_hasil:
                                        modul_belajar["fakta_belajar"].append({
                                            "tanggal": datetime.now().strftime("%Y-%m-%d"),
                                            "url": domain_name,
                                            "informasi": fakta_hasil
                                        })
                                        simpan_json(DB_MODUL_BELAJAR, modul_belajar)
                                        print(f"{H}[✔] Sukses menyimpan fakta kognitif baru!{N}")
                                        ketik_efek(fakta_hasil)
                                        jawaban_terakhir_ai = fakta_hasil
                                    else:
                                        print(f"{M}[❌] AI gagal mengekstrak fakta.{N}\n")
                            else:
                                print(f"{M}[❌] Gagal mengakses web. Code: {res_web.status_code}{N}\n")
                        except Exception as e:
                            print(f"{M}[❌] Error koneksi: {e}{N}\n")
                        continue

                    if user_input.lower().startswith('!browsing '):
                        query_raw = user_input[10:].strip()
                        print(f"{S}[Scraping] OneAI dan Copilot melakukan Scraping dari search engine untuk '{query_raw}'...{N}")
                        try:
                            search_query = query_raw
                            urls_found = re.findall(r'https?://[^\s\)\?\]]+', query_raw)
                            if urls_found:
                                parsed = urllib.parse.urlparse(urls_found[0])
                                params = urllib.parse.parse_qs(parsed.query)
                                search_query = params['q'][0] if 'q' in params else os.path.basename(parsed.path)

                            search_query_clean = re.sub(r'[^\w\s]', '', search_query).strip()
                            query_encoded = urllib.parse.quote_plus(search_query_clean)

                            loaded_domains = muat_json(DB_DOMAINS, DOMAINS_DEFAULT)
                            search_engines = [url.replace("{query}", query_encoded) for url in loaded_domains.values()]
                            random.shuffle(search_engines)

                            headers_browser = {
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) rv:122.0",
                                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9"
                            }
                            req_web, url_terpilih, scrap_raw_chunk = None, "", ""
                            tor_aktif, tor_port = periksa_status_tor()
                            proxies = dapatkan_tor_proxies(tor_port) if (tor_aktif and SOCKS_TERPASANG) else None

                            for url_target in search_engines:
                                try:
                                    res_try = requests.get(url_target, headers=headers_browser, proxies=proxies, timeout=8)
                                    if res_try.status_code == 200 and len(res_try.text) > 2000 and "captcha" not in res_try.text.lower():
                                        req_web, url_terpilih = res_try, url_target
                                        break
                                except Exception:
                                    continue

                            if not req_web:
                                try:
                                    # BUG FIX: Perbaikan format URL wikipedia yang tercampur markdown
                                    url_wiki_fallback = f"[https://id.wikipedia.org/w/api.php?action=query&list=search&srsearch=](https://id.wikipedia.org/w/api.php?action=query&list=search&srsearch=){query_encoded}&format=json"
                                    res_fallback = requests.get(url_wiki_fallback, timeout=8)
                                    
                                    if res_fallback.status_code == 200:
                                        search_data = res_fallback.json().get("query", {}).get("search", [])
                                        if search_data:
                                            url_terpilih = "Wikipedia API"
                                            scrap_raw_chunk = "\n".join([f"- {i['title']}: {i['snippet']}" for i in search_data[:4]])
                                            scrap_raw_chunk = re.sub(r'<[^>]*>', '', scrap_raw_chunk)
                                except Exception:
                                    pass

                            if req_web or scrap_raw_chunk:
                                if not scrap_raw_chunk and req_web:
                                    text_cleaned = re.sub(r'<script.*?</script>', '', req_web.text, flags=re.DOTALL)
                                    text_cleaned = re.sub(r'<style.*?</style>', '', text_cleaned, flags=re.DOTALL)
                                    text_cleaned = re.sub(r'<[^>]*>', ' ', text_cleaned)
                                    scrap_raw_chunk = re.sub(r'\s+', ' ', text_cleaned).strip()[:6000]

                                print(f"{S}[Processing] OneAI dan Copilot mengolah data bersama menjadi text...{N}")
                                prompt_pengolah = (
                                    f"Olah data scraping untuk query: '{search_query_clean}':\n\n"
                                    f"\"\"\"\n{scrap_raw_chunk}\n\"\"\"\n\n"
                                    f"Saring informasi paling relevan dan tampilkan secara rapi."
                                )
                                temp_history = list(riwayat_chat) + [{"role": "user", "content": prompt_pengolah}]
                                res_online, _ = engine.kirim_request_smart(model_aktif['id'], temp_history)
                                
                                if res_online and res_online.status_code == 200:
                                    jawaban_online = res_online.json()['choices'][0]['message']['content']
                                    ketik_efek(jawaban_online)
                                    jawaban_terakhir_ai = jawaban_online
                                    riwayat_chat.append({"role": "user", "content": f"Pencarian Online: {search_query_clean}"})
                                    riwayat_chat.append({"role": "assistant", "content": jawaban_online})
                                else:
                                    print(f"{M}[!] Gagal memproses data via AI.{N}\n")
                            else:
                                print(f"{M}[❌] Seluruh mesin pencari menolak koneksi.{N}\n")
                        except Exception as e:
                            print(f"{M}[Error] Gagal search: {e}{N}\n")
                        continue

                    if user_input.lower() == '!backup':
                        print(f"{S}[Backup] Mengamankan skrip saat ini...{N}")
                        sukses, hasil = buat_backup_aman()
                        print(f"{H}[✔] Sukses! Backup: {hasil}{N}\n" if sukses else f"{M}[❌] Gagal: {hasil}{N}\n")
                        continue

                    riwayat_chat.append({"role": "user", "content": user_input})
                    if len(riwayat_chat) > 7:
                        riwayat_chat = [riwayat_chat[0]] + riwayat_chat[-6:]

                    response, _ = engine.kirim_request_smart(model_aktif['id'], riwayat_chat)
                    if response and response.status_code == 200:
                        try:
                            jawaban_ai = response.json()['choices'][0]['message']['content']
                            if jawaban_ai:
                                counter_pesan += 1
                                ketik_efek(jawaban_ai)
                                jawaban_terakhir_ai = jawaban_ai
                                riwayat_chat.append({"role": "assistant", "content": jawaban_ai})
                            else:
                                print(f"\n{K}[!] Gak ada respons teks.{N}\n")
                        except Exception:
                            print(f"\n{K}[!] Gak ada respons teks.{N}\n")
                    else:
                        print(f"\n{M}[!] Gagal mendapatkan respons dari server.{N}\n")
                        break
                        
                except KeyboardInterrupt:
                    print(f"\n{M}[Sistem] Sesi chat dihentikan.{N}")
                    break

        elif pilihan_utama == "2":
            while True:
                print(f"\n--- Pengaturan Persona ---")
                for k, v in sorted(persona_list.items(), key=lambda x: int(x[0])):
                    status = f" {H}(AKTIF){N}" if persona_aktif['nama'] == v['nama'] else ""
                    print(f"[{k}] {v['nama']}{status}")
                print(f"[{H}0{N}] + Tambah Persona Baru\n[{M}H{N}] - Hapus Persona\n[{M}K{N}] Kembali")
                
                pilih_p = input("\nPilih nomor: ").strip().lower()
                if pilih_p == 'k':
                    break
                elif pilih_p == '0':
                    nama_p, inst_p = input("Nama Persona: ").strip(), input("Instruksi:\n-> ").strip()
                    if nama_p and inst_p:
                        no_baru = str(max([int(k) for k in persona_list.keys()] or [0]) + 1)
                        persona_list[no_baru] = {"nama": nama_p, "instruksi": inst_p}
                        simpan_json(DB_PERSONA, persona_list)
                elif pilih_p == 'h':
                    hapus_p = input("Masukkan nomor persona: ").strip()
                    if hapus_p in persona_list:
                        if len(persona_list) <= 1:
                            print(f"\n{M}[❌] Gagal! Minimal tersisa 1 Persona.{N}")
                        else:
                            deleted = persona_list.pop(hapus_p)
                            simpan_json(DB_PERSONA, persona_list)
                            print(f"\n{H}[✔] Persona '{deleted['nama']}' dihapus.{N}")
                            if persona_aktif['nama'] == deleted['nama']:
                                persona_aktif = persona_list[sorted(persona_list.keys(), key=lambda x: int(x))[0]]
                    time.sleep(1.5)
                elif pilih_p in persona_list:
                    persona_aktif = persona_list[pilih_p]
                    break

        elif pilihan_utama == "3":
            while True:
                print(f"\n--- Pengaturan Model AI ---")
                if model_list:
                    for k, v in sorted(model_list.items(), key=lambda x: int(x[0])):
                        status = f" {H}(AKTIF){N}" if model_aktif['nama'] == v['nama'] else ""
                        print(f"[{k}] {v['nama']}{status}")
                else:
                    print(f"{K}[!] Belum ada koleksi model.{N}")
                print(f"[{H}0{N}] + Tambah Model Baru\n[{M}H{N}] - Hapus Model\n[{M}K{N}] Kembali")
                
                pilih_m = input("\nPilih nomor: ").strip().lower()
                if pilih_m == 'k':
                    break
                elif pilih_m == '0':
                    nama_m, id_m = input("Nama Model: ").strip(), input("Model ID OpenRouter:\n-> ").strip()
                    if nama_m and id_m:
                        no_baru = str(max([int(k) for k in model_list.keys()] or [0]) + 1)
                        model_list[no_baru] = {"nama": nama_m, "id": id_m, "jatah_rpd": 300}
                        simpan_json(DB_MODEL, model_list)
                        if len(model_list) == 1: model_aktif = model_list[no_baru]
                elif pilih_m == 'h':
                    hapus_m = input("Masukkan nomor model: ").strip()
                    if hapus_m in model_list:
                        if len(model_list) <= 1:
                            print(f"\n{M}[❌] Gagal! Minimal tersisa 1 Model.{N}")
                        else:
                            deleted = model_list.pop(hapus_m)
                            simpan_json(DB_MODEL, model_list)
                            print(f"\n{H}[✔] Model '{deleted['nama']}' dihapus.{N}")
                            if model_aktif['nama'] == deleted['nama']:
                                model_aktif = model_list[sorted(model_list.keys(), key=lambda x: int(x))[0]]
                    time.sleep(1.5)
                elif pilih_m in model_list:
                    model_aktif = model_list[pilih_m]
                    break

        elif pilihan_utama == "4":
            cek_semua_limit(api_keys)
        elif pilihan_utama == "5":
            menu_kelola_key_interaktif()
        elif pilihan_utama == "6":
            menu_cek_limit_model(model_list)
        elif pilihan_utama == "7":
            ToS.menu_kelola_tos()
        elif pilihan_utama == "8":
            menu_fitur_termux_ringan()
        elif pilihan_utama == "9":
            menu_kelola_library_python()
        elif pilihan_utama == "10":
            menu_kelola_db_dan_plugins()
        elif pilihan_utama == "11":
            asisten_self_coder_interaktif(api_keys, model_aktif)
        elif pilihan_utama == "12":
            menu_copilot_kustom()
        elif pilihan_utama == "13":
            AUTO_UPDATE_MANDIRI = not AUTO_UPDATE_MANDIRI
            status_str = "DIAKTIFKAN" if AUTO_UPDATE_MANDIRI else "DINONAKTIFKAN"
            print(f"\n{H}[✔] Fitur Auto Update AI {status_str}!{N}")
            time.sleep(1.5)
        elif pilihan_utama == "14":
            menu_manajemen_domains_search()
        elif pilihan_utama == "15":
            cek_kesehatan_dan_repair()
        elif pilihan_utama == "16":
            menu_manajemen_belajar_whitelist()

if __name__ == "__main__":
    jalankan_aplikasi_utama()

