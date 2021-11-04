import os
import datetime
import random

from pathlib import Path
from midiutil import MIDIFile


class FileHandler(object):

    """
    Note Notation:
    List of lists of lists, each inner-most list in the form (Midi Note Number, Duration as 'beat').
    The next inner-most lists are considered 'NoteUnits', or groups of notes.

    example: [[[48, 1.0],], [[51, 0.25], [53, 0.25], [55, 1.0], [51, 0.5],], [[48, 2.0],]]

    File names for each melody consist of:
        * each note as midi note number *dash* duration (with the '.' replaced by 'p')
        * and each NoteUnit separated by double underscores
    The above example becomes:
        48-1p0__51-0p25_52-0p25_55-1p0_51_0p5__48-2p0.mid
    """

    def __init__(self):
        self.root_directory = '/Users/obmuc/Documents/programming/python/evolving/evolving-music/static/midi_files'
        self.date_string = str(datetime.datetime.now().date())
        self.directory = self._setup_directory()

    def increment_directory_name(self, directory):
        highest_current = None
        for path in Path(self.root_directory).iterdir():
            if path.is_dir():
                last_part_of_path = str(path).split('/')[-1]
                date_part_of_name = last_part_of_path.split('_')[0]
                if (date_part_of_name == self.date_string):
                    try:
                        directory_increment = last_part_of_path.split('_')[1]
                    except IndexError:
                        continue
                    if (not highest_current) or (int(directory_increment) > highest_current):
                        highest_current = int(directory_increment)
        if highest_current:
            return f"{directory}_{highest_current + 1}"
        else:
            return f"{directory}_1"
            
    def _setup_directory(self):
        """Create a folder to store today's mutations, if necessary)"""
        directory = os.path.join(self.root_directory, self.date_string)
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            directory = self.increment_directory_name(directory)
        # create a 'seed' directory inside the folder to store the file used to generate that day's mutations.
        seed_directory = os.path.join(directory, 'seed')
        if not os.path.exists(seed_directory):
            os.makedirs(seed_directory)
        return directory

    def get_seed_file(self):
        """Get the seed file from the root_directory"""
        os.chdir(self.root_directory)
        for listed_file in os.listdir("."):
            if listed_file.endswith(".mid"):
                return listed_file

    @staticmethod
    def filename_to_list(filename):
        """Convert a string into a list representing a melody"""
        melody_list = []
        melody_string = filename.split('.')[0]
        note_unit_strings = melody_string.split('__')
        for note_unit_string in note_unit_strings:
            note_strings = note_unit_string.split('_')
            note_unit_list = []
            for note_string in note_strings:
                note_values = note_string.split('-')
                note_unit_list.append([int(note_values[0]), float(str(note_values[1]).replace('p', '.'))])
            melody_list.append(note_unit_list)
        return melody_list

    @staticmethod
    def list_to_filename(melody_list):
        """Convert a list representing a melody into a filename-appropriate string"""
        the_string = ""
        for note_unit in melody_list:
            if the_string != "":
                the_string += '__'
            the_string += "_".join(["%s-%s" % (note[0], str(note[1]).replace('.', 'p')) for note in note_unit])
        return "%s.mid" % the_string


class MidiMaker:
    """ Transforms NoteUnits into midi notes that can be output. """

    def __init__(self, file_handler, melody):
        self.file_handler = file_handler
        self.melody = melody

        # set some defaults
        self.track = 0
        self.channel = 0
        self.time = 0
        self.tempo = 60
        self.volume = 127

    def write(self):
        midi_file = MIDIFile(1)
        midi_file.addTempo(self.track, self.time, self.tempo)
        current_time = 0
        for note_unit in self.melody:
            for note in note_unit:
                midi_file.addNote(self.track, self.channel, note[0], current_time, 1, self.volume)  # note[1]
        file_name_with_path = os.path.join(self.file_handler.directory, self.file_handler.list_to_filename(melody_list=self.melody))
        with open(file_name_with_path, "wb") as output_file:
            midi_file.writeFile(output_file)
        return file_name_with_path


