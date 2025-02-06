import os

from . import create_app

app = create_app(os.getenv("CONFIG_MODE"))

@app.route('/')
def hello():
    return "Hello World"

from .users import routes

if __name__ == "__main__":
    app.run()