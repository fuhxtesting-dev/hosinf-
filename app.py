#!/usr/bin/env python3
"""
FX HOSTING - Ultimate VPS Management Panel
Version: 4.0.0 - Admin/User Role System
"""

import os, sys, signal, subprocess, threading, time, shutil, zipfile, py7zr
import psutil, json, hashlib, secrets, re, platform, socket, datetime, base64, math
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, session, abort
from functools import wraps
from pathlib import Path

app = Flask(__name__)

# Secret key persistence
SECRET_KEY_FILE = 'secret_key.txt'
if os.path.exists(SECRET_KEY_FILE):
    with open(SECRET_KEY_FILE, 'r') as f:
        app.secret_key = f.read().strip()
else:
    app.secret_key = secrets.token_hex(32)
    with open(SECRET_KEY_FILE, 'w') as f:
        f.write(app.secret_key)

app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=datetime.timedelta(days=1)
)

# =============================================================================
# CONFIGURATION
# =============================================================================
BASE_DIR = os.getcwd()
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'user_files')
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
DB_FILE = 'servers_db.json'
CONFIG_FILE = 'config.json'
ACTIVITY_LOG = 'activity_log.json'
START_TIME = time.time()

for folder in [STATIC_FOLDER, UPLOAD_FOLDER, os.path.join(BASE_DIR, 'backups')]:
    os.makedirs(folder, exist_ok=True)

DEFAULT_ICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64' viewBox='0 0 24 24' fill='%2300ff00'%3E%3Cpath d='M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zM4 18V6h16v12H4z'/%3E%3Cpath d='M6 8h12v2H6zm0 4h8v2H6z' opacity='.5'/%3E%3C/svg%3E"

THEMES = {
    "matrix": {"name":"Matrix Green","primary":"#00ff00","secondary":"#00cc00","accent":"#00ff80","bg":"#050505","card_bg":"#0a0f0a","text":"#e0ffe0","danger":"#ff3333","warning":"#ffaa00","info":"#00ccff"},
    "night":  {"name":"Night Blue","primary":"#4d88ff","secondary":"#3366cc","accent":"#aa88ff","bg":"#050510","card_bg":"#0a0a1a","text":"#e0e8ff","danger":"#ff4d4d","warning":"#ffaa00","info":"#00ccff"},
    "ocean":  {"name":"Ocean Blue","primary":"#3399ff","secondary":"#0066cc","accent":"#ff99cc","bg":"#050a15","card_bg":"#0a1525","text":"#e0f0ff","danger":"#ff4d4d","warning":"#ffaa00","info":"#00ccff"},
    "sunset": {"name":"Sunset Orange","primary":"#ff9933","secondary":"#cc6600","accent":"#ff66b3","bg":"#150a05","card_bg":"#1f120a","text":"#fff0e0","danger":"#ff3333","warning":"#ffcc00","info":"#00ccff"},
    "blood":  {"name":"Blood Red","primary":"#ff4d4d","secondary":"#cc0000","accent":"#ff80bf","bg":"#150505","card_bg":"#1f0a0a","text":"#ffe0e0","danger":"#ff0000","warning":"#ffaa00","info":"#00ccff"},
    "neon":   {"name":"Neon Purple","primary":"#cc66ff","secondary":"#9933cc","accent":"#ffff80","bg":"#0a0515","card_bg":"#120a1f","text":"#f0e0ff","danger":"#ff4d4d","warning":"#ffaa00","info":"#00ccff"},
    "cyber":  {"name":"Cyber Cyan","primary":"#33ffff","secondary":"#00cccc","accent":"#ff80ff","bg":"#051015","card_bg":"#0a1a1f","text":"#e0ffff","danger":"#ff4d4d","warning":"#ffaa00","info":"#0088ff"},
    "vapor":  {"name":"Vapor Pink","primary":"#ff99cc","secondary":"#cc6699","accent":"#80ffff","bg":"#150510","card_bg":"#1f0a1a","text":"#ffe0f0","danger":"#ff3333","warning":"#ffcc00","info":"#00ccff"},
    "gold":   {"name":"Royal Gold","primary":"#ffcc66","secondary":"#cc9933","accent":"#ffb380","bg":"#151005","card_bg":"#1f1a0a","text":"#fff8e0","danger":"#ff3333","warning":"#ffaa00","info":"#00ccff"},
    "tokyo":  {"name":"Tokyo Night","primary":"#7aa2f7","secondary":"#565f89","accent":"#bb9af7","bg":"#06080f","card_bg":"#0d111f","text":"#c0caf5","danger":"#f7768e","warning":"#e0af68","info":"#7dcfff"},
    "dracula":{"name":"Dracula","primary":"#ff79c6","secondary":"#bd93f9","accent":"#8be9fd","bg":"#0d0d14","card_bg":"#161620","text":"#f8f8f2","danger":"#ff5555","warning":"#f1fa8c","info":"#8be9fd"},
    "monokai":{"name":"Monokai","primary":"#a6e22e","secondary":"#f92672","accent":"#66d9ef","bg":"#0d0d0d","card_bg":"#1a1a1a","text":"#f8f8f0","danger":"#f92672","warning":"#e6db74","info":"#66d9ef"},
    "nord":   {"name":"Nord","primary":"#88c0d0","secondary":"#81a1c1","accent":"#b48ead","bg":"#0d1117","card_bg":"#161b22","text":"#d8dee9","danger":"#bf616a","warning":"#ebcb8b","info":"#81a1c1"},
    "midnight":{"name":"Midnight","primary":"#7c4dff","secondary":"#512da8","accent":"#ff6e40","bg":"#080510","card_bg":"#110d1f","text":"#f0ecff","danger":"#ff5252","warning":"#ffd740","info":"#40c4ff"},
    "emerald":{"name":"Emerald","primary":"#00e676","secondary":"#00c853","accent":"#69f0ae","bg":"#05150a","card_bg":"#0a1f12","text":"#e0ffec","danger":"#ff5252","warning":"#ffd740","info":"#40c4ff"},
    "amber":  {"name":"Amber","primary":"#ffab00","secondary":"#ff6d00","accent":"#ffe57f","bg":"#151005","card_bg":"#1f1808","text":"#fff8e0","danger":"#ff5252","warning":"#ffcc00","info":"#00b0ff"},
    "ruby":   {"name":"Ruby","primary":"#ff1744","secondary":"#d50000","accent":"#ff8a80","bg":"#150508","card_bg":"#1f0a0f","text":"#ffe0e8","danger":"#ff5252","warning":"#ffd740","info":"#40c4ff"},
    "sapphire":{"name":"Sapphire","primary":"#2979ff","secondary":"#2962ff","accent":"#82b1ff","bg":"#050a15","card_bg":"#0a1025","text":"#e0ecff","danger":"#ff5252","warning":"#ffd740","info":"#00b0ff"},
    "amethyst":{"name":"Amethyst","primary":"#e040fb","secondary":"#aa00ff","accent":"#ea80fc","bg":"#120515","card_bg":"#1c0a1f","text":"#f8e0ff","danger":"#ff5252","warning":"#ffd740","info":"#00b0ff"},
    "silver": {"name":"Silver Grey","primary":"#b3b3b3","secondary":"#808080","accent":"#cccccc","bg":"#0a0a0a","card_bg":"#151515","text":"#f0f0f0","danger":"#ff4d4d","warning":"#ffaa00","info":"#00ccff"}
}

DEFAULT_CONFIG = {
    "site_title": "FX HOSTING | Ultimate VPS Panel",
    "site_header": "FX HOSTING",
    "icon_url": DEFAULT_ICON,
    "theme": "matrix",
    "font_family": "terminal",
    "terminal_height": 300,
    "auto_refresh": True,
    "notifications": True,
    "show_system_stats": True,
    "session_timeout": 60,
    "max_log_lines": 2000,
    "passwords": {
        "secret": hashlib.sha256("FXFUHXFFKING".encode()).hexdigest(),
        "user": hashlib.sha256("admin".encode()).hexdigest()
    },
    # Webhook notifications (Discord / Telegram)
    "webhooks": {
        "discord_url": "",
        "telegram_bot_token": "",
        "telegram_chat_id": "",
        "notify_on_crash": True,
        "notify_on_start": False,
        "notify_on_stop": False,
        "notify_on_high_cpu": True,
        "cpu_alert_threshold": 90,
        "ram_alert_threshold": 90
    }
}

USERS_FILE = 'users_db.json'
DOMAINS_FILE = 'domains_db.json'
RESOURCE_HISTORY_FILE = 'resource_history.json'

DEFAULT_USERS = {
    "admin_default": {
        "username": "admin",
        "password_hash": hashlib.sha256("FXFUHXFFKING".encode()).hexdigest(),
        "role": "admin",
        "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
        "is_builtin": True
    },
    "user_default": {
        "username": "user",
        "password_hash": hashlib.sha256("admin".encode()).hexdigest(),
        "role": "user",
        "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
        "is_builtin": True
    }
}

# =============================================================================
# DATA PERSISTENCE
# =============================================================================

def load_json(filename, default=None):
    if default is None: default = {}
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except: return default
    return default

def save_json(filename, data):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving {filename}: {e}")

