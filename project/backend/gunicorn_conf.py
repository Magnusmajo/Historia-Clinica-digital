import multiprocessing
import os

bind = "0.0.0.0:8000"
workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
threads = int(os.getenv("WEB_THREADS", "1"))
timeout = int(os.getenv("WEB_TIMEOUT_SECONDS", "60"))
graceful_timeout = int(os.getenv("WEB_GRACEFUL_TIMEOUT_SECONDS", "30"))
keepalive = int(os.getenv("WEB_KEEPALIVE_SECONDS", "5"))
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()
forwarded_allow_ips = os.getenv("FORWARDED_ALLOW_IPS", "*")
