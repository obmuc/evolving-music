import os
import shutil
from flask import Flask, render_template, request
from mutator import FileHandler, Mutator, MidiMaker

app = Flask(__name__)

""" 
TODO:
- write selected file to a new folder, 'seed_file', and move any previous files in that folder to the 'progression' folder
- add a 'Discard all and regenerate' option which deletes the folder that was created and starts over with the same seed file.
- include file tempo in the file name
- retrieve tempo from the file name and use when generating derivative melodies
- create test suite
"""

@app.route("/test")
def test():
    return render_template('test.html')


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/review", methods = ['POST', 'GET'])
def review():
    seed_file = request.form.get('seed_file')

    # alter to allow submittal of seed files that already have relative path
    file_handler = FileHandler()
    seed_file_with_full_path = file_handler.find_seed_file_on_disk()
    seed_file_with_relative_path = file_handler.full_to_relative_path(seed_file_with_full_path)

    seed_melody = file_handler.filename_to_list(filename=seed_file)
    i = 0
    created_melodies = []
    created_files = []
    output_directory = file_handler.setup_output_directory()
    output_directory_seed_folder = os.path.join(output_directory, 'seed')
    shutil.copy2(seed_file_with_full_path, output_directory_seed_folder)
    mutator = Mutator(seed_melody=seed_melody, mutation_percentage=5)
    while i < 10:
        mutated_melody = mutator.mutate()
        if mutated_melody != seed_melody and mutated_melody not in created_melodies:
            midi_maker = MidiMaker(output_directory=output_directory, melody=mutated_melody)
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


@app.route("/select", methods = ['POST', 'GET'])
def select():
    file_handler = FileHandler()
    selected_file_with_relative_path = request.form.get('relative_file_path')
    selection_type = request.form.get('selection_type')
    print(selection_type)
    # 1 archive the current seed file in the 'progression' directory
    file_handler.archive_seed_file()
    # 2 write the selected file to seed_file directory
    file_handler.selected_file_to_seed_file(selected_file_with_relative_path)
    if selection_type == 'regenerate':
        # 3 use requests to submit a POST request to the /review route, passing in the selected file
        pass
    elif selection_type == 'quit':
        # 3 render a new 'quit' template.
        pass



if __name__ == '__main__':
    app.run(debug=True) 