def load_config():
    config = load_json(CONFIG_FILE, DEFAULT_CONFIG.copy())
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value
    if 'passwords' not in config:
        config['passwords'] = DEFAULT_CONFIG['passwords']
    return config

CONFIG = load_config()
SERVERS = {}

# ---- Multi-user store ----
def load_users():
    users = load_json(USERS_FILE, None)
    if users is None:
        users = DEFAULT_USERS.copy()
        save_json(USERS_FILE, users)
    return users

def save_users(users):
    save_json(USERS_FILE, users)

USERS = load_users()

# ---- Domain mapping store ----
def load_domains():
    return load_json(DOMAINS_FILE, {})

def save_domains(domains):
    save_json(DOMAINS_FILE, domains)

DOMAINS = load_domains()

# ---- Resource history (per-server CPU/RAM over time, last 60 points = ~30 min @ 30s) ----
def load_resource_history():
    return load_json(RESOURCE_HISTORY_FILE, {})

def save_resource_history(hist):
    save_json(RESOURCE_HISTORY_FILE, hist)

RESOURCE_HISTORY = load_resource_history()
HEALTH_SCORES = {}   # server_id -> {'score': int, 'crashes_24h': int, 'last_crash': str}
CRASH_LOG = {}        # server_id -> list of crash timestamps (epoch)

def log_activity(action, details="", role="system"):
    logs = load_json(ACTIVITY_LOG, [])
    logs.append({
        "time": time.strftime('%Y-%m-%d %H:%M:%S'),
        "action": action,
        "details": details,
        "role": role
    })
    if len(logs) > 1000:
        logs = logs[-800:]
    save_json(ACTIVITY_LOG, logs)

def save_servers():
    try:
        data = {}
        for sid, s in SERVERS.items():
            data[sid] = {
                'cmd': s.get('cmd', ''),
                'cwd': s.get('cwd', ''),
                'path': s.get('path', ''),
                'auto_restart': s.get('auto_restart', False),
                'restart_interval': s.get('restart_interval', '1h'),
                'status': s.get('status', 'stopped'),
                'last_start_time': s.get('last_start_time', 0),
                'created_at': s.get('created_at', time.strftime('%Y-%m-%d %H:%M:%S')),
                'notes': s.get('notes', ''),
                'group': s.get('group', 'default'),
                'tags': s.get('tags', []),
                'env_vars': s.get('env_vars', {})
            }
        save_json(DB_FILE, data)
    except Exception as e:
        print(f"Error saving servers: {e}")

def load_servers():
    global SERVERS
    saved = load_json(DB_FILE, {})
    for sid, s in saved.items():
        SERVERS[sid] = {
            'process': None, 'cmd': s.get('cmd', ''), 'cwd': s.get('cwd', ''),
            'auto_restart': s.get('auto_restart', False), 'restart_interval': s.get('restart_interval', '1h'),
            'logs': [f">>> Server '{sid}' loaded at {time.strftime('%Y-%m-%d %H:%M:%S')}"],
            'status': 'stopped', 'path': s.get('path', ''), 'last_start_time': 0,
            'created_at': s.get('created_at', time.strftime('%Y-%m-%d %H:%M:%S')),
            'notes': s.get('notes', ''), 'group': s.get('group', 'default'),
            'tags': s.get('tags', []), 'env_vars': s.get('env_vars', {})
        }

load_servers()

# =============================================================================
# DECORATORS & ROLE SYSTEM
# =============================================================================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Blocks USER role - only ADMIN can access"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Access Denied: Admin permission required', 'code': 'ADMIN_ONLY'}), 403
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

def get_current_role():
    return "admin" if session.get('is_admin') else "user"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_system_stats():
    try:
        cpu = psutil.cpu_percent(interval=0.3)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()
        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        boot_time = psutil.boot_time()
        uptime = int(time.time() - boot_time)
        return {
            'cpu': cpu, 'ram_used': round(ram.used/(1024**3),2), 'ram_total': round(ram.total/(1024**3),2),
            'ram_percent': ram.percent, 'disk_used': round(disk.used/(1024**3),2),
            'disk_total': round(disk.total/(1024**3),2), 'disk_percent': round(disk.percent,1),
            'net_sent': round(net.bytes_sent/(1024**2),2), 'net_recv': round(net.bytes_recv/(1024**2),2),
            'load_avg': [round(x,2) for x in load_avg], 'uptime': uptime,
            'processes': len(psutil.pids()), 'connections': len(psutil.net_connections())
        }
    except Exception as e:
        return {'cpu':0,'ram_used':0,'ram_total':0,'ram_percent':0,'disk_used':0,'disk_total':0,'disk_percent':0,'net_sent':0,'net_recv':0,'load_avg':[0,0,0],'uptime':0,'processes':0,'connections':0}

def get_network_info():
    try:
        hostname = socket.gethostname()
        try: ip = socket.gethostbyname(hostname)
        except: ip = "127.0.0.1"
        interfaces = {}
        for name, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    interfaces[name] = {'ip': addr.address, 'netmask': addr.netmask}
        return {'hostname': hostname, 'ip': ip, 'interfaces': interfaces}
    except:
        return {'hostname':'unknown','ip':'127.0.0.1','interfaces':{}}

def format_uptime(seconds):
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    parts = []
    if days > 0: parts.append(f"{days}d")
    if hours > 0: parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)

def kill_process_completely(proc):
    try:
        if proc is None: return
        parent = psutil.Process(proc.pid)
        children = parent.children(recursive=True)
        for child in children:
            try: child.terminate()
            except: pass
        gone, alive = psutil.wait_procs(children, timeout=3)
        for child in alive:
            try: child.kill()
            except: pass
        try:
            parent.terminate()
            parent.wait(timeout=3)
        except:
            try: parent.kill()
            except: pass
    except: pass

def log_monitor(server_id, proc_obj):
    server = SERVERS.get(server_id)
    if not server: return
    try:
        for line in iter(proc_obj.stdout.readline, ''):
            if server_id not in SERVERS or SERVERS[server_id].get('process') != proc_obj: break
            if line:
                cleaned = line.strip()
                if cleaned:
                    max_lines = CONFIG.get('max_log_lines', 2000)
                    if len(SERVERS[server_id]['logs']) > max_lines:
                        SERVERS[server_id]['logs'] = SERVERS[server_id]['logs'][-int(max_lines*0.9):]
                    SERVERS[server_id]['logs'].append(cleaned)
    except: pass
    finally:
        try: proc_obj.stdout.close()
        except: pass
    if server_id in SERVERS and SERVERS[server_id].get('process') == proc_obj:
        SERVERS[server_id]['status'] = 'stopped'
        SERVERS[server_id]['process'] = None
        SERVERS[server_id]['logs'].append(">>> [FX HOSTING] Process terminated.")
        save_servers()
        # Crash detection: if it wasn't a manual stop (no explicit 'Stopped'/'restart' log just before)
        recent_logs = SERVERS[server_id]['logs'][-3:]
        was_manual = any('Stopped at' in l or 'restart triggered' in l for l in recent_logs)
        if not was_manual:
            record_crash(server_id)
            notify_event('crash', server_id, "Process exited unexpectedly (possible crash)")

