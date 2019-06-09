# Code for the parsing and preprocessing of the persona-chat dataset.
#
# Supported tasks:
#    - Translation
#
# @author: jpquiroga@gmail.com

import json
from typing import Text
from tqdm import tqdm
from .translate import Translator


def translate_dataset(dataset_file: Text, destination_dataset_file: Text, translator: Translator):
    """
    Translate a dataset. The dataset must be in the Persona-Chat format.
    :param dataset_file: Location of the json file of the dataset.
    :param destination_dataset_file: Location of the destination translated dataset.
    :param translator:
    """
    with open(dataset_file, "r") as f:
        dataset = json.load(f)
    # Dataset is a list of dictionaries, each of them corresponding to one dialogue.
    # Translate texts
    for d in dataset:
        dialogue = d["dialogue"]
        for turn in dialogue:
            turn["text"] = translator.translate(turn["text"])
    # Save translated dataset
    with open(destination_dataset_file, "w") as f:
        json.dump(dataset, f)


def get_texts_to_translate(dataset_file: Text, destination_texts_file: Text):
    """
    Get a list of texts to be translated from a Persona-Chat dataset and saves it as to a plain text file.
    :param dataset_file:
    :param destination_texts_file:
    :return: List of texts.
    """
    res = []
    with open(dataset_file, "r") as f:
        dataset = json.load(f)
    for d in dataset:
        dialogue = d["dialog"]
        for turn in dialogue:
            res.append(turn["text"])
    with open(destination_texts_file, "w") as f:
        for l in res:
            f.write(_normalize_text_line(l) + "\n")
    return res


def _normalize_text_line(text_line):
    return text_line.replace("\n", " ").replace("\r", "")


def translate_dataset_from_files(dataset_file: Text, destination_dataset_file: Text, origin_texts_file: Text,
                                 translated_texts_file: Text, tqdm_call: tqdm = tqdm):
    """
    Translate a dataset. The dataset must be in the Persona-Chat format.
    :param dataset_file: Location of the json file of the dataset.
    :param destination_dataset_file: Location of the destination translated dataset.
    :param origin_texts_file: File containing the original texts.
    :param translated_texts_file: File containing the translated texts.
    :param tqdm_call:
    :return: The new translated dataset as a json object.
    """
    with open(dataset_file, "r") as f:
        # Dataset is a list of dictionaries, each of them corresponding to one dialogue.
        dataset = json.load(f)
    # Load translated texts as a dictionary
    with open(origin_texts_file, "r") as f_o:
        _orig_texts = (t for t in f_o)
    with open(translated_texts_file, "r") as f_t:
        _trans_texts = (t for t in f_t)
    translation_dict = dict(zip(_orig_texts, _trans_texts))

    # Translate texts
    for d in tqdm_call(dataset):
        dialogue = d["dialogue"]
        for turn in dialogue:
            _t = _normalize_text_line(turn["text"])
            turn["text"] = translation_dict(_t)

    # Save translated dataset
    with open(destination_dataset_file, "w") as f:
        json.dump(dataset, f)
    return dataset
