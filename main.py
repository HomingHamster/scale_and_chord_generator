# (c) 2024 Felix Farquharson
# This code is licensed under MIT license (see LICENSE.txt for details)

import os
from mido import MidiFile, MidiTrack, Message
import music21
from midi2audio import FluidSynth
import ffmpeg

# Define the note names and their corresponding MIDI numbers
notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
note_to_midi = {note: i for i, note in enumerate(notes)}

# Define the scale intervals
scales = {
    "major": [2, 2, 1, 2, 2, 2, 1],
    "natural_minor": [2, 1, 2, 2, 1, 2, 2],
    "harmonic_minor": [2, 1, 2, 2, 1, 3, 1],
    "melodic_minor": [2, 1, 2, 2, 2, 2, 1],
    "dorian": [2, 1, 2, 2, 2, 1, 2],
    "phrygian": [1, 2, 2, 2, 1, 2, 2],
    "lydian": [2, 2, 2, 1, 2, 2, 1],
    "mixolydian": [2, 2, 1, 2, 2, 1, 2],
    "locrian": [1, 2, 2, 1, 2, 2, 2]
}

chord_formulas = {
    # Major Chords
    "major": [0, 4, 7],
    "major6": [0, 4, 7, 9],
    "major7": [0, 4, 7, 11],
    "major9": [0, 4, 7, 11, 14],
    "major11": [0, 4, 7, 11, 14, 17],
    "major13": [0, 4, 7, 11, 14, 17, 21],
    # Minor Chords
    "minor": [0, 3, 7],
    "minor6": [0, 3, 7, 9],
    "minor7": [0, 3, 7, 10],
    "minor9": [0, 3, 7, 10, 14],
    "minor11": [0, 3, 7, 10, 14, 17],
    "minor13": [0, 3, 7, 10, 14, 17, 21],
    # Dominant Chords
    "dominant7": [0, 4, 7, 10],
    "dominant9": [0, 4, 7, 10, 14],
    "dominant11": [0, 4, 7, 10, 14, 17],
    "dominant13": [0, 4, 7, 10, 14, 17, 21],
    # Augmented Chords
    "augmented": [0, 4, 8],
    "augmented7": [0, 4, 8, 10],
    "augmented9": [0, 4, 8, 10, 14],
    # Diminished Chords
    "diminished": [0, 3, 6],
    "diminished7": [0, 3, 6, 9],
    # Suspended Chords
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    # Altered Chords
    "7#5": [0, 4, 8, 10],
    "7b5": [0, 4, 6, 10],
    "7#9": [0, 4, 7, 10, 15],
    "7b9": [0, 4, 7, 10, 13],
    # Other Chords
    "add9": [0, 4, 7, 14],
    "major7#11": [0, 4, 7, 11, 18],
    "minor_major7": [0, 3, 7, 11]
}

progressions = {
    "I-V-ii-IV": [0, 4, 1, 3],
    "12-bar-blues": [0, 0, 0, 0, 3, 3, 0, 0, 4, 3, 0, 0],
    "I-IV-I-V-IV-I": [0, 3, 0, 4, 3, 0],
    "iii-vi-ii-V": [2, 5, 1, 4],
    "I-vi-ii-V": [0, 5, 1, 4],
    "I-vi-ii-V-I": [0, 5, 1, 4, 0],
    "I-V-vi-iii-IV-I-IV-V": [0, 4, 5, 2, 3, 0, 3, 4],
    "I-IV-V": [0, 3, 4],
    "I-bVII-IV": [0, 10, 3],
    "I-V-vi-iii-IV-I-ii-V": [0, 4, 5, 2, 3, 0, 1, 4],
    "ii-V-I": [1, 4, 0],
    "I-ii-IV-V": [0, 1, 3, 4],
    "ii-V-I-vi": [1, 4, 0, 5],
    "i-bVI-bVII": [0, 8, 10],
    "i-bVII-bVI-VII": [0, 10, 8, 11],
    "i-iv-v": [0, 3, 7],
    "I-IV-vi-V": [0, 3, 5, 4],
    "I-V-IV-I": [0, 4, 3, 0],
    "vi-IV-I-V": [5, 3, 0, 4],
    "I-IV-I-V": [0, 3, 0, 4],
    "I-V-IV": [0, 4, 3],
    "I-IV-V-IV": [0, 3, 4, 3],
    "I-IV-V-I": [0, 3, 4, 0],
    "I-vi-IV-V": [0, 5, 3, 4],
}


