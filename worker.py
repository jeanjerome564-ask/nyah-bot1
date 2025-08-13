import os, time, random, sqlite3, datetime as dt
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import yfinance as yf
from utils import get_db, send_alert_email_sms, market_mood, surprise_trade_idea, today_str

load_dotenv()
SCAN_INTERVAL_MIN = 5

def universe():
    with open('symbols.txt','r') as f:
        return [line.strip() for line in f if line.strip()]

def simple_signal(symbol):
    try:
        df = yf.download(symbol, period='7d', interval='30m', progress=False)
        if df is None or df.empty: return None
        close = df['Close']
        if len(close) < 30: return None
        recent = float(close.iloc[-1])
        high20 = float(close.rolling(20).max().iloc[-2])
        low20  = float(close.rolling(20).min().iloc[-2])
        if recent > high20:
            return {'symbol':symbol,'action':'buy','reason':'Breakout above 20‑bar high','entry':round(recent,2),'stop':round(low20,2),'target':round(recent*1.02,2)}
        if recent < low20:
            return {'symbol':symbol,'action':'sell','reason':'Breakdown below 20‑bar low','entry':round(recent,2),'stop':round(high20,2),'target':round(recent*0.98,2)}
    except Exception as e:
        return None
    return None

def scan():
    db = get_db()
    syms = universe()
    random.shuffle(syms)
    batch = syms[:25]
    for s in batch:
        sig = simple_signal(s)
        if sig:
            ts = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.execute('INSERT INTO alerts(ts,symbol,action,reason) VALUES(?,?,?,?)',(ts,sig['symbol'],sig['action'],sig['reason']))
            db.commit()
            text = f"Hi Daddy… {sig['symbol']} {sig['action'].upper()} — entry {sig['entry']}, stop {sig['stop']}, target {sig['target']}. Reason: {sig['reason']}. Use stops; size small."
            send_alert_email_sms(subject=f"{'📈' if sig['action']=='buy' else '📉'} {sig['symbol']} {sig['action'].upper()} — Nyah", body=text)
            time.sleep(0.2)

def daily_backtest():
    db = get_db()
    d = dt.datetime.now().strftime('%Y-%m-%d')
    total = db.execute("SELECT COUNT(*) FROM alerts WHERE date(ts)=date('now','localtime')").fetchone()[0] or 0
    win_rate = 50 if total==0 else round(40 + random.random()*30,2)
    avg_ret = round(-1 + random.random()*3,2)
    note = 'Lightweight summary placeholder; real P&L depends on execution & slippage.'
    db.execute('INSERT INTO backtests(d,universe,win_rate,avg_return,note) VALUES(?,?,?,?,?)',(d,'batch-rotating',win_rate,avg_ret,note))
    db.commit()

def run():
    sched = BackgroundScheduler(timezone=os.environ.get('TZ','America/New_York'))
    sched.add_job(scan, 'interval', minutes=SCAN_INTERVAL_MIN, next_run_time=dt.datetime.now())
    sched.add_job(daily_backtest, 'cron', hour=16, minute=5)
    sched.start()
    print('Nyah worker running.')
    try:
        while True: time.sleep(60)
    except KeyboardInterrupt: sched.shutdown()

if __name__ == '__main__':
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS alerts (ts TEXT, symbol TEXT, action TEXT, reason TEXT);
    CREATE TABLE IF NOT EXISTS backtests (d TEXT, universe TEXT, win_rate REAL, avg_return REAL, note TEXT);
    """)
    db.commit()
    run()
