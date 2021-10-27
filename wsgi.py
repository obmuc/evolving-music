from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/test")
def test():
    return render_template('test.html')


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/review", methods = ['POST', 'GET'])
def review():
    print(request.form)