# Function to check harmonic consonance
def is_consonant_chord(chord):
    consonant_intervals = [0, 3, 4, 7, 8, 9, 12]
    for i in range(len(chord)):
        for j in range(i + 1, len(chord)):
            interval = (chord[j] - chord[i]) % 12
            if interval not in consonant_intervals:
                return False
    return True


# Function to generate a scale
def generate_scale(root, scale_type):
    scale_intervals = scales[scale_type]
    scale = [root]
    current_note = notes.index(root)
    for interval in scale_intervals:
        current_note = (current_note + interval) % 12
        scale.append(notes[current_note])
    return scale


# Function to generate a chord
def generate_chord(root, formula):
    root_index = notes.index(root)
    chord = [(root_index + interval) % 12 for interval in formula]
    return chord


# Function to generate all possible chords for a scale
def generate_all_chords_for_scale(scale):
    all_chords = []
    for root in scale:
        for chord_name, formula in chord_formulas.items():
            chord = generate_chord(root, formula)
            all_chords.append((root, chord_name, chord))
    return all_chords


# Function to generate chord progression
def generate_progression(chords, progression_pattern):
    progression = [chords[i] for i in progression_pattern]
    return progression


# Function to create MIDI file for a chord
def create_midi_for_chord(chord, filename):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    for note in chord:
        midi_note = note + 60  # +60 to bring it to the middle octave
        track.append(Message('note_on', note=midi_note, velocity=64, time=0))
        track.append(Message('note_off', note=midi_note, velocity=64, time=480))

    mid.save(filename)


# Function to create MIDI file for a scale
def create_midi_for_scale(scale, filename):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    for note in scale:
        midi_note = note_to_midi[note] + 60  # +60 to bring it to the middle octave
        track.append(Message('note_on', note=midi_note, velocity=64, time=0))
        track.append(Message('note_off', note=midi_note, velocity=64, time=480))

    mid.save(filename)


# Function to create MIDI files for all chords and progressions

def create_files_from_midi(filename):
    score_image = music21.converter.parse(filename + ".mid")

    score_image.write("musicxml.png", filename + ".png")

    os.remove(filename + ".musicxml")
    os.rename(filename + "-1.png", filename+".png")

    FluidSynth().midi_to_audio(midi_file=filename+".mid", audio_file=filename+".wav")
    FluidSynth().midi_to_audio(midi_file=filename+".mid", audio_file=filename+".flac")

    ffmpeg.input(filename+".flac").output(filename+".mp3").overwrite_output().run()


def create_midi_files(root_note, scale_type):
    scale = generate_scale(root_note, scale_type)
    all_chords = generate_all_chords_for_scale(scale)

    # Create directory structure
    base_dir = f'output/{root_note}_{scale_type}'
    chords_dir = f'{base_dir}/Chords'
    progressions_dir = f'{base_dir}/Progressions'
    os.makedirs(chords_dir, exist_ok=True)
    os.makedirs(progressions_dir, exist_ok=True)

    scale_filename = f'{base_dir}/{root_note}_{scale_type}'
    create_midi_for_scale(scale, scale_filename+".mid")
    create_files_from_midi(scale_filename)

    # Create MIDI files for chords
    for root, chord_name, chord in all_chords:
        if is_consonant_chord(chord):
            chord_filename = f'{chords_dir}/{root}_{chord_name}'
            create_midi_for_chord(chord, chord_filename+".mid")
            create_files_from_midi(chord_filename)

    # Create MIDI files for progressions
    for progression_name, pattern in progressions.items():
        progression = generate_progression([chord for _, _, chord in all_chords[:7]], pattern)
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)

        for chord in progression:
            for note in chord:
                midi_note = note + 60  # +60 to bring it to the middle octave
                track.append(Message('note_on', note=midi_note, velocity=64, time=0))
                track.append(Message('note_off', note=midi_note, velocity=64, time=480))

        filename = f'{progressions_dir}/{progression_name}'
        mid.save(filename+".mid")
        create_files_from_midi(filename)


# Generate MIDI files for each scale and chord

for note in notes:
    for scale_type in scales.keys():
        create_midi_files(note, scale_type)

print("MIDI files have been successfully created.")