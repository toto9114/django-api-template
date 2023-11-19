import multiprocessing
from common_lib.utils.env_loader import load_env
from config import config as c


bind = "0.0.0.0:5000"
workers = load_env(
    "WSGI_NUM_PROCESS", str(multiprocessing.cpu_count() * 2 + 1), as_type=int
)
threads = load_env("WSGI_NUM_THREAD", "1", as_type=int)
accesslog = "-"
errorlog = "-"
loglevel = c.LOG_LEVEL

timeout = load_env("WSGI_TIMEOUT", "60", as_type=int)
graceful_timeout = load_env("WSGI_GRACEFUL_TIMEOUT", "30", as_type=int)
