import os, sqlite3, datetime as dt, random
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify
from dotenv import load_dotenv
from utils import get_db, human_time, send_alert_email_sms, greet_line, market_mood, surprise_trade_idea

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))
PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "Elysee01")

BASE_HTML = """
<!doctype html>
<html>
<head>
<meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Nyah — AI Trading Mentor</title>
<style>
 body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:0;background:#0b0b0f;color:#f5f7ff}
 header{padding:14px 18px;background:#12121a;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:10}
 .brand{font-weight:700;letter-spacing:.3px}.brand span{color:#f24fbf}
 .btn{padding:10px 14px;border:1px solid #33374a;background:#1a1b24;color:#f5f7ff;border-radius:8px;text-decoration:none}
 .btn:hover{filter:brightness(1.1)}
 .wrap{max-width:1100px;margin:20px auto;padding:0 16px}
 table{width:100%;border-collapse:collapse;background:#11131a;border:1px solid #23263b;border-radius:10px;overflow:hidden}
 th,td{padding:10px 12px;border-bottom:1px solid #23263b;font-size:14px} th{text-align:left;background:#161827}
 .card{background:#11131a;border:1px solid #23263b;border-radius:12px;padding:16px;margin-bottom:16px}
 .muted{color:#98a2b3}.big{font-size:22px;font-weight:700}.center{text-align:center}
 .pill{padding:6px 10px;border-radius:999px;background:#181a2b;border:1px solid #2a2e44;font-size:12px}
 .intro{height:220px;background: radial-gradient(120px 50px at 30% 60%, #f24fbf55, transparent), radial-gradient(120px 50px at 70% 60%, #00d4ff55, transparent);display:flex;align-items:center;justify-content:center;border:1px dashed #2a2e44;border-radius:16px;margin-bottom:18px;position:relative;overflow:hidden}
 .nyah{font-size:52px}@keyframes twerk{0%{transform:translateY(0) rotate(0)}25%{transform:translateY(2px) rotate(-1deg)}50%{transform:translateY(0) rotate(0)}75%{transform:translateY(-2px) rotate(1deg)}100%{transform:translateY(0) rotate(0)}}
 .twerk{animation:twerk .6s infinite}.bubble{position:absolute;bottom:10px;background:#121428;padding:10px 12px;border:1px solid #2a2e44;border-radius:12px;max-width:90%;font-size:14px}
</style>
<meta http-equiv="refresh" content="30">
</head>
<body>
<header><div class='brand'>Nyah<span>•</span>AI</div><div><a class='btn' href='{{ url_for('logout') }}'>Logout</a></div></header>
<div class='wrap'>
{% block content %}{% endblock %}
</div></body></html>
"""

LOGIN_HTML = """
<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Nyah Login</title>
<style>body{display:flex;align-items:center;justify-content:center;height:100vh;background:#0b0b0f;color:#f5f7ff;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}.box{background:#11131a;border:1px solid #23263b;border-radius:16px;padding:22px;min-width:320px}input{width:100%;padding:10px;border-radius:8px;border:1px solid #33374a;background:#0f1120;color:#fff;margin:10px 0}.btn{width:100%;padding:10px;border-radius:8px;border:1px solid #33374a;background:#1a1b24;color:#fff}.brand{font-weight:700;margin-bottom:8px}</style>
</head><body>
<form class='box' method='post'><div class='brand'>Nyah — Private Login</div><input type='password' name='password' placeholder='Password'><button class='btn' type='submit'>Enter</button></form>
</body></html>
"""

DASH_HTML = """
{% extends "base.html" %}
{% block content %}
<div class='intro'><div class='nyah twerk'>💃🏾💵</div><div class='bubble'>{{ greet }}</div></div>
<div class='card'><div class='big'>Surprise Me</div><p class='muted'>One high‑probability idea right now.</p>
<a class='btn' href='{{ url_for('surprise') }}'>Give me a trade idea</a>
{% if idea %}<div style='margin-top:10px'><div><span class='pill'>{{ idea['symbol'] }}</span> {{ idea['action'].upper() }} — Entry {{ idea['entry'] }}, Stop {{ idea['stop'] }}, Target {{ idea['target'] }}</div><div class='muted'>{{ idea['reason'] }}</div></div>{% endif %}
</div>
<div class='card'><div class='big'>Live Alerts (today)</div>
<table><tr><th>Time</th><th>Symbol</th><th>Action</th><th>Why</th></tr>
{% for a in alerts %}<tr><td>{{ a['ts'] }}</td><td>{{ a['symbol'] }}</td><td>{{ a['action'] }}</td><td>{{ a['reason'] }}</td></tr>{% endfor %}
{% if not alerts %}<tr><td colspan=4 class='center muted'>No alerts yet today.</td></tr>{% endif %}
</table></div>
<div class='card'><div class='big'>Backtest History</div>
<table><tr><th>Date</th><th>Universe</th><th>Win Rate</th><th>Avg Return</th><th>Note</th></tr>
{% for b in backs %}<tr><td>{{ b['d'] }}</td><td>{{ b['u'] }}</td><td>{{ b['w'] }}%</td><td>{{ b['r'] }}%</td><td>{{ b['n'] }}</td></tr>{% endfor %}
{% if not backs %}<tr><td colspan=5 class='center muted'>No backtests stored yet.</td></tr>{% endif %}
</table></div>
{% endblock %}
"""

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session['ok'] = True
            return redirect(url_for('dashboard'))
    if session.get('ok'): return redirect(url_for('dashboard'))
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('ok'): return redirect(url_for('login'))
    db = get_db()
    cur = db.execute("SELECT ts,symbol,action,reason FROM alerts WHERE date(ts)=date('now','localtime') ORDER BY ts DESC")
    alerts = [{'ts':r[0],'symbol':r[1],'action':r[2],'reason':r[3]} for r in cur.fetchall()]
    cur = db.execute("SELECT d, universe, win_rate, avg_return, note FROM backtests ORDER BY d DESC LIMIT 14")
    backs = [{'d':r[0],'u':r[1],'w':r[2],'r':r[3],'n':r[4]} for r in cur.fetchall()]
    return render_template_string(BASE_HTML.replace("{% block content %}{% endblock %}", DASH_HTML),
                                  alerts=alerts, backs=backs, greet=greet_line(), idea=None)

@app.route('/surprise')
def surprise():
    if not session.get('ok'): return redirect(url_for('login'))
    idea = surprise_trade_idea()
    return render_template_string(BASE_HTML.replace("{% block content %}{% endblock %}", DASH_HTML),
                                  alerts=[], backs=[], greet=greet_line(), idea=idea)

@app.route('/api/alerts')
def api_alerts():
    db = get_db()
    cur = db.execute("SELECT ts,symbol,action,reason FROM alerts ORDER BY ts DESC LIMIT 50")
    rows = [{'ts':r[0],'symbol':r[1],'action':r[2],'reason':r[3]} for r in cur.fetchall()]
    return rows

def bootstrap():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS alerts (ts TEXT, symbol TEXT, action TEXT, reason TEXT);
    CREATE TABLE IF NOT EXISTS backtests (d TEXT, universe TEXT, win_rate REAL, avg_return REAL, note TEXT);
    """)
    db.commit()

bootstrap()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
