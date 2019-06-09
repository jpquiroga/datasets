# Code for unifying translation for dataset processing.
#
# @author: jpquiroga@gmail.com

from typing import Text


class Translator(object):
    """
    Base Translator class
    """

    def translate(self, text: Text, **kwargs) -> Text:
        """
        Translate a text.
        :param text: Text to translate
        :param kwargs:
        :return: Translated text.
        """
        raise NotImplementedError("Translator is an abstract class. This method needs to be implemented!")
