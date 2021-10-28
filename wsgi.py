import os
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
    # TODO: configure midi files to be served by the web server and send a URL instead of a file path to the template.

    seed_file = request.form.get('seed_file')

    current_directory = os.getcwd()
    midi_file_directory = f"{current_directory}/midi_files"

    for dirpath, dirnames, files in os.walk(midi_file_directory):
        for found_name in files:
            if found_name == seed_file:
                seed_file_with_path = os.path.join(dirpath, found_name)

    return render_template(
        'review.html',
        seed_file_with_path = seed_file_with_path
    )
