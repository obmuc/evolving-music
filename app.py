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

    file_handler = FileHandler()
    seed_file_with_full_path = file_handler.find_seed_file_on_disk(seed_file)
    seed_file_with_relative_path = file_handler.full_to_relative_path(seed_file_with_full_path)

    seed_melody = file_handler.filename_to_list(filename=seed_file)
    i = 0
    created_melodies = []
    created_files = []
    mutator = Mutator(seed_melody=seed_melody, mutation_percentage=5)
    while i < 10:
        mutated_melody = mutator.mutate()
        if mutated_melody != seed_melody and mutated_melody not in created_melodies:
            midi_maker = MidiMaker(file_handler=file_handler, melody=mutated_melody)
            mutated_file = midi_maker.write()
            created_melodies.append(mutated_melody)
            created_files.append(file_handler.full_to_relative_path(mutated_file))
            i += 1
    # print(created_files)

    return render_template(
        'review.html',
        seed_file_with_relative_path = seed_file_with_relative_path,
        created_files = created_files
    )


if __name__ == '__main__':
    app.run(debug=True) 