(c) 2024 Felix Farquharson
This code is licensed under MIT license (see LICENSE.txt for details)


Chord, Scale, and Chord Progression MIDI, WAV, and MP3 Generator
================================================================

Sponsorship
-----------
Please give me money:

Card: https://buy.stripe.com/00g00m6e1gEW68E4gk

Description
-----------

This software generates all possible chords, scales, and some generic progressions
(in progress, not fully working) and contains code to output them as midi, flac,
wav, mp3 and score image files. It checks for harmonic consonance and will only generate
correct chords.

How to run/install
------------------

Install MuseScore or a similar XML reader. For generating the midi files from code.

Install the libraries in the requirements file with `pip install -r requirements.txt`.

Run the file with `python main.py` and the files will be generated in the output
folder.
