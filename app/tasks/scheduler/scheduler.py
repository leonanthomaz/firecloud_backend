# app/functions/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.helpers.render.ping import keep_alive_ping

def start_scheduler():
    scheduler = BackgroundScheduler(timezone="UTC")
    
    # Ping de keep-alive a cada 5 minutos
    scheduler.add_job(keep_alive_ping, "interval", minutes=5)

    scheduler.start()
    