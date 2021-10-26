from flask import Flask, render_template

app = Flask(__name__)

@app.route("/test")
def test():
    return render_template('test.html')


@app.route("/")
def home():
    return render_template('home.html')