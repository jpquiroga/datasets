# Code for the parsing and preprocessing of the opensubtitles dataset.
#
# Supported tasks:
#    - Translation: see related alignment format information at https://www.cs.vassar.edu/CES/CES1-5.html#ToCalign
#

import xml.sax
import xml.dom
import os.path
from tqdm import tqdm
from bs4 import BeautifulSoup
import argparse
import subprocess
import time
import datetime

CURSOR_UP_ONE = "\x1b[1A"
ERASE_LINE = "\x1b[2K"

class OpensubtitlesAlignementHandler(xml.sax.ContentHandler):

    def __init__(self, alignment_file, base_dir: str, origin_output_text_file: str, destination_output_text_file: str,
                 subsample_rate=1, sample_index=0):
        self.subsample_rate = subsample_rate
        self.sample_index = sample_index
        self.aligment_file = alignment_file
        self.base_dir = base_dir
        self.origin_subtitles_file = None
        self.destination_subtitles_file = None
        self.origin_output_text_file = origin_output_text_file + "_" + str(sample_index)
        self.destination_output_text_file = destination_output_text_file + "_" + str(sample_index)
        # Temporal file descriptors for reading
        self.in_orig_fd = None
        self.in_dest_fd = None
        # Temporal parsers for reading
        self.in_orig_bs = None
        self.in_dest_bs = None
        # Open output files for writing
        self.out_orig_fd = open(self.origin_output_text_file, "w")
        self.out_dest_fd = open(self.destination_output_text_file, "w")
        # Progress control
        self.num_subtitles_to_process = self._get_num_subtitles_to_process()
        self.num_processed_subtitles = 0
        self.start_time = None
        self.count = 0
        self.active = False
        self.in_orig_dict = None
        self.in_dest_dict = None


    def startElement(self, name, attrs):
        """Signals the start of an element in non-namespace mode.

        The name parameter contains the raw XML 1.0 name of the
        element type as a string and the attrs parameter holds an
        instance of the Attributes class containing the attributes of
        the element."""
        if name == "linkGrp":
            if self.count % self.subsample_rate == self.sample_index:
                self.active = True
                self.origin_subtitles_file = os.path.join(self.base_dir, attrs["fromDoc"])
                self.destination_subtitles_file = os.path.join(self.base_dir, attrs["toDoc"])

                # All files are supposed to be uncompressed
                if self.origin_subtitles_file.endswith(".gz"):
                    self.origin_subtitles_file = self.origin_subtitles_file[:-3]
                if self.destination_subtitles_file.endswith(".gz"):
                    self.destination_subtitles_file = self.destination_subtitles_file[:-3]

                # Read subtitle files for later alignment processing
                self.in_orig_fd = open(self.origin_subtitles_file, "r")
                contents = self.in_orig_fd.read()
                self.in_orig_bs = BeautifulSoup(contents, 'xml')
                self.in_orig_dict = {e.attrs["id"]:e.text for e in self.in_orig_bs.find_all("s")}
                #
                self.in_dest_fd = open(self.destination_subtitles_file, "r")
                contents = self.in_dest_fd.read()
                self.in_dest_bs = BeautifulSoup(contents, 'xml')
                self.in_dest_dict = {e.attrs["id"]:e.text for e in self.in_dest_bs.find_all("s")}
            else:
                self.active = False
            self.count += 1
        elif name == "link" and self.active:
            xtargets = attrs["xtargets"]
            orig_indexes, dest_indexes = xtargets.split(";")
            orig_indexes = orig_indexes.strip()
            dest_indexes = dest_indexes.strip()
            if len(orig_indexes) > 0 and len(dest_indexes) > 0:
                orig_indexes = orig_indexes.split(" ")
                dest_indexes = dest_indexes.split(" ")
                try:
                    # text_orig = [self.in_orig_bs.find("s", {"id":i}).text.replace("\n", " ").strip() for i in orig_indexes]
                    # text_dest = [self.in_dest_bs.find("s", {"id":i}).text.replace("\n", " ").strip() for i in dest_indexes]
                    text_orig = [self.in_orig_dict[i].replace("\n", " ").strip() for i in orig_indexes]
                    text_dest = [self.in_dest_dict[i].replace("\n", " ").strip() for i in dest_indexes]
                    # Write to files
                    self.out_orig_fd.write(" ".join(text_orig) + "\n")
                    self.out_dest_fd.write(" ".join(text_dest) + "\n")
                except:
                    print("Error aligning files {} and {} at indexes {} and {} respectively".format(
                        self.origin_subtitles_file, self.destination_subtitles_file, orig_indexes, dest_indexes))
                    print("Skipping...")

    def endElement(self, name):
        """Signals the end of an element in non-namespace mode.

        The name parameter contains the name of the element type, just
        as with the startElement event."""
        if name == "linkGrp" and self.active:
            self.in_orig_fd.close()
            self.in_dest_fd.close()
            self.num_processed_subtitles += 1
            if self.start_time is None:
                self.start_time = time.time()
            # if self.num_processed_subtitles > 1:
            #     print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)

            elapsed_time = time.time() - self.start_time
            time_to_go = elapsed_time / self.num_processed_subtitles * \
                         (self.num_subtitles_to_process - self.num_processed_subtitles)

            str_to_print = "Processed {} / {} ({:.2f}% Elapsed time: {}. Time to go: {})".format(self.num_processed_subtitles,
                                                       self.num_subtitles_to_process,
                                                       self.num_processed_subtitles / self.num_subtitles_to_process * 100,
                                                       str(datetime.timedelta(seconds=elapsed_time)),
                                                       str(datetime.timedelta(seconds=time_to_go)))
            print(str_to_print, end="\r")
            self.active = False

    def close(self):
        if self.out_orig_fd is not None:
            self.out_orig_fd.close()
        if self.out_dest_fd is not None:
            self.out_dest_fd.close()

    def _get_num_subtitles_to_process(self):
        print("Gathering subtitles to process...")
        p = subprocess.Popen(["grep", '-c', "linkGrp", self.aligment_file], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        result, err = p.communicate()
        if p.returncode != 0:
            raise IOError(err)
        res = int(int(int(result.strip().split()[0]) / 2) / self.subsample_rate)
        print("Found {} subtitles to process.".format(res))
        return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preproces opensubtitles in two languages to produce a couple of files"
                                                 "with aligned texts that cna be used for automatic translation "
                                                 "training.")
    parser.add_argument("alignment_file",
                        type=str,
                        help="The file containing the alignement information in XCES format.")
    parser.add_argument("base_dir",
                        type=str,
                        help="The base dir where subtitles data is located for both languages to be preprocessed.")
    parser.add_argument("origin_output_text_file",
                        type=str,
                        help="The output file where the origin language texts will be written.")
    parser.add_argument("destination_output_text_file",
                        type=str,
                        help="The output file where the destination language texts will be written.")
    parser.add_argument("subsample_rate",
                        type=int,
                        help="The subsample rate")
    parser.add_argument("sample_index",
                        type=int,
                        help="The sample index (valid values are in {0, ..., subsample_rate-1}")

    args = parser.parse_args()

    handler = OpensubtitlesAlignementHandler(args.alignment_file, args.base_dir, args.origin_output_text_file,
                                             args.destination_output_text_file, subsample_rate=args.subsample_rate,
                                             sample_index=args.sample_index)
    xml.sax.parse(args.alignment_file, handler)
    handler.close()
