import os, smtplib, sqlite3, datetime as dt, random
from email.message import EmailMessage
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()
DB_PATH = os.environ.get('DB_PATH','nyah.db')

def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def human_time():
    return dt.datetime.now().strftime('%Y-%m-%d %H:%M')

def today_str():
    return dt.datetime.now().strftime('%Y-%m-%d')

def market_mood():
    moods = ['bullish','bearish','neutral','volatile']
    i = (dt.datetime.now().hour // 6) % 4
    return moods[i]

def part_of_day():
    h = dt.datetime.now().hour
    if h < 12: return 'morning'
    if h < 17: return 'afternoon'
    return 'evening'

def greet_line():
    m = market_mood()
    name = 'Nile' if m in ['bullish','volatile'] else 'Daddy'
    if m == 'bullish':  return f'Good {part_of_day()}, {name}… I’m feeling bullish today. Let’s hunt winners.'
    if m == 'bearish':  return f'Good {part_of_day()}, {name}… Markets look soft. I’ve got defensive plays for you.'
    if m == 'volatile': return f'Good {part_of_day()}, {name}… Volatility is spicing things up. Eyes on momentum.'
    return f'Good {part_of_day()}, {name}… It’s quiet, but I’ve got ideas to make it move.'

def send_email(subject, body, to_addrs):
    host = os.environ.get('SMTP_HOST')
    port = int(os.environ.get('SMTP_PORT','587'))
    user = os.environ.get('SMTP_USER')
    pwd  = os.environ.get('SMTP_PASSWORD')
    if not host or not user or not pwd:
        print('SMTP not configured; printing message instead:\n', subject, body)
        return False
    msg = EmailMessage()
    msg['From'] = user
    msg['To'] = ', '.join(to_addrs) if isinstance(to_addrs,(list,tuple)) else to_addrs
    msg['Subject'] = subject
    msg.set_content(body)
    with smtplib.SMTP(host, port) as s:
        s.starttls(); s.login(user, pwd); s.send_message(msg)
    return True

def send_alert_email_sms(subject, body):
    to = [os.environ.get('ALERT_EMAIL_TO','')]
    for addr in [os.environ.get('ALERT_SMS_EMAIL_TO',''), os.environ.get('ALERT_MMS_EMAIL_TO','')]:
        if addr: to.append(addr)
    ok = send_email(subject, body, [a for a in to if a])
    if os.environ.get('USE_TWILIO','false').lower() == 'true':
        try:
            client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
            twiml = f'<Response><Say voice="Polly.Joanna">Hi Daddy. {body}</Say></Response>'
            client.calls.create(twiml=twiml, from_=os.environ['TWILIO_FROM_NUMBER'], to=os.environ.get('OWNER_PHONE_E164','+17725198965'))
        except Exception as e:
            print('Twilio call failed:', e)
    return ok

def surprise_trade_idea():
    choices = [('AAPL','buy','Breakout + momentum'),
               ('MSFT','buy','Strong trend continuation'),
               ('NVDA','buy','Pullback to support + bounce'),
               ('TSLA','sell','Breakdown risk after weak bounce'),
               ('AMZN','buy','Volume spike + RSI > 50'),
               ('META','buy','Flag breakout pattern'),
               ('AMD','buy','MACD bullish cross'),
               ('NFLX','sell','Gap fill down setup')]
    sym, act, why = random.choice(choices)
    price = round(100 + random.random()*200,2)
    return {'symbol':sym,'action':act,'entry':price,
            'stop':round(price*(0.98 if act=='buy' else 1.02),2),
            'target':round(price*(1.02 if act=='buy' else 0.98),2),
            'reason':why}
