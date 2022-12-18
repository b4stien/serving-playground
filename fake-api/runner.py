from circus import get_arbiter

myprogram = {"cmd": "python fake_api.py", "numprocesses": 4}

arbiter = get_arbiter([myprogram])
try:
    arbiter.start()
finally:
    arbiter.stop()
