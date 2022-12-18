import sys

from custom_gunicorn import CustomGunicornApplication


if __name__ == "__main__":
    socket = sys.argv[1] if len(sys.argv) > 1 else "unix:/var/run/fake_api/000.sock"
    gunicorn_app = CustomGunicornApplication(socket=socket).run()