class Mutator(object):
    """
    Possible Mutations:
        * Pitch Mutations:
            * no change
            * Up half-step
            * Down half-step
            * Up whole-step
            * Down whole-step
            etc...
        * Duration Mutations:
            * no change
            * + .25
            * - .25
            * + .5
            * - .5
            * + 1
            * - 1
        * Splitting Mutations (one note becomes 2 or three; only if duration .5 or greater):
            * If cleanly divisible by 2:
                * split in half
            * If cleanly divisible by 3:
                * split into thirds
        * Joining Mutations (2 or more notes become one; randomly choose which pitch to use)
    """

    # TODO: Allow deletion of a note if multiple in note-unit

    DURATION_CHANGES = {0: 0.25, 1: 0.5, 2: 1}

    def __init__(self, seed_melody, mutation_percentage=25):
        """
        Args:
            seed_melody (List)
        Kwargs:
            mutation_percentage (Int): defines what percent of the time a note_unit should mutate.
        """
        self.seed_melody = seed_melody
        self.mutation_percentage = mutation_percentage
        self.pitch_change_probs = self._build_scaled_probabilities_list(max_change=12)
        self.duration_change_probs = self._build_scaled_probabilities_list(max_change=3)

    @staticmethod
    def _build_scaled_probabilities_list(max_change):
        """Builds a list of integers.  The first is derived by 2 to the power of (max_change - 1).  Each subsequent
        value derived by (previous_value / 2) + previous_value.  This results in a series of values that can be used to
        provide decreasing probabilities for random selections: a random number between 1 and the max value of the list
        is selected.  The index of the lowest value in the list that is greater than or equal to the random value can
        then be used to select the value needed.

        Args:
            max_change (Int): the number of values that should be in the resulting list
        Returns:
            List containing Ints that represent scaled probabilities

        Examples:
            max_change=4:
                 1, 2, 3, 4
                 (8, 4, 2, 1)
                 result = 8, 12, 14, 15
            max_change=5:
                 1, 2, 3, 4, 5
                 (16, 8, 4, 2, 1)
                 result = 16, 24, 28, 30, 31
        """

        change_probs = []
        first_value = 2**(max_change - 1)
        change_probs.append(first_value)
        i = max_change
        prob_range = first_value
        prob_value = first_value
        while i > 1:
            prob_range /= 2
            prob_value = prob_range + prob_value
            change_probs.append(prob_value)
            i -= 1
        return change_probs

    def _join_or_split(self, note_unit):
        """Join or split apart note_units

        Args:
            note_unit (list)
        Returns:
            note_unit (list)
        """
        operation = random.choice(['join', 'split'])
        if operation == 'split':
            target_note = random.choice(note_unit)
            target_note_index = note_unit.index(target_note)
            if target_note[1] < 0.5:
                return note_unit  # too small - do nothing
            elif target_note[1] % 0.5 == 0.0:
                shortened_note = [target_note[0], target_note[1] * 0.5]
                note_unit[target_note_index] = shortened_note
                note_unit.insert(target_note_index + 1, self._mutate_pitch(seed_note=shortened_note))
                return note_unit
            elif target_note[1] % 0.75 == 0.0:
                new_duration = target_note[1] / 3
                shortened_note = [target_note[0], new_duration]
                note_unit[target_note_index] = shortened_note
                note_unit.insert(target_note_index + 1, self._mutate_pitch(seed_note=shortened_note))
                note_unit.insert(target_note_index + 2, self._mutate_pitch(seed_note=shortened_note))
                return note_unit
        else:
            if len(note_unit) <= 1:
                return note_unit
            else:
                number_of_notes_to_join = 2
                note_join_probs_list = self._build_scaled_probabilities_list(max_change=len(note_unit) - 1)
                note_join_probs_index = random.randint(1, note_join_probs_list[-1])
                for j, note_change_prob in enumerate(note_join_probs_list):
                    if note_join_probs_index <= note_change_prob:
                        number_of_notes_to_join = j + 2
                        break
                notes_to_join = note_unit[0:number_of_notes_to_join]
                remaining_notes = note_unit[number_of_notes_to_join:]
                new_pitch = random.choice(notes_to_join)[0]
                new_duration = 0
                for note in notes_to_join:
                    new_duration += note[1]
                remaining_notes.insert(0, [new_pitch, new_duration])
                return remaining_notes
        return note_unit

    def _mutate_duration(self, seed_note):
        note = list(seed_note)  # make a copy of the note so we don't overwrite seed_melody
        duration_change_rand = random.randint(1, self.duration_change_probs[-1])
        duration_change_index = 0
        for i, dcp_value in enumerate(self.duration_change_probs):
            if duration_change_rand <= dcp_value:
                duration_change_index = i
                break
        duration_change_amount = self.DURATION_CHANGES[duration_change_index]
        increase_duration = random.choice([True, False])
        if increase_duration:
            new_duration = note[1] + duration_change_amount
        else:
            new_duration = note[1] - duration_change_amount
        if new_duration > 0:
            note[1] = new_duration
        return note

    def _mutate_pitch(self, seed_note):
        note = list(seed_note)  # make a copy of the note so we don't overwrite seed_melody
        pitch_change_rand = random.randint(1, self.pitch_change_probs[-1])
        pitch_change_amount = 0
        for i, pcp_value in enumerate(self.pitch_change_probs):
            if pitch_change_rand <= pcp_value:
                pitch_change_amount = i + 1
                break
        increase_pitch = random.choice([True, False])
        if increase_pitch:
            note[0] += pitch_change_amount
        else:
            note[0] -= pitch_change_amount
        return note

    def _mutate_duration_and_pitch(self, note_unit):
        """'Mutates' a note_unit by altering it's pitch and/or duration.

        Args:
            note_unit (List)
        Returns:
            note_unit (List)
        """
        # if there's more than one note in the note_unit:
        if len(note_unit) > 1:
            # choose which notes in the note_unit to mutate randomly select which to change
            # a probability scale is used to determine how many notes to mutate, with fewer mutations being more common.
            number_of_notes_to_change = 1
            note_change_probs_list = self._build_scaled_probabilities_list(max_change=len(note_unit))
            note_change_index = random.randint(1, note_change_probs_list[-1])
            for j, note_change_prob in enumerate(note_change_probs_list):
                if note_change_index <= note_change_prob:
                    number_of_notes_to_change = j + 1
            notes_to_change = []
            while len(notes_to_change) < number_of_notes_to_change:
                chosen_note = random.choice(note_unit)
                if chosen_note not in notes_to_change:
                    notes_to_change.append(note_unit.index(chosen_note))
        else:
            notes_to_change = [0]
        for note_index in notes_to_change:
            note = note_unit[note_index]
            mutated_note = note
            # choose which type of mutation (pitch, duration, or both)
            mutation_types = [
                ['_mutate_pitch', ],
                ['_mutate_duration', ],
                ['_mutate_pitch', '_mutate_duration']
            ]
            mutation_type = random.choice(mutation_types)
            for mutation_method in mutation_type:
                mutated_note = getattr(self, mutation_method)(note)
            note_unit[note_index] = mutated_note
        return note_unit

    def mutate(self):
        mutated_melody = []
        # loop through each note_unit
        for note_unit in self.seed_melody:
            # decide if each one should mutate
            mutate_rand = random.randint(1, 100)
            if mutate_rand <= self.mutation_percentage:
                mutating_note_unit = list(note_unit)  # copy note_unit so we don't alter seed melody
                # we join/split note_units randomly using the same mutation percentage passed into __init__()
                join_split_rand = random.randint(1, 100)
                if join_split_rand <= self.mutation_percentage:
                    mutating_note_unit = self._join_or_split(note_unit=mutating_note_unit)
                else:  # if the note_unit isn't joining/splitting, alter it's pitch and/or duration
                    mutating_note_unit = self._mutate_duration_and_pitch(note_unit=mutating_note_unit)
                mutated_melody.append(mutating_note_unit)
            else:
                mutated_melody.append(note_unit)
        return mutated_melody


# For running via command line
def main():
    file_handler = FileHandler()
    seed_file = file_handler.get_seed_file()
    seed_melody = file_handler.filename_to_list(filename=seed_file)
    print("original melody:")
    print(seed_melody)
    i = 0
    created_melodies = []
    mutator = Mutator(seed_melody=seed_melody, mutation_percentage=5)
    while i < 20:
        mutated_melody = mutator.mutate()
        if mutated_melody != seed_melody and mutated_melody not in created_melodies:
            print("mutated_melody:")
            print(mutated_melody)
            midi_maker = MidiMaker(file_handler=file_handler, melody=mutated_melody)
            midi_maker.write()
            created_melodies.append(mutated_melody)
            i += 1


if __name__ == "__main__":
    main()