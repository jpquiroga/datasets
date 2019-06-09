#
# Preprocessing utilities for the Cornell movies dialogues corpus
# (https://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html)
#
# @author: jpquiroga@gmail.com

import pandas as pd
from tqdm import tqdm
from typing import Text, Optional, Callable
from . import split_line


def movie_lines_to_dataframe(file_path: Text, tqdm_call: Optional[Callable] = tqdm) -> pd.DataFrame:
    """
    Transform the movie_lines.txt file to a pandas dataframe object.

    :param file_path:
        - movie_lines.txt
            - contains the actual text of each utterance
            - fields:
                - lineID
                - characterID (who uttered this phrase)
                - movieID
                - character name
                - text of the utterance
    :param tqdm_call:

    :return Pandas dataframe
    """
    DELIM = "+++$+++"
    line_ids = []
    character_ids = []
    movie_ids = []
    character_names = []
    utterances = []
    with open(file_path, encoding="utf-8", errors="ignore") as f:
        for l in tqdm_call(f.readlines()):
            _parsed_line = split_line(l, DELIM)
            line_ids.append(_parsed_line[0])
            character_ids.append(_parsed_line[1])
            movie_ids.append(_parsed_line[2])
            character_names.append(_parsed_line[3])
            utterances.append(_parsed_line[4])
    res = pd.DataFrame()
    res["LINE_ID"] = line_ids
    res["CHARACTER_ID"] = character_ids
    res["MOVIE_ID"] = movie_ids
    res["CHARACTER_NAME"] = character_names
    res["UTTERANCE"] = utterances
    return res






