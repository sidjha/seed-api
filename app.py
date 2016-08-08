from flask import Flask, render_template, request, json
import os

app = Flask(__name__)

@app.route("/")
def index():
    return "seed v1.0"

if __name__ == "__main__":
    app.run()