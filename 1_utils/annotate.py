#!/usr/bin/env python
from __future__ import unicode_literals, print_function

import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding
import doccano
from spacy import displacy
import json


@plac.annotations(
    input_file=('File with texts to annotate', 'option', 'i', Path),
    output_file=('JSON file to store the annotations to', 'option', 'o', Path),
    model_dir=('Diretory of the pretrained model', 'option', 'm', str))
def main(input_file, output_file, model_dir):

    data = ''

    with open(str(input_file), 'r') as csv_file:
        data = csv_file.readlines()

    nlp2 = spacy.load(model_dir)

    output = []
    for line in data:
        doc = nlp2(line)
        output.append((line, {
            'entities': [(ent.start_char, ent.start_char + len(ent.text), ent.label_) for ent in doc.ents]
        }))

        print('Entities', [(ent.text, ent.start, ent.start + len(ent.text), ent.label_) for ent in doc.ents])

    file = open(str(output_file), 'w')
    file.write(json.dumps(output))
    file.close()


if __name__ == '__main__':
    plac.call(main)