def start_server_internal(server_id, server):
    if server['status'] == 'running': return True
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    for k, v in server.get('env_vars', {}).items():
        env[k] = v
    work_dir = os.path.join(server['path'], server.get('cwd', ''))
    if not os.path.exists(work_dir): work_dir = server['path']
    try:
        if not server['cmd'] or server['cmd'].strip() == '':
            server['logs'].append(">>> [FX HOSTING] Error: No start command specified")
            return False
        if not os.path.exists(work_dir):
            server['logs'].append(f">>> [FX HOSTING] Error: Directory not found: {work_dir}")
            return False
        proc = subprocess.Popen(
            server['cmd'], shell=True, cwd=work_dir,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE, text=True, bufsize=1,
            universal_newlines=True, env=env,
            preexec_fn=os.setsid if os.name != 'nt' else None
        )
        server['process'] = proc
        server['status'] = 'running'
        server['last_start_time'] = time.time()
        server['logs'].append(f">>> [FX HOSTING] Server started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        threading.Thread(target=log_monitor, args=(server_id, proc), daemon=True).start()
        save_servers()
        log_activity("Server Start", f"Server '{server_id}' started", get_current_role())
        notify_event('start', server_id, "Server started successfully")
        return True
    except Exception as e:
        server['logs'].append(f">>> [FX HOSTING] Failed to start: {str(e)}")
        return False

def auto_restarter():
    while True:
        time.sleep(10)
        current_time = time.time()
        for server_id, server in list(SERVERS.items()):
            try:
                if server.get('status') == 'running' and server.get('auto_restart'):
                    interval_map = {'30s':30,'1m':60,'5m':300,'10m':600,'15m':900,'20m':1200,'25m':1500,'30m':1800,'1h':3600,'2h':7200,'3h':10800,'6h':21600,'12h':43200,'24h':86400}
                    interval_sec = interval_map.get(server.get('restart_interval', '1h'), 3600)
                    if current_time - server.get('last_start_time', current_time) >= interval_sec:
                        server['logs'].append(f">>> [FX HOSTING] Auto-restarting...")
                        if server.get('process'): kill_process_completely(server['process'])
                        server['process'] = None
                        server['status'] = 'stopped'
                        start_server_internal(server_id, server)
            except Exception as e:
                print(f"Auto-restart error for {server_id}: {e}")

threading.Thread(target=auto_restarter, daemon=True).start()

# =============================================================================
# WEBHOOK NOTIFICATIONS (Discord / Telegram)
# =============================================================================

def send_discord_webhook(title, description, color=0xff0000):
    url = CONFIG.get('webhooks', {}).get('discord_url', '').strip()
    if not url:
        return
    try:
        import urllib.request
        payload = json.dumps({
            "embeds": [{
                "title": title, "description": description, "color": color,
                "footer": {"text": "FX HOSTING Panel"},
                "timestamp": datetime.datetime.utcnow().isoformat()
            }]
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"Discord webhook error: {e}")

def send_telegram_webhook(text):
    wh = CONFIG.get('webhooks', {})
    token = wh.get('telegram_bot_token', '').strip()
    chat_id = wh.get('telegram_chat_id', '').strip()
    if not token or not chat_id:
        return
    try:
        import urllib.request, urllib.parse
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": text, "parse_mode": "HTML"}).encode()
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"Telegram webhook error: {e}")

def notify_event(event_type, server_id, message):
    """event_type: crash | start | stop | high_cpu | high_ram"""
    wh = CONFIG.get('webhooks', {})
    flag_map = {
        'crash': 'notify_on_crash', 'start': 'notify_on_start',
        'stop': 'notify_on_stop', 'high_cpu': 'notify_on_high_cpu',
        'high_ram': 'notify_on_high_cpu'
    }
    if not wh.get(flag_map.get(event_type, ''), False):
        return
    icons = {'crash': '🔴', 'start': '🟢', 'stop': '🟡', 'high_cpu': '⚠️', 'high_ram': '⚠️'}
    icon = icons.get(event_type, 'ℹ️')
    title = f"{icon} FX HOSTING — {event_type.replace('_',' ').upper()}"
    full_msg = f"{title}\nServer: {server_id}\n{message}\nTime: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    color_map = {'crash': 0xff0000, 'start': 0x00ff00, 'stop': 0xffaa00, 'high_cpu': 0xff6600, 'high_ram': 0xff6600}
    threading.Thread(target=send_discord_webhook, args=(title, f"**Server:** {server_id}\n{message}", color_map.get(event_type, 0x888888)), daemon=True).start()
    threading.Thread(target=send_telegram_webhook, args=(full_msg,), daemon=True).start()

# =============================================================================
# SERVER HEALTH SCORE & CRASH DETECTION
# =============================================================================

def record_crash(server_id):
    now = time.time()
    CRASH_LOG.setdefault(server_id, [])
    CRASH_LOG[server_id].append(now)
    # keep only last 24h
    CRASH_LOG[server_id] = [t for t in CRASH_LOG[server_id] if now - t < 86400]

def compute_health_score(server_id):
    server = SERVERS.get(server_id)
    if not server:
        return {'score': 0, 'crashes_24h': 0, 'status': 'unknown'}
    crashes_24h = len([t for t in CRASH_LOG.get(server_id, []) if time.time() - t < 86400])
    score = 100
    score -= min(crashes_24h * 15, 60)
    if server.get('status') != 'running':
        score -= 20
    score = max(0, min(100, score))
    if score >= 80: label = 'Excellent'
    elif score >= 60: label = 'Good'
    elif score >= 35: label = 'Degraded'
    else: label = 'Critical'
    return {'score': score, 'crashes_24h': crashes_24h, 'status': label}

def resource_history_collector():
    """Collect per-server CPU/RAM usage (via psutil per-process) every 30s"""
    while True:
        time.sleep(30)
        try:
            for server_id, server in list(SERVERS.items()):
                proc = server.get('process')
                cpu = 0.0
                ram_mb = 0.0
                if proc and server.get('status') == 'running':
                    try:
                        p = psutil.Process(proc.pid)
                        children = p.children(recursive=True)
                        cpu = p.cpu_percent(interval=0.1)
                        ram_mb = p.memory_info().rss / (1024*1024)
                        for c in children:
                            try:
                                cpu += c.cpu_percent(interval=0)
                                ram_mb += c.memory_info().rss / (1024*1024)
                            except: pass
                    except: pass
                RESOURCE_HISTORY.setdefault(server_id, [])
                RESOURCE_HISTORY[server_id].append({
                    't': time.strftime('%H:%M:%S'), 'cpu': round(cpu, 1), 'ram_mb': round(ram_mb, 1)
                })
                if len(RESOURCE_HISTORY[server_id]) > 60:
                    RESOURCE_HISTORY[server_id] = RESOURCE_HISTORY[server_id][-60:]

                # High resource alert
                wh = CONFIG.get('webhooks', {})
                if cpu >= wh.get('cpu_alert_threshold', 90):
                    notify_event('high_cpu', server_id, f"CPU usage: {cpu:.1f}%")

            save_resource_history(RESOURCE_HISTORY)
        except Exception as e:
            print(f"Resource history error: {e}")

threading.Thread(target=resource_history_collector, daemon=True).start()

# =============================================================================
# AUTH ROUTES
# =============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        username = request.form.get('username', '').strip()
        hashed = hashlib.sha256(password.encode()).hexdigest()

        matched_user = None
        matched_uid = None

        # 1) Try multi-user DB first (match by username+password, or password-only if no username given)
        for uid, u in USERS.items():
            if u.get('password_hash') == hashed:
                if username and u.get('username', '').lower() != username.lower():
                    continue
                matched_user = u
                matched_uid = uid
                break

        if matched_user:
            session['logged_in'] = True
            session['is_admin'] = (matched_user.get('role') == 'admin')
            session['login_time'] = time.time()
            session['username'] = matched_user.get('username')
            session['user_id'] = matched_uid
            session['role_label'] = 'ADMIN' if session['is_admin'] else 'USER'
            log_activity("Login", f"User '{matched_user.get('username')}' logged in ({session['role_label']})", session['is_admin'] and 'admin' or 'user')
            return redirect(url_for('index'))

        # 2) Legacy fallback: old single admin/user password system
        if hashed == CONFIG['passwords']['secret']:
            session['logged_in'] = True
            session['is_admin'] = True
            session['login_time'] = time.time()
            session['username'] = 'admin'
            session['role_label'] = 'ADMIN'
            log_activity("Login", "Legacy admin logged in", "admin")
            return redirect(url_for('index'))
        elif hashed == CONFIG['passwords']['user']:
            session['logged_in'] = True
            session['is_admin'] = False
            session['login_time'] = time.time()
            session['username'] = 'user'
            session['role_label'] = 'USER'
            log_activity("Login", "Legacy user logged in", "user")
            return redirect(url_for('index'))
        else:
            log_activity("Login Failed", f"Invalid credentials (user: {username or 'n/a'})", "unknown")
            return render_template('login.html', error="Access Denied: Invalid credentials", config=CONFIG, themes=THEMES)
    return render_template('login.html', config=CONFIG, themes=THEMES)

@app.route('/logout')
def logout():
    log_activity("Logout", "User logged out", get_current_role())
    session.clear()
    return redirect(url_for('login'))

# =============================================================================
# MAIN ROUTE
# =============================================================================

@app.route('/')
@login_required
def index():
    stats = get_system_stats()
    net_info = get_network_info()
    current_theme = THEMES.get(CONFIG.get('theme', 'matrix'), THEMES['matrix'])
    is_admin = session.get('is_admin', False)
    serializable_servers = {}
    groups = set()
    for sid, s in SERVERS.items():
        serializable_servers[sid] = {
            'cmd': s.get('cmd', '') if is_admin else '***',  # hide cmd from users
            'cwd': s.get('cwd', ''),
            'auto_restart': s.get('auto_restart', False),
            'restart_interval': s.get('restart_interval', '1h'),
            'status': s.get('status', 'stopped'),
            'path': s.get('path', '') if is_admin else '***',
            'last_start_time': s.get('last_start_time', 0),
            'created_at': s.get('created_at', 'Unknown'),
            'notes': s.get('notes', '') if is_admin else '',
            'group': s.get('group', 'default'),
            'tags': s.get('tags', []),
            'uptime': format_uptime(int(time.time() - s.get('last_start_time', 0))) if s.get('status') == 'running' else '0m',
            'pid': s['process'].pid if s.get('process') else None
        }
        groups.add(s.get('group', 'default'))
    app_uptime = format_uptime(int(time.time() - START_TIME))
    health_map = {sid: compute_health_score(sid) for sid in SERVERS}
    return render_template('index.html',
        servers=serializable_servers, stats=stats, net_info=net_info,
        total_count=len(SERVERS), running_count=sum(1 for s in SERVERS.values() if s['status'] == 'running'),
        config=CONFIG, theme=current_theme, themes=THEMES,
        is_admin=is_admin, app_uptime=app_uptime,
        username=session.get('username', 'user'),
        domains=DOMAINS, health_map=health_map,
        start_date=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(START_TIME)),
        groups=sorted(groups), base_dir=BASE_DIR if is_admin else '***')

# =============================================================================
# READ-ONLY APIs (Both ADMIN and USER can access)
# =============================================================================

