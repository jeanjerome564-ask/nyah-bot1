# Nyah — Cloud FullScan Dashboard (Render)

**Features**
- Web dashboard (password: `Elysee01`)
- Background scanner every 5 min (batch rotates ~25 tickers)
- Email + Verizon SMS via SMTP gateways
- Optional phone call alerts (Twilio)
- Surprise Me idea button
- Simple daily backtest summary

> Educational only. No guarantees. Always use stop losses.

## Deploy on Render (no code)

1. Create free account at https://render.com
2. Click **New +** → **Blueprint** → upload this ZIP
3. When prompted, add env vars from `.env.example` (set your SMTP keys)
4. Render creates **nyah-web** (dashboard) and **nyah-worker** (scanner)
5. Open web URL → login with `Elysee01`

## Add more tickers
Edit `symbols.txt` in the Render dashboard → one ticker per line.

## Local dev
```
pip install -r requirements.txt
python worker.py
gunicorn app:app  # or python app.py for dev
```
