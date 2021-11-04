import os
from flask import Flask, render_template, request
from mutator import FileHandler, Mutator, MidiMaker

app = Flask(__name__)

@app.route("/test")
def test():
    return render_template('test.html')


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/review", methods = ['POST', 'GET'])
def review():
    seed_file = request.form.get('seed_file')

    current_directory = os.getcwd()
    midi_file_directory = f"{current_directory}/static/midi_files"

    for dirpath, dirnames, files in os.walk(midi_file_directory):
        for found_name in files:
            if found_name == seed_file:
                seed_file_with_path = os.path.join(dirpath, found_name)

    seed_file_with_relative_path = seed_file_with_path.replace(current_directory, '')

    file_handler = FileHandler()
    seed_melody = file_handler.filename_to_list(filename=seed_file)
    i = 0
    created_melodies = []
    created_files = []
    mutator = Mutator(seed_melody=seed_melody, mutation_percentage=5)
    while i < 10:
        mutated_melody = mutator.mutate()
        if mutated_melody != seed_melody and mutated_melody not in created_melodies:
            # print("mutated_melody:")
            # print(mutated_melody)
            # TODO: need to return a relative file instead for use in links... can't be full path
            midi_maker = MidiMaker(file_handler=file_handler, melody=mutated_melody)
            mutated_file = midi_maker.write()
            created_melodies.append(mutated_melody)
            created_files.append(mutated_file)
            i += 1
    # print(created_files)

    return render_template(
        'review.html',
        seed_file_with_relative_path = seed_file_with_relative_path,
        created_files = created_files
    )


if __name__ == '__main__':
    app.run(debug=True) 