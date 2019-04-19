#
# Wrapper code for the Azure Translation Service API.
# See https://docs.microsoft.com/en-us/azure/cognitive-services/translator/quickstart-python-translate
#

# -*- coding: utf-8 -*-
import os, requests, uuid, json
from tqdm import tqdm
from typing import Text, List, Optional, Tuple, Any, Dict, Callable


# class AzureTranslator(object):
#     """
#     Wrapper for the Azure Translator API.
#     See https://docs.microsoft.com/en-us/azure/cognitive-services/translator/quickstart-python-translate
#     """
#
#     def __init__(self, subscription_key: Text):
#         # Requests elements
#         self.base_url = 'https://api.cognitive.microsofttranslator.com'
#         self.path = '/translate?api-version=3.0'
#         self.params = '&to=es'
#         self.constructed_url = self.base_url + self.path + self.params
#         self.headers = {
#             'Ocp-Apim-Subscription-Key': subscription_key,
#             'Content-type': 'application/json',
#             'X-ClientTraceId': str(uuid.uuid4())
#         }
#
#     def translate_text_azure(self, texts: List[Text], origin_language: Optional[Text] = "en",
#                              destination_language: Optional[Text] = "es") -> Tuple[List[Text], List[Text]]:
#         """
#         Translate a list of texts to a given language.
#
#         :param texts: List of texts to be translated (independently from each other).
#         :param origin_language:
#         :param destination_language:
#         :return:
#         """
#         body = [{"text": t, "from": origin_language, "to": destination_language} for t in texts]
#         request = requests.post(self.constructed_url, headers=self.headers, json=body)
#         response = request.json()
#         # Extract results
#         res = []
#         for r in response:
#             # Take the first translation
#             res.append(r["translations"][0]["text"])
#         return res, response


class AzureTranslator(object):
    """
    Wrapper for the Azure Translator API.
    See https://docs.microsoft.com/en-us/azure/cognitive-services/translator/quickstart-python-translate
    """

    _SEPARATOR = "$___$___$"

    def __init__(self, subscription_key: Text, origin_language: Text = "en", destination_language: Text = "es"):

        # If you want to set your subscription key as a string, uncomment the line
        # below and add your subscription key.
        # subscriptionKey = 'put_your_key_here'

        self.origin_language = origin_language
        self.destination_language = destination_language
        self.base_url = 'https://api.cognitive.microsofttranslator.com'
        self.path = '/translate?api-version=3.0'
        self.params = '&from={}&to={}'.format(origin_language, destination_language)
        self.constructed_url = self.base_url + self.path + self.params
        self.headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

    def translate_text_azure(self, texts: List[Text], log_file: Text = "./translation_log") -> \
            Tuple[List[Text], List[Text]]:
        """
        Translate a list of texts to one language.

        :param texts:
        :param log_file: File to store (append) logging data. This logging file can be used to recover translation
        results. Raw API responses are also appended to the file <log_file>_raw

        Sample Azure Translation API response:

            [
                {
                    "detectedLanguage": {
                        "language": "en",
                        "score": 1.0
                    },
                    "translations": [
                        {
                            "text": "Hallo Welt!",
                            "to": "de"
                        },
                        {
                            "text": "Salve, mondo!",
                            "to": "it"
                        }
                    ]
                }
            ]

        :return: List of translation and list of raw responses (as a tuple).
        """
        #     body = [{
        #         'text' : text
        #     }]
        body = [{"text": t} for t in texts]
        request = requests.post(self.constructed_url, headers=self.headers, json=body)
        if request.status_code != 200:
            raise TranslationExample(status_code=request.status_code, reason=request.reason,
                                     content=request.content)
        response = request.json()
        # Extract results
        res = []
        if log_file is not None:
            with open(log_file + "_raw", "a") as f:
                for i, r in enumerate(response):
                    f.write("{} {} {}\n".format(texts[i], AzureTranslator._SEPARATOR, r))
        for r in response:
            # Take the first translation
            res.append(r["translations"][0]["text"])
        if log_file is not None:
            with open(log_file, "a") as f:
                for i, r in enumerate(res):
                    f.write("{} {} {}\n".format(texts[i], AzureTranslator._SEPARATOR, r))
            with open(log_file + "_raw", "a") as f:
                for i, r in enumerate(response):
                    f.write("{} {} {}\n".format(texts[i], AzureTranslator._SEPARATOR, r))

        return res, response

    def translate_with_dict(self, texts: List[Text], translation_dict: Dict[Text, Text], num_texts_per_request=20,
                            tqdm_call: Optional[Callable] = tqdm, log_file: Text = "./translation_log") -> Dict[Text,Text]:
        """

        :param texts: List of texts to translate
        :param translation_dict: Translation dictionary
        :param num_texts_per_request:
        :param tqdm_call:
        :param log_file:
        :return:
        """
        _buffer = []
        for i, t in tqdm_call(enumerate(texts), desc="Number of texts to translate", total=len(texts)):
            _t = t.strip()
            if _t not in translation_dict:
                _buffer.append(_t)
            if len(_buffer) >= num_texts_per_request or i >= len(texts)-1:
                r1, r2 = self.translate_text_azure(_buffer, log_file=log_file)
                for j, trans_t in enumerate(r1):
                    translation_dict[_buffer[j]] = trans_t
                _buffer = []
        # if len(_buffer) > 0:
        #     r1, r2 = self.translate_text_azure(_buffer, log_file=log_file)
        #     for j, trans_t in enumerate(r1):
        #         translation_dict[_buffer[j]] = trans_t
        return translation_dict


class TranslationExample(Exception):

    def __init__(self, status_code: Any, reason: Any, content: Any):
        super().__init__(status_code, reason, content)
        self.status_code = status_code
        self.reason = reason
        self.content = content