@app.route('/api/server/<server_id>/logs')
@login_required
def get_server_logs(server_id):
    if server_id not in SERVERS:
        return jsonify({'logs': ''})
    return jsonify({'logs': '\n'.join(SERVERS[server_id]['logs'][-500:])})

@app.route('/api/system/stats')
@login_required
def system_stats():
    return jsonify(get_system_stats())

@app.route('/api/system/info')
@login_required
def system_info():
    try:
        info = {
            'platform': platform.platform(), 'processor': platform.processor() or 'Unknown',
            'architecture': platform.architecture()[0], 'python_version': platform.python_version(),
            'hostname': socket.gethostname(), 'cpu_count': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
            'total_ram': round(psutil.virtual_memory().total/(1024**3),2),
            'swap': round(psutil.swap_memory().total/(1024**3),2),
            'boot_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(psutil.boot_time())),
            'users': [u.name for u in psutil.users()]
        }
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/processes')
@login_required
def get_processes():
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'create_time']):
            try:
                info = proc.info
                info['create_time'] = time.strftime('%H:%M:%S', time.localtime(info['create_time']))
                processes.append(info)
            except: pass
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        return jsonify({'processes': processes[:100]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/ports')
@login_required
def get_ports():
    try:
        connections = psutil.net_connections()
        ports = []
        for conn in connections:
            if conn.laddr:
                try: proc_name = psutil.Process(conn.pid).name() if conn.pid else ''
                except: proc_name = ''
                ports.append({'port': conn.laddr.port, 'address': conn.laddr.ip,
                              'status': conn.status or '', 'pid': conn.pid, 'name': proc_name})
        ports.sort(key=lambda x: x['port'])
        return jsonify({'ports': ports[:200]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/activity')
@login_required
def get_activity():
    # Users only see limited activity, admins see all
    logs = load_json(ACTIVITY_LOG, [])
    if not session.get('is_admin'):
        # Users only see server start/stop events (not sensitive info)
        safe_logs = [l for l in logs if l.get('action') in ['Server Start', 'Stop', 'Restart', 'Login', 'Logout']]
        return jsonify({'logs': list(reversed(safe_logs))[:50]})
    return jsonify({'logs': list(reversed(logs))[:200]})

@app.route('/api/settings', methods=['GET'])
@login_required
def settings_get():
    safe_config = {k: v for k, v in CONFIG.items() if k != 'passwords'}
    return jsonify(safe_config)

# =============================================================================
# ADMIN-ONLY APIs
# =============================================================================

@app.route('/api/server/create', methods=['POST'])
@admin_required
def create_server():
    try:
        data = request.get_json() or request.form
        server_name = data.get('server_name', '').strip().replace(' ', '_')
        start_command = data.get('start_command', '').strip()
        group = data.get('group', 'default').strip()
        notes = data.get('notes', '').strip()
        if not server_name: return jsonify({'error': 'Server name required'}), 400
        if server_name in SERVERS: return jsonify({'error': 'Server name already exists'}), 400
        server_path = os.path.join(UPLOAD_FOLDER, server_name)
        os.makedirs(server_path, exist_ok=True)
        SERVERS[server_name] = {
            'process': None, 'cmd': start_command, 'cwd': '',
            'logs': [f">>> [FX HOSTING] Server '{server_name}' created at {time.strftime('%Y-%m-%d %H:%M:%S')}"],
            'auto_restart': False, 'restart_interval': '1h', 'last_start_time': 0,
            'status': 'stopped', 'path': server_path,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'notes': notes, 'group': group, 'tags': [], 'env_vars': {}
        }
        save_servers()
        log_activity("Create Server", f"Created server '{server_name}'", "admin")
        return jsonify({'status': 'ok', 'server_id': server_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/upload', methods=['POST'])
@admin_required
def upload_server_file():
    try:
        server_name = request.form.get('server_name', '').strip().replace(' ', '_')
        start_command = request.form.get('start_command', '').strip()
        group = request.form.get('group', 'default').strip()
        notes = request.form.get('notes', '').strip()
        if not server_name: return jsonify({'error': 'Server name required'}), 400
        if server_name in SERVERS: return jsonify({'error': 'Server name already exists'}), 400
        server_path = os.path.join(UPLOAD_FOLDER, server_name)
        os.makedirs(server_path, exist_ok=True)
        file = request.files.get('file')
        if file and file.filename:
            file_path = os.path.join(server_path, file.filename)
            file.save(file_path)
            if file.filename.lower().endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as z: z.extractall(server_path)
            elif file.filename.lower().endswith('.7z'):
                with py7zr.SevenZipFile(file_path, mode='r') as z: z.extractall(server_path)
        SERVERS[server_name] = {
            'process': None, 'cmd': start_command, 'cwd': '',
            'logs': [f">>> [FX HOSTING] Server '{server_name}' created with upload at {time.strftime('%Y-%m-%d %H:%M:%S')}"],
            'auto_restart': False, 'restart_interval': '1h', 'last_start_time': 0,
            'status': 'stopped', 'path': server_path,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'notes': notes, 'group': group, 'tags': [], 'env_vars': {}
        }
        save_servers()
        log_activity("Upload Server", f"Created server '{server_name}' with upload", "admin")
        return jsonify({'status': 'ok', 'server_id': server_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/<action>', methods=['POST'])
@login_required
def server_action_api(server_id, action):
    # USER can ONLY view logs (handled separately), not perform actions
    if not session.get('is_admin'):
        return jsonify({'error': 'Access Denied: Admin permission required', 'code': 'ADMIN_ONLY'}), 403
    if server_id not in SERVERS:
        return jsonify({'error': 'Server not found'}), 404
    server = SERVERS[server_id]
    try:
        if action == 'start':
            start_server_internal(server_id, server)
            return jsonify({'status': 'ok'})
        elif action == 'stop':
            if server['process']: kill_process_completely(server['process'])
            server['process'] = None
            server['status'] = 'stopped'
            server['logs'].append(f">>> [FX HOSTING] Stopped at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            save_servers()
            log_activity("Stop", f"Server '{server_id}' stopped", "admin")
            notify_event('stop', server_id, "Server stopped manually")
            return jsonify({'status': 'ok'})
        elif action == 'restart':
            if server['process']: kill_process_completely(server['process'])
            server['process'] = None
            server['status'] = 'stopped'
            server['logs'].append(">>> [FX HOSTING] Manual restart triggered...")
            time.sleep(0.5)
            start_server_internal(server_id, server)
            return jsonify({'status': 'ok'})
        elif action == 'delete':
            if server['process']: kill_process_completely(server['process'])
            server['process'] = None
            if os.path.exists(server['path']): shutil.rmtree(server['path'], ignore_errors=True)
            del SERVERS[server_id]
            save_servers()
            log_activity("Delete", f"Server '{server_id}' deleted", "admin")
            return jsonify({'status': 'ok'})
        elif action == 'clone':
            new_name = (request.get_json() or {}).get('new_name', '').strip().replace(' ', '_')
            if not new_name or new_name in SERVERS:
                return jsonify({'error': 'Invalid clone name'}), 400
            new_path = os.path.join(UPLOAD_FOLDER, new_name)
            if os.path.exists(server['path']): shutil.copytree(server['path'], new_path)
            SERVERS[new_name] = {
                'process': None, 'cmd': server['cmd'], 'cwd': server.get('cwd', ''),
                'logs': [f">>> [FX HOSTING] Cloned from '{server_id}' at {time.strftime('%Y-%m-%d %H:%M:%S')}"],
                'auto_restart': False, 'restart_interval': '1h', 'last_start_time': 0,
                'status': 'stopped', 'path': new_path,
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'notes': f"Cloned from {server_id}", 'group': server.get('group', 'default'),
                'tags': list(server.get('tags', [])), 'env_vars': dict(server.get('env_vars', {}))
            }
            save_servers()
            log_activity("Clone", f"Server '{server_id}' cloned to '{new_name}'", "admin")
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'error': 'Invalid action'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/config', methods=['GET', 'POST'])
@admin_required
def server_config(server_id):
    if server_id not in SERVERS:
        return jsonify({'error': 'Server not found'}), 404
    if request.method == 'POST':
        data = request.get_json()
        if not data: return jsonify({'error': 'No data provided'}), 400
        SERVERS[server_id]['cmd'] = data.get('cmd', SERVERS[server_id]['cmd'])
        SERVERS[server_id]['cwd'] = data.get('cwd', SERVERS[server_id].get('cwd', ''))
        SERVERS[server_id]['auto_restart'] = data.get('auto_restart', SERVERS[server_id].get('auto_restart', False))
        SERVERS[server_id]['restart_interval'] = data.get('restart_interval', SERVERS[server_id].get('restart_interval', '1h'))
        SERVERS[server_id]['notes'] = data.get('notes', SERVERS[server_id].get('notes', ''))
        SERVERS[server_id]['group'] = data.get('group', SERVERS[server_id].get('group', 'default'))
        SERVERS[server_id]['env_vars'] = data.get('env_vars', SERVERS[server_id].get('env_vars', {}))
        save_servers()
        log_activity("Config Update", f"Server '{server_id}' config updated", "admin")
        return jsonify({'status': 'ok'})
    return jsonify({
        'cmd': SERVERS[server_id].get('cmd', ''), 'cwd': SERVERS[server_id].get('cwd', ''),
        'auto_restart': SERVERS[server_id].get('auto_restart', False),
        'restart_interval': SERVERS[server_id].get('restart_interval', '1h'),
        'notes': SERVERS[server_id].get('notes', ''), 'group': SERVERS[server_id].get('group', 'default'),
        'env_vars': SERVERS[server_id].get('env_vars', {}), 'created_at': SERVERS[server_id].get('created_at', 'Unknown')
    })

@app.route('/api/server/<server_id>/input', methods=['POST'])
@admin_required
def send_server_input(server_id):
    cmd = (request.get_json() or request.form).get('command', '')
    if not cmd or server_id not in SERVERS: return jsonify({'error': 'Invalid request'}), 400
    server = SERVERS[server_id]
    if not server['process']: return jsonify({'error': 'Process not running'}), 400
    try:
        proc = server['process']
        if proc.stdin and not proc.stdin.closed:
            proc.stdin.write(cmd + '\n')
            proc.stdin.flush()
            server['logs'].append(f">>> [INPUT] {cmd}")
            return jsonify({'status': 'ok'})
        return jsonify({'error': 'stdin closed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/clear_logs', methods=['POST'])
@admin_required
def clear_server_logs(server_id):
    if server_id not in SERVERS: return jsonify({'error': 'Server not found'}), 404
    SERVERS[server_id]['logs'] = [f">>> [FX HOSTING] Logs cleared at {time.strftime('%Y-%m-%d %H:%M:%S')}"]
    return jsonify({'status': 'ok'})

# =============================================================================
# FILE MANAGEMENT (ADMIN ONLY)
# =============================================================================

@app.route('/api/files/<server_id>')
@admin_required
def list_files(server_id):
    if server_id not in SERVERS: return jsonify({'error': 'Server not found'}), 404
    subpath = request.args.get('path', '')
    base_path = SERVERS[server_id]['path']
    full_path = os.path.normpath(os.path.join(base_path, subpath)) if subpath else base_path
    if not os.path.realpath(full_path).startswith(os.path.realpath(base_path)):
        full_path = base_path; subpath = ''
    if not os.path.exists(full_path): return jsonify({'files': [], 'current_path': '', 'total_size': '0 B'})
    files = []
    total_size = 0
    for item in os.listdir(full_path):
        item_path = os.path.join(full_path, item)
        is_file = os.path.isfile(item_path)
        size = os.path.getsize(item_path) if is_file else 0
        total_size += size
        size_str = f"{size} B" if size < 1024 else (f"{size/1024:.1f} KB" if size < 1024**2 else f"{size/(1024**2):.1f} MB")
        files.append({'name': item, 'size': size_str, 'raw_size': size, 'type': 'file' if is_file else 'dir',
                      'ext': os.path.splitext(item)[1].lower() if is_file else '',
                      'modified': time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(item_path)))})
    files.sort(key=lambda x: (x['type'] != 'dir', x['name'].lower()))
    total_str = f"{total_size} B" if total_size < 1024 else (f"{total_size/1024:.1f} KB" if total_size < 1024**2 else f"{total_size/(1024**2):.1f} MB")
    return jsonify({'files': files, 'current_path': subpath, 'total_size': total_str})

@app.route('/api/files/<server_id>/content')
@admin_required
def file_content(server_id):
    if server_id not in SERVERS: return jsonify({'error': 'Server not found'}), 404
    filename = request.args.get('filename', '')
    subpath = request.args.get('path', '')
    base_path = SERVERS[server_id]['path']
    file_path = os.path.normpath(os.path.join(base_path, subpath, filename))
    if not os.path.realpath(file_path).startswith(os.path.realpath(base_path)): return jsonify({'error': 'Invalid path'}), 400
    if not os.path.isfile(file_path): return jsonify({'error': 'File not found'}), 404
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f: content = f.read()
        return jsonify({'content': content, 'size': os.path.getsize(file_path)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<server_id>/save', methods=['POST'])
@admin_required
def save_file_content(server_id):
    if server_id not in SERVERS: return jsonify({'error': 'Server not found'}), 404
    data = request.get_json() or request.form
    filename = data.get('filename', ''); subpath = data.get('path', ''); content = data.get('content', '')
    base_path = SERVERS[server_id]['path']
    file_path = os.path.normpath(os.path.join(base_path, subpath, filename))
    if not os.path.realpath(file_path).startswith(os.path.realpath(base_path)): return jsonify({'error': 'Invalid path'}), 400
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f: f.write(content)
        log_activity("File Save", f"Saved '{filename}' in '{server_id}'", "admin")
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<server_id>/create', methods=['POST'])
@admin_required
def create_file_api(server_id):
    if server_id not in SERVERS: return jsonify({'error': 'Server not found'}), 404
    data = request.get_json() or request.form
    filename = data.get('filename', ''); subpath = data.get('path', ''); content = data.get('content', '')
    base_path = SERVERS[server_id]['path']
    file_path = os.path.normpath(os.path.join(base_path, subpath, filename))
    if not os.path.realpath(file_path).startswith(os.path.realpath(base_path)): return jsonify({'error': 'Invalid path'}), 400
    if os.path.exists(file_path): return jsonify({'error': 'File already exists'}), 400
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f: f.write(content)
        log_activity("File Create", f"Created '{filename}' in '{server_id}'", "admin")
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<server_id>/mkdir', methods=['POST'])
@admin_required
def create_folder(server_id):
    if server_id not in SERVERS: return jsonify({'error': 'Server not found'}), 404
    data = request.get_json() or request.form
    name = data.get('name', ''); subpath = data.get('path', '')
    base_path = SERVERS[server_id]['path']
    target = os.path.normpath(os.path.join(base_path, subpath, name))
    if not os.path.realpath(target).startswith(os.path.realpath(base_path)): return jsonify({'error': 'Invalid path'}), 400
    os.makedirs(target, exist_ok=True)
    return jsonify({'status': 'ok'})

@app.route('/api/files/<server_id>/rename', methods=['POST'])
@admin_required
def rename_file(server_id):
    if server_id not in SERVERS: return jsonify({'error': 'Server not found'}), 404
    data = request.get_json() or request.form
    old_name = data.get('old_name', ''); new_name = data.get('new_name', ''); subpath = data.get('path', '')
    base_path = SERVERS[server_id]['path']
    old_path = os.path.normpath(os.path.join(base_path, subpath, old_name))
    new_path = os.path.normpath(os.path.join(base_path, subpath, new_name))
    if not os.path.realpath(old_path).startswith(os.path.realpath(base_path)): return jsonify({'error': 'Invalid path'}), 400
    if not os.path.exists(old_path): return jsonify({'error': 'File not found'}), 404
    os.rename(old_path, new_path)
    return jsonify({'status': 'ok'})

@app.route('/api/files/<server_id>/delete', methods=['POST'])
@admin_required
def delete_file(server_id):
    if server_id not in SERVERS: return jsonify({'error': 'Server not found'}), 404
    data = request.get_json() or request.form
    filename = data.get('filename', ''); subpath = data.get('path', '')
    base_path = SERVERS[server_id]['path']
    file_path = os.path.normpath(os.path.join(base_path, subpath, filename))
    if not os.path.realpath(file_path).startswith(os.path.realpath(base_path)): return jsonify({'error': 'Invalid path'}), 400
    if os.path.isdir(file_path): shutil.rmtree(file_path)
    else: os.remove(file_path)
    log_activity("Delete File", f"Deleted '{filename}' from '{server_id}'", "admin")
    return jsonify({'status': 'ok'})

@app.route('/api/files/<server_id>/upload', methods=['POST'])
@admin_required
def upload_file(server_id):
    if server_id not in SERVERS: return jsonify({'error': 'Server not found'}), 404
    subpath = request.form.get('path', '')
    file = request.files.get('file')
    if not file or not file.filename: return jsonify({'error': 'No file provided'}), 400
    base_path = SERVERS[server_id]['path']
    target_dir = os.path.normpath(os.path.join(base_path, subpath)) if subpath else base_path
    if not os.path.realpath(target_dir).startswith(os.path.realpath(base_path)): return jsonify({'error': 'Invalid path'}), 400
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, file.filename)
    file.save(file_path)
    msg = 'File uploaded successfully'
    if file.filename.lower().endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as z: z.extractall(target_dir)
        msg = 'ZIP extracted successfully'
    elif file.filename.lower().endswith('.7z'):
        with py7zr.SevenZipFile(file_path, mode='r') as z: z.extractall(target_dir)
        msg = '7Z extracted successfully'
    log_activity("File Upload", f"Uploaded '{file.filename}' to '{server_id}'", "admin")
    return jsonify({'status': 'ok', 'message': msg})

@app.route('/api/files/<server_id>/download')
@admin_required
def download_file(server_id):
    if server_id not in SERVERS: return jsonify({'error': 'Server not found'}), 404
    import io
    filename = request.args.get('filename', ''); subpath = request.args.get('path', '')
    base_path = SERVERS[server_id]['path']
    file_path = os.path.normpath(os.path.join(base_path, subpath, filename))
    if not os.path.realpath(file_path).startswith(os.path.realpath(base_path)): return jsonify({'error': 'Invalid path'}), 400
    if not os.path.exists(file_path): return jsonify({'error': 'File not found'}), 404
    if os.path.isdir(file_path):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(file_path):
                for f in files:
                    abs_path = os.path.join(root, f)
                    arcname = os.path.relpath(abs_path, os.path.dirname(file_path))
                    zf.write(abs_path, arcname)
        zip_buffer.seek(0)
        return send_file(zip_buffer, as_attachment=True, download_name=filename+'.zip', mimetype='application/zip')
    return send_file(file_path, as_attachment=True)

@app.route('/api/files/<server_id>/extract', methods=['POST'])
@admin_required
def extract_archive(server_id):
    if server_id not in SERVERS: return jsonify({'error': 'Server not found'}), 404
    data = request.get_json() or request.form
    filename = data.get('filename', ''); subpath = data.get('path', '')
    base_path = SERVERS[server_id]['path']
    archive_path = os.path.normpath(os.path.join(base_path, subpath, filename))
    if not os.path.exists(archive_path): return jsonify({'error': 'Archive not found'}), 404
    extract_to = os.path.dirname(archive_path)
    try:
        if filename.lower().endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as z: z.extractall(extract_to)
        elif filename.lower().endswith('.7z'):
            with py7zr.SevenZipFile(archive_path, mode='r') as z: z.extractall(extract_to)
        else: return jsonify({'error': 'Unsupported format'}), 400
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# PACKAGE MANAGER (ADMIN ONLY)
# =============================================================================

@app.route('/api/packages/<server_id>/install', methods=['POST'])
@admin_required
def install_package(server_id):
    if server_id not in SERVERS: return jsonify({'error': 'Server not found'}), 404
    data = request.get_json() or request.form
    pkg_type = data.get('type', 'pip'); pkg_name = data.get('name', '').strip()
    if not pkg_name: return jsonify({'error': 'Package name required'}), 400
    commands = {'pip': f"pip install {pkg_name}", 'npm': f"npm install {pkg_name}", 'apt': f"apt install -y {pkg_name}", 'pkg': f"pkg install -y {pkg_name}", 'gem': f"gem install {pkg_name}"}
    cmd = commands.get(pkg_type, f"pip install {pkg_name}")
    SERVERS[server_id]['logs'].append(f">>> [FX HOSTING] Installing {pkg_name} via {pkg_type}...")
    def run_install():
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in iter(process.stdout.readline, ''):
                if line: SERVERS[server_id]['logs'].append(line.strip())
            SERVERS[server_id]['logs'].append(f">>> [FX HOSTING] Installation of {pkg_name} completed.")
        except Exception as e:
            SERVERS[server_id]['logs'].append(f">>> [FX HOSTING] Install error: {str(e)}")
    threading.Thread(target=run_install, daemon=True).start()
    log_activity("Package Install", f"Installed '{pkg_name}' ({pkg_type}) on '{server_id}'", "admin")
    return jsonify({'status': 'ok'})

@app.route('/api/packages/<server_id>/uninstall', methods=['POST'])
@admin_required
def uninstall_package(server_id):
    if server_id not in SERVERS: return jsonify({'error': 'Server not found'}), 404
    data = request.get_json() or request.form
    pkg_type = data.get('type', 'pip'); pkg_name = data.get('name', '').strip()
    if not pkg_name: return jsonify({'error': 'Package name required'}), 400
    commands = {'pip': f"pip uninstall -y {pkg_name}", 'npm': f"npm uninstall {pkg_name}", 'apt': f"apt remove -y {pkg_name}"}
    cmd = commands.get(pkg_type, f"pip uninstall -y {pkg_name}")
    SERVERS[server_id]['logs'].append(f">>> [FX HOSTING] Uninstalling {pkg_name}...")
    def run_uninst():
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in iter(process.stdout.readline, ''):
                if line: SERVERS[server_id]['logs'].append(line.strip())
            SERVERS[server_id]['logs'].append(f">>> [FX HOSTING] Uninstallation complete.")
        except Exception as e:
            SERVERS[server_id]['logs'].append(f">>> [FX HOSTING] Uninstall error: {str(e)}")
    threading.Thread(target=run_uninst, daemon=True).start()
    return jsonify({'status': 'ok'})

@app.route('/api/packages/<server_id>/list')
@admin_required
def list_packages(server_id):
    if server_id not in SERVERS: return jsonify({'error': 'Server not found'}), 404
    pkg_type = request.args.get('type', 'pip')
    commands = {'pip': "pip list --format=json", 'npm': "npm list --depth=0 --json", 'apt': "apt list --installed 2>/dev/null | head -50"}
    cmd = commands.get(pkg_type, "pip list --format=json")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return jsonify({'output': result.stdout[:5000] or 'No packages found'})
    except:
        return jsonify({'output': 'Failed to list packages'})

# =============================================================================
# BACKUP MANAGER (ADMIN ONLY)
# =============================================================================

@app.route('/api/backup/<server_id>/create', methods=['POST'])
@admin_required
def create_backup(server_id):
    if server_id not in SERVERS: return jsonify({'error': 'Server not found'}), 404
    try:
        backup_dir = os.path.join(BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        backup_name = f"{server_id}_{timestamp}.zip"
        backup_path = os.path.join(backup_dir, backup_name)
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(SERVERS[server_id]['path']):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, SERVERS[server_id]['path'])
                    zf.write(file_path, arcname)
        log_activity("Backup", f"Created backup '{backup_name}' for '{server_id}'", "admin")
        return jsonify({'status': 'ok', 'backup_name': backup_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backup/<server_id>/restore', methods=['POST'])
@admin_required
def restore_backup(server_id):
    if server_id not in SERVERS: return jsonify({'error': 'Server not found'}), 404
    data = request.get_json() or request.form
    backup_name = os.path.basename(data.get('backup_name', ''))
    backup_path = os.path.join(BASE_DIR, 'backups', backup_name)
    if not os.path.exists(backup_path): return jsonify({'error': 'Backup not found'}), 404
    try:
        if SERVERS[server_id].get('status') == 'running' and SERVERS[server_id].get('process'):
            kill_process_completely(SERVERS[server_id]['process'])
            SERVERS[server_id]['process'] = None
            SERVERS[server_id]['status'] = 'stopped'
        if os.path.exists(SERVERS[server_id]['path']): shutil.rmtree(SERVERS[server_id]['path'])
        os.makedirs(SERVERS[server_id]['path'], exist_ok=True)
        with zipfile.ZipFile(backup_path, 'r') as zf: zf.extractall(SERVERS[server_id]['path'])
        log_activity("Restore", f"Restored backup '{backup_name}' to '{server_id}'", "admin")
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backup/list')
@login_required
def list_backups():
    backup_dir = os.path.join(BASE_DIR, 'backups')
    if not os.path.exists(backup_dir): return jsonify({'backups': []})
    backups = []
    for f in sorted(os.listdir(backup_dir), reverse=True):
        if f.endswith('.zip'):
            fpath = os.path.join(backup_dir, f)
            size = os.path.getsize(fpath)
            size_str = f"{size/1024:.1f} KB" if size < 1024**2 else f"{size/(1024**2):.1f} MB"
            backups.append({'name': f, 'size': size_str, 'date': time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(fpath)))})
    return jsonify({'backups': backups})

@app.route('/api/backup/delete', methods=['POST'])
@admin_required
def delete_backup():
    data = request.get_json() or request.form
    backup_name = data.get('backup_name', '').replace('..', '')
    backup_path = os.path.join(BASE_DIR, 'backups', backup_name)
    if os.path.exists(backup_path): os.remove(backup_path); return jsonify({'status': 'ok'})
    return jsonify({'error': 'Backup not found'}), 404

# =============================================================================
# TERMINAL (ADMIN ONLY)
# =============================================================================

@app.route('/api/terminal/execute', methods=['POST'])
@admin_required
def terminal_execute():
    data = request.get_json() or request.form
    command = data.get('command', '').strip()
    cwd = data.get('cwd', None)
    if not command: return jsonify({'error': 'No command provided'}), 400
    dangerous = ['rm -rf /', 'mkfs', 'dd if=/dev/zero', ':(){:|:&};:', '> /dev/sda']
    for d in dangerous:
        if d in command:
            return jsonify({'output': f'\x1b[31mBlocked: dangerous command detected ({d})\x1b[0m', 'returncode': 403, 'cwd': cwd or BASE_DIR})
    work_dir = cwd if (cwd and os.path.isdir(cwd)) else BASE_DIR
    if command.startswith('cd ') or command == 'cd':
        target = command[3:].strip() if command != 'cd' else os.path.expanduser('~')
        target = os.path.expanduser(target)
        if not os.path.isabs(target): target = os.path.normpath(os.path.join(work_dir, target))
        if os.path.isdir(target): return jsonify({'output': '', 'returncode': 0, 'cwd': target})
        else: return jsonify({'output': f'cd: {target}: No such file or directory', 'returncode': 1, 'cwd': work_dir})
    try:
        result = subprocess.run(command, shell=True, cwd=work_dir, capture_output=True, text=True, timeout=60, env={**os.environ, 'TERM': 'xterm-256color'})
        output = result.stdout + result.stderr
        log_activity("Terminal", f"CMD: {command[:80]}", "admin")
        return jsonify({'output': output[:50000], 'returncode': result.returncode, 'cwd': work_dir})
    except subprocess.TimeoutExpired:
        return jsonify({'output': 'Command timed out (60s)', 'returncode': -1, 'cwd': work_dir})
    except Exception as e:
        return jsonify({'output': str(e), 'returncode': -1, 'cwd': work_dir})

@app.route('/api/terminal/autocomplete', methods=['POST'])
@admin_required
def terminal_autocomplete():
    data = request.get_json() or {}
    prefix = data.get('prefix', ''); cwd = data.get('cwd', BASE_DIR)
    try:
        if not os.path.isdir(cwd): cwd = BASE_DIR
        parts = prefix.split('/'); partial = parts[-1]; parent = '/'.join(parts[:-1]) if len(parts) > 1 else ''
        search_dir = os.path.join(cwd, parent) if parent else cwd
        if not os.path.isdir(search_dir): search_dir = cwd
        matches = []
        for item in os.listdir(search_dir):
            if item.startswith(partial):
                full = (parent + '/' + item) if parent else item
                if os.path.isdir(os.path.join(search_dir, item)): full += '/'
                matches.append(full)
        return jsonify({'matches': sorted(matches)[:20]})
    except:
        return jsonify({'matches': []})

# =============================================================================
# PROCESS KILLER (ADMIN ONLY)
# =============================================================================

@app.route('/api/system/kill_process', methods=['POST'])
@admin_required
def kill_system_process():
    data = request.get_json() or request.form
    pid = data.get('pid')
    try:
        pid_int = int(pid)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid PID'}), 400
    try:
        p = psutil.Process(pid_int)
        p.kill()
        log_activity("Process Kill", f"Killed PID {pid_int}", "admin")
        return jsonify({'status': 'ok'})
    except psutil.NoSuchProcess:
        return jsonify({'error': f'No such process: PID {pid_int} (already stopped?)'}), 404
    except psutil.AccessDenied:
        return jsonify({'error': f'Access denied: cannot kill PID {pid_int} (permission issue)'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# BULK OPERATIONS (ADMIN ONLY)
# =============================================================================

@app.route('/api/bulk/upload', methods=['POST'])
@admin_required
def bulk_upload():
    file = request.files.get('file')
    if not file or not file.filename: return jsonify({'error': 'No file provided'}), 400
    results = {}; file_bytes = file.read(); filename = file.filename
    for server_id, server in SERVERS.items():
        try:
            base_path = server.get('path', '')
            if not base_path or not os.path.exists(base_path):
                results[server_id] = {'status': 'error', 'message': 'Path not found'}; continue
            file_path = os.path.join(base_path, filename)
            with open(file_path, 'wb') as f: f.write(file_bytes)
            msg = 'Uploaded'
            if filename.lower().endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as z: z.extractall(base_path); msg = 'ZIP extracted'
            results[server_id] = {'status': 'ok', 'message': msg}
        except Exception as e:
            results[server_id] = {'status': 'error', 'message': str(e)}
    log_activity("Bulk Upload", f"File '{filename}' uploaded to {len(SERVERS)} servers", "admin")
    return jsonify({'status': 'ok', 'results': results, 'total': len(SERVERS)})

@app.route('/api/bulk/start_command', methods=['POST'])
@admin_required
def bulk_start_command():
    data = request.get_json() or request.form
    cmd = data.get('command', '').strip()
    if not cmd: return jsonify({'error': 'No command provided'}), 400
    results = {}
    for server_id in SERVERS:
        try: SERVERS[server_id]['cmd'] = cmd; results[server_id] = {'status': 'ok'}
        except Exception as e: results[server_id] = {'status': 'error', 'message': str(e)}
    save_servers()
    return jsonify({'status': 'ok', 'results': results, 'total': len(SERVERS)})

@app.route('/api/bulk/action', methods=['POST'])
@admin_required
def bulk_action():
    """Start/Stop/Restart ALL servers at once"""
    data = request.get_json() or request.form
    action = data.get('action', '')
    server_ids = data.get('server_ids', list(SERVERS.keys()))
    results = {}
    for server_id in server_ids:
        if server_id not in SERVERS: continue
        server = SERVERS[server_id]
        try:
            if action == 'start':
                start_server_internal(server_id, server); results[server_id] = 'started'
            elif action == 'stop':
                if server['process']: kill_process_completely(server['process'])
                server['process'] = None; server['status'] = 'stopped'; results[server_id] = 'stopped'
            elif action == 'restart':
                if server['process']: kill_process_completely(server['process'])
                server['process'] = None; server['status'] = 'stopped'
                time.sleep(0.3); start_server_internal(server_id, server); results[server_id] = 'restarted'
        except Exception as e:
            results[server_id] = f'error: {str(e)}'
    save_servers()
    log_activity(f"Bulk {action.title()}", f"Action on {len(results)} servers", "admin")
    return jsonify({'status': 'ok', 'results': results})

# =============================================================================
# SETTINGS (ADMIN ONLY for write)
# =============================================================================

@app.route('/api/settings', methods=['POST'])
@admin_required
def settings_update():
    global CONFIG
    data = request.get_json() or request.form
    CONFIG['site_title'] = data.get('site_title', CONFIG['site_title'])
    CONFIG['site_header'] = data.get('site_header', CONFIG['site_header'])
    CONFIG['icon_url'] = data.get('icon_url', CONFIG['icon_url'])
    CONFIG['theme'] = data.get('theme', CONFIG['theme'])
    CONFIG['font_family'] = data.get('font_family', CONFIG.get('font_family', 'terminal'))
    CONFIG['terminal_height'] = int(data.get('terminal_height', CONFIG.get('terminal_height', 300)))
    CONFIG['auto_refresh'] = data.get('auto_refresh', 'true') == 'true'
    CONFIG['notifications'] = data.get('notifications', 'true') == 'true'
    CONFIG['show_system_stats'] = data.get('show_system_stats', 'true') == 'true'
    save_json(CONFIG_FILE, CONFIG)
    log_activity("Settings", "Application settings updated", "admin")
    return jsonify({'status': 'ok'})

@app.route('/api/settings/password', methods=['POST'])
@login_required
def change_password_api():
    global CONFIG
    data = request.get_json() or request.form
    current = data.get('current', ''); new_pass = data.get('new', '')
    hashed_current = hashlib.sha256(current.encode()).hexdigest()
    target = data.get('target', 'user')
    if target == 'secret' and not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    if hashed_current != CONFIG['passwords'].get(target, ''):
        return jsonify({'error': 'Current password incorrect'}), 400
    CONFIG['passwords'][target] = hashlib.sha256(new_pass.encode()).hexdigest()
    save_json(CONFIG_FILE, CONFIG)
    log_activity("Password Change", f"{target} password changed", get_current_role())
    return jsonify({'status': 'ok'})

# =============================================================================
# TELEGRAM BOT DEPLOY (ADMIN ONLY)
# =============================================================================

@app.route('/api/telegram/deploy', methods=['POST'])
@admin_required
def deploy_telegram_bot():
    data = request.get_json() or request.form
    bot_token = data.get('token', '').strip()
    bot_name = data.get('name', 'TelegramBot').strip().replace(' ', '_')
    if not bot_token or ':' not in bot_token: return jsonify({'error': 'Invalid bot token'}), 400
    if bot_name in SERVERS: return jsonify({'error': 'Server name already exists'}), 400
    server_path = os.path.join(UPLOAD_FOLDER, bot_name)
    os.makedirs(server_path, exist_ok=True)
    bot_code = f'''#!/usr/bin/env python3
"""Telegram Bot - Auto Generated by FX HOSTING"""
import asyncio, logging, sys
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = "{bot_token}"
router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("<b>FX HOSTING Bot\\n\\n/start /help /ping /status</b>", parse_mode=ParseMode.HTML)

@router.message(Command("ping"))
async def cmd_ping(message: types.Message):
    import time
    start = time.time()
    msg = await message.answer("Pinging...")
    elapsed = (time.time() - start) * 1000
    await msg.edit_text(f"<b>Pong!</b>\\nLatency: {{elapsed:.1f}}ms", parse_mode=ParseMode.HTML)

@router.message(Command("status"))
async def cmd_status(message: types.Message):
    import psutil
    cpu = psutil.cpu_percent(interval=0.5); ram = psutil.virtual_memory().percent; disk = psutil.disk_usage('/').percent
    await message.answer(f"<b>System Status</b>\\nCPU: {{cpu}}%\\nRAM: {{ram}}%\\nDisk: {{disk}}%", parse_mode=ParseMode.HTML)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
'''
    with open(os.path.join(server_path, 'bot.py'), 'w') as f: f.write(bot_code)
    SERVERS[bot_name] = {
        'process': None, 'cmd': 'python3 bot.py', 'cwd': '',
        'logs': [f">>> [FX HOSTING] Telegram bot '{bot_name}' created"], 'auto_restart': True,
        'restart_interval': '1h', 'last_start_time': 0, 'status': 'stopped', 'path': server_path,
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'), 'notes': f'Token: {bot_token[:10]}...',
        'group': 'Telegram Bots', 'tags': ['telegram', 'bot'], 'env_vars': {}
    }
    save_servers()
    log_activity("Telegram Bot", f"Deployed bot '{bot_name}'", "admin")
    return jsonify({'status': 'ok', 'server_id': bot_name})

# =============================================================================
# ROLE INFO API
# =============================================================================

@app.route('/api/whoami')
@login_required
def whoami():
    return jsonify({
        'role': 'admin' if session.get('is_admin') else 'user',
        'username': session.get('username', 'unknown'),
        'is_admin': session.get('is_admin', False),
        'login_time': session.get('login_time', 0),
        'permissions': {
            'view_servers': True,
            'view_logs': True,
            'view_stats': True,
            'start_stop_servers': session.get('is_admin', False),
            'manage_files': session.get('is_admin', False),
            'terminal': session.get('is_admin', False),
            'settings': session.get('is_admin', False),
            'backup': session.get('is_admin', False),
            'packages': session.get('is_admin', False),
            'delete_servers': session.get('is_admin', False),
        }
    })

# =============================================================================
# MULTI-USER MANAGEMENT API (ADMIN ONLY)
# =============================================================================

@app.route('/api/users', methods=['GET'])
@admin_required
def list_users():
    safe_users = {}
    for uid, u in USERS.items():
        safe_users[uid] = {
            'username': u.get('username'), 'role': u.get('role'),
            'created_at': u.get('created_at'), 'is_builtin': u.get('is_builtin', False)
        }
    return jsonify({'users': safe_users})

@app.route('/api/users/create', methods=['POST'])
@admin_required
def create_user():
    data = request.get_json() or request.form
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', 'user').strip()
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    if role not in ('admin', 'user'):
        return jsonify({'error': 'Invalid role'}), 400
    if len(password) < 4:
        return jsonify({'error': 'Password must be at least 4 characters'}), 400
    for u in USERS.values():
        if u.get('username', '').lower() == username.lower():
            return jsonify({'error': 'Username already exists'}), 400
    uid = f"u_{secrets.token_hex(6)}"
    USERS[uid] = {
        'username': username,
        'password_hash': hashlib.sha256(password.encode()).hexdigest(),
        'role': role,
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'is_builtin': False
    }
    save_users(USERS)
    log_activity("User Create", f"Created {role} user '{username}'", "admin")
    return jsonify({'status': 'ok', 'user_id': uid})

@app.route('/api/users/<user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    if user_id not in USERS:
        return jsonify({'error': 'User not found'}), 404
    if USERS[user_id].get('is_builtin'):
        return jsonify({'error': 'Cannot delete built-in user'}), 400
    username = USERS[user_id].get('username')
    del USERS[user_id]
    save_users(USERS)
    log_activity("User Delete", f"Deleted user '{username}'", "admin")
    return jsonify({'status': 'ok'})

@app.route('/api/users/<user_id>/password', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    if user_id not in USERS:
        return jsonify({'error': 'User not found'}), 404
    data = request.get_json() or request.form
    new_pass = data.get('password', '').strip()
    if len(new_pass) < 4:
        return jsonify({'error': 'Password must be at least 4 characters'}), 400
    USERS[user_id]['password_hash'] = hashlib.sha256(new_pass.encode()).hexdigest()
    save_users(USERS)
    log_activity("User Password Reset", f"Reset password for '{USERS[user_id].get('username')}'", "admin")
    return jsonify({'status': 'ok'})

# =============================================================================
# DOMAIN / SUBDOMAIN MAPPING API
# =============================================================================

@app.route('/api/domains', methods=['GET'])
@login_required
def list_domains():
    return jsonify({'domains': DOMAINS})

@app.route('/api/domains/<server_id>', methods=['POST'])
@admin_required
def set_domain(server_id):
    if server_id not in SERVERS:
        return jsonify({'error': 'Server not found'}), 404
    data = request.get_json() or request.form
    domain = data.get('domain', '').strip().lower()
    port = data.get('port', '').strip()
    ssl = data.get('ssl', False)
    if not domain:
        return jsonify({'error': 'Domain required'}), 400
    if not re.match(r'^[a-z0-9]([a-z0-9\-\.]*[a-z0-9])?$', domain):
        return jsonify({'error': 'Invalid domain format'}), 400
    if not port.isdigit():
        return jsonify({'error': 'Port must be a number'}), 400
    DOMAINS[server_id] = {
        'domain': domain, 'port': int(port), 'ssl': bool(ssl),
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    save_domains(DOMAINS)
    log_activity("Domain Map", f"Mapped '{domain}' -> '{server_id}:{port}'", "admin")
    return jsonify({'status': 'ok', 'nginx_config': generate_nginx_config(domain, int(port), bool(ssl))})

@app.route('/api/domains/<server_id>/delete', methods=['POST'])
@admin_required
def delete_domain(server_id):
    if server_id in DOMAINS:
        del DOMAINS[server_id]
        save_domains(DOMAINS)
        return jsonify({'status': 'ok'})
    return jsonify({'error': 'Domain mapping not found'}), 404

def generate_nginx_config(domain, port, ssl=False):
    if ssl:
        return f"""server {{
    listen 80;
    server_name {domain};
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name {domain};

    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;

    location / {{
        proxy_pass http://127.0.0.1:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}
}}

# To enable SSL run: certbot --nginx -d {domain}"""
    return f"""server {{
    listen 80;
    server_name {domain};

    location / {{
        proxy_pass http://127.0.0.1:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}
}}

# To enable SSL run: certbot --nginx -d {domain}"""

@app.route('/api/domains/<server_id>/nginx_config')
@admin_required
def get_nginx_config(server_id):
    if server_id not in DOMAINS:
        return jsonify({'error': 'No domain mapped'}), 404
    d = DOMAINS[server_id]
    return jsonify({'config': generate_nginx_config(d['domain'], d['port'], d.get('ssl', False))})

# =============================================================================
# SERVER HEALTH SCORE API
# =============================================================================

@app.route('/api/health/<server_id>')
@login_required
def get_health(server_id):
    if server_id not in SERVERS:
        return jsonify({'error': 'Server not found'}), 404
    return jsonify(compute_health_score(server_id))

@app.route('/api/health/all')
@login_required
def get_all_health():
    result = {}
    for sid in SERVERS:
        result[sid] = compute_health_score(sid)
    return jsonify({'health': result})

# =============================================================================
# RESOURCE HISTORY API (per-server CPU/RAM graphs)
# =============================================================================

@app.route('/api/resource_history/<server_id>')
@login_required
def get_resource_history(server_id):
    return jsonify({'history': RESOURCE_HISTORY.get(server_id, [])})

# =============================================================================
# WEBHOOK SETTINGS API (ADMIN ONLY)
# =============================================================================

@app.route('/api/webhooks', methods=['GET'])
@admin_required
def get_webhooks():
    wh = CONFIG.get('webhooks', {}).copy()
    # Mask tokens partially for display safety
    if wh.get('discord_url'):
        wh['discord_url_masked'] = wh['discord_url'][:40] + '...' if len(wh['discord_url']) > 40 else wh['discord_url']
    return jsonify(wh)

@app.route('/api/webhooks', methods=['POST'])
@admin_required
def update_webhooks():
    global CONFIG
    data = request.get_json() or request.form
    wh = CONFIG.setdefault('webhooks', {})
    for key in ['discord_url', 'telegram_bot_token', 'telegram_chat_id']:
        if key in data:
            wh[key] = data.get(key, '').strip()
    for key in ['notify_on_crash', 'notify_on_start', 'notify_on_stop', 'notify_on_high_cpu']:
        if key in data:
            wh[key] = data.get(key) in (True, 'true', 'True', 1, '1')
    for key in ['cpu_alert_threshold', 'ram_alert_threshold']:
        if key in data:
            try: wh[key] = int(data.get(key))
            except: pass
    save_json(CONFIG_FILE, CONFIG)
    log_activity("Webhook Settings", "Webhook configuration updated", "admin")
    return jsonify({'status': 'ok'})

@app.route('/api/webhooks/test', methods=['POST'])
@admin_required
def test_webhook():
    data = request.get_json() or request.form
    wh_type = data.get('type', 'discord')
    if wh_type == 'discord':
        send_discord_webhook("🧪 Test Notification", "This is a test message from FX HOSTING Panel. Your Discord webhook is working!", 0x00ff00)
    else:
        send_telegram_webhook("🧪 Test Notification\n\nThis is a test message from FX HOSTING Panel. Your Telegram webhook is working!")
    return jsonify({'status': 'ok', 'message': f'{wh_type} test notification sent'})

# =============================================================================
# STATIC FILES & ERRORS
# =============================================================================

@app.route('/static/<path:filename>')
def serve_static(filename):
    try: return send_file(os.path.join(STATIC_FOLDER, filename))
    except: return "File not found", 404

@app.errorhandler(404)
def not_found(e): return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e): return jsonify({'error': 'Internal server error'}), 500

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   FX HOSTING v4.0.0 - Admin/User Role System            ║
    ║   ADMIN: Full access | USER: View-only (servers/logs)   ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    print(f"[FX HOSTING] Server started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("[FX HOSTING] Panel running on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
