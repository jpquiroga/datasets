#
# Preprocessing utilities.
#

from typing import Text, List, Optional, Callable, Dict
from tqdm import tqdm


def split_line(s_line: Text, delim: Text) -> List[Text]:
    """
    Split a line of text according to a given delimiter.
    :param s_line: Text line
    :param delim: Delimiter

    :return: List of texts
    """
    res = []
    _buff = s_line
    while delim in _buff:
        _index = _buff.index(delim)
        res.append(_buff[:_index].strip())
        _buff = _buff[_index+len(delim):].strip()
    res.append(_buff)
    return res


def build_text_translation_dict(log_file: Text, tqdm_call: Optional[Callable] = tqdm) -> Dict[Text, Text]:
    """
    Build a text translation dictionary from a translation log file with the format:
    <original_text> $___$___$ <translated_text>

    :param log_file:
    :param tqdm_call:
    :return: The dictionary with the translations
    """
    res = {}
    with open(log_file) as f:
        for l in tqdm_call(f.readlines()):
            toks = l.split("$___$___$")
            if len(toks) == 2:
                res[toks[0].strip()] = toks[1].strip()
    return res


def count_chars(texts_list: List[Text]) -> int:
    """
    Count the number of characters in a text list.
    :param texts_list:
    :return: Number of characters
    """
    count = 0
    for l in texts_list:
        count += len(l)
    return count
