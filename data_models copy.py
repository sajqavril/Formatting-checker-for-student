import parselmouth as pm
import numpy as np
import os
import editdistance
import datetime
import pandas as pd
import re
import zipfile
import xlsxwriter
import argparse

#################################################################
# Global Constant
#################################################################

VALIDFILETYPE = "ooTextFile"
TEXTGRID = "TextGrid"
SOUND = "Sound 2"
INTERVALTIER = "IntervalTier"
TEXTTIER = "TextTier"
STUDENT_ANDREW_ID_LIST = ["Test_Student1","Test_Student2"]
STUDENT_ANDREW_ID_LIST.extend(["jiaqi{:d}".format(i) for i in range(8)])
BASE_DIR = os.path.dirname(__file__) # set the directory that stores all the output files in the location of the distributed package/directory


#################################################################
# Base Tier Class
# overloaded by IntervalTier and TextTier
#################################################################
class BaseTier(object):
    '''
    A container for all types of tier
    will be implemented as either IntervalTier or TextTier
    '''

    def __init__(self, tier_text) -> None:
        '''
        Initializes the universal attributes of tier: 
        class, name, xmin, xmax, size, transcript, total time.
        @type tier: a tier object; single item in the TextGrid list.
        @param text_type:  TextGrid format
        @param t_time:  Total time of TextGrid file.
        @param classid:  Type of tier (point or interval).
        @param nameid:  Name of tier.
        @param xmin:  xmin of the tier.
        @param xmax:  xmax of the tier.
        @param size:  Number of entries in the tier
        @param transcript:  The raw transcript for the tier.
        '''
        self.tier_text = tier_text 
        self.t_time = 0
        self.classid = ""
        self.nameid = ""
        self.xmin = 0
        self.xmax = 0
        self.size = 0
        self.transcript = ""
        self.tier_info = ""
        self.tier_labels = []
        self._make_info()

    def __iter__(self):
        return self
    
    def _make_info(self):
        """
        Figures out most attributes of the tier object:
        classid, nameid, xmin, xmax, size, transcript.
        """

        trans = "([\S\s]*)"
        classid = " +class = \"(.*)\" *[\r\n]+"
        nameid = " +name = \"(.*)\" *[\r\n]+"
        xmin = " +xmin = (\d+\.?\d*[e\-\d*]*) *[\r\n]+"
        xmax = " +xmax = (\d+\.?\d*[e\-\d*]*) *[\r\n]+"
        size = " +\S+: size = (\d+) *"
        
        m = re.compile(classid + nameid + xmin + xmax + size + trans)
        try:
            self.tier_info = m.findall(self.tier_text)[0]
        except:
            print("ERR _make_info: ", self.tier_text)
        self.classid = self.tier_info[0]
        self.nameid = self.tier_info[1].strip()
        self.xmin = float(self.tier_info[2])
        self.xmax = float(self.tier_info[3])
        if self.size != None:
            self.size = int(self.tier_info[4])
        self.transcript = self.tier_info[-1]
        self.tier_labels = self._make_tier_labels()

        assert self.size == len(self.tier_labels), "The size {:d} of the tier {:s} and \
            the detected number of labels of {:d} do not match!".format(self.size, self.nameid, len(self.tier_labels))

    def _make_tier_labels(self):
        """
        @return: List of the information that stored in the tier
        """
        return NotImplementedError
    
    def tier_labels(self):
        """
        @return: Either the segmentation details or the points details of the tier.
        Depending on which specific type of the Tier that processed
        """
        
        return self.tier_labels

    def transcript(self):
        """
        @return:  Transcript of the tier, as it appears in the file.
        """

        return self.transcript

    def time(self, non_speech_char="."):
        """
        @return: Utterance time of a given tier.
        Screens out entries that begin with a non-speech marker.
        """

        total = 0.0
        if self.classid != TEXTTIER:
            for (time1, time2, utt) in self.simple_transcript:
                utt = utt.strip()
                if utt and not utt[0] == ".":
                    total += (float(time2) - float(time1))
        return total

    def tier_name(self):
        """
        @return:  Tier name of a given tier.
        """

        return self.nameid

    def classid(self):
        """
        @return:  Type of transcription on tier.
        """

        return self.classid

    def min_max(self):
        """
        @return:  (xmin, xmax) tuple for a given tier.
        """

        return (self.xmin, self.xmax)


    def __repr__(self):
        return "<{:s} \"{:s}\" (%.2f, %.2f) %.2f%%>" % (self.classid, self.nameid, self.xmin, self.xmax, 100*self.time()/self.t_time)

    def __str__(self):
        return self.__repr__() + "\n  " + "\n  ".join(" ".join(row) for row in self.tier_labels)

#################################################################
# IntervalTier Class
#################################################################

class IntervalTier(BaseTier):
    """ 
    A container for IntervalTier instance
    """

    def __init__(self, tier) -> None:
        super().__init__(tier)

    def _make_tier_labels(self):
        """
        @return:  Labels of the tier, in form of [(start_time, end_time, label)]
        """

        label_head = " +\S+ \[\d+\]: *[\r\n]+"
        label_xmin = " +\S+ = (\S+) *[\r\n]+"
        label_xmax = " +\S+ = (\S+) *[\r\n]+"
        label_text = " +\S+ = \"([^\"]*?)\""
        
        trans_m = re.compile(label_head + label_xmin + label_xmax + label_text)
        tier_labels = trans_m.findall(self.transcript)
        self.tier_labels = [(float(tier_label[0].strip()), float(tier_label[1].strip()), tier_label[2].strip()) for tier_label in tier_labels]
        return self.tier_labels
    

#################################################################
# TextTier Class
#################################################################

class TextTier(BaseTier):
    """ 
    A container for TextTier instance
    It can sort the labels based on the name of the markers
    """

    def __init__(self, tier) -> None:
        super().__init__(tier)

    def _make_tier_labels(self):
        """
        @return:  Labels of the tier, in form of [(time, label)]
        """

        label_head = " +\S+ \[\d+\]: *[\r\n]+"
        label_number = " +\S+ = (\S+) *[\r\n]+"
        label_text = " +\S+ = \"([^\"]*?)\""
        
        trans_m = re.compile(label_head + label_number + label_text)
        tier_labels = trans_m.findall(self.transcript)
        self.tier_labels = [(float(tier_label[0].strip()), tier_label[1].strip()) for tier_label in tier_labels]
        self._sort_tier_labels()

        return self.tier_labels
    
    def _sort_tier_labels(self):
        """
        @return: 
        """

        assert self.tier_labels != None, "You should build the tier_labels first and then sort them all."
        self.sorted_tier_labels = [l for l in self.tier_labels]
        self.sorted_tier_labels.sort(key=lambda x:x[1], reverse=False)
    
class DefaultTextTier(object):
    """ 
    A container of a special TextTier instance, the default error bound for segmentation questions
    """
    def __init__(self, nameid, size, default_error_bound):
        self.nameid = nameid + "-error-bound"
        self.classid = TEXTTIER
        self.size = size
        self.default_error_bound = default_error_bound
        self.tier_labels = [(0., default_error_bound)]*size


#################################################################
# TextGrid Class
#################################################################

class TextGrid(object):
    """
    Class to manipulate the TextGrid format used by Praat.
    Separates each tier within this file into its own Tier object.  
    Each TextGrid object has a number of tiers (size), xmin, xmax, and tiers with their own attributes.
    """

    def __init__(self, textgrid_text):
        """
        Takes open read file as input, initializes attributes
        of the TextGrid file.
        @type textgrid_text: textgrid text
        @param size:  Number of tiers.
        @param xmin: xmin.
        @param xmax: xmax.
        @param t_time:  Total time of TextGrid file.
        @type tiers:  A list of tier objects.
        """

        self.textgrid_text = textgrid_text
        self.nameid = ""
        self.classid = ""
        self.size = 0
        self.xmin = 0
        self.xmax = 0
        self.t_time = 0
        self.tiers = self._find_tiers()

        assert self.size == len(self.tiers), "The size {:d} in the textgrid {:s} does \
            not match the detected tiers {:d}".format(self.size, self.nameid, len(self.tiers))

    def __iter__(self):
        for tier in self.tiers:
            yield tier

    def next(self):
        if self.idx == (self.size - 1):
            raise StopIteration
        self.idx += 1
        return self.tiers[self.idx]

    def _load_tiers(self, header):
        """
        Iterates over each tier and grabs tier information.
        """

        tiers = []

        tier_re = header + "[\s\S]+?(?=" + header + "|$$)"
        m = re.compile(tier_re)
        tier_iter = m.finditer(self.textgrid_text)
        
        for iterator in tier_iter:
            (begin, end) = iterator.span()
            tier_text = self.textgrid_text[begin:end]
            tier_class = BaseTier
            try: 
                tmp = tier_text.index(INTERVALTIER)
                tier_class = IntervalTier
            except: 
                try:
                    tmp = tier_text.index(TEXTTIER)
                    tier_class = TextTier
                except:
                    pass
            assert tier_class != BaseTier
            tiers.append(tier_class(tier_text))
        return tiers

    def _find_tiers(self):
        """
        Splits the textgrid file into substrings corresponding to tiers.
        """

        classid = " +class = \"(.*)\" *[\r\n]+"
        nameid = " +name = \"(.*)\" *[\r\n]+"
        xmin = " +xmin = (\d+\.?\d*[e\-\d*]*) *[\r\n]+"
        xmax = " +xmax = (\d+\.?\d*[e\-\d*]*) *[\r\n]+"
        size = " +size = (\d+) *[\r\n]+"
        tiers = " +\w+\? \<\w+\> *[\r\n]+" # corresponding to the text "tiers? <exists>" in the file
        # header = "\t\t\titem ?\[[^]]*\]:"
        header = "\n            item ?\[[^]]*\]:"
        
        m = re.compile(classid + nameid + xmin + xmax + tiers + size)
        try:
            file_info = m.findall(self.textgrid_text)[0]
        except:
            print("ERR _find_tiers: "+ self.textgrid_text)

        self.classid = file_info[0].strip()
        self.nameid = file_info[1].strip()
        self.xmin = float(file_info[2])
        self.xmax = float(file_info[3])
        self.t_time = self.xmax - self.xmin
        self.size = int(file_info[4])
        tiers = self._load_tiers(header)
        
        return tiers 
    
#################################################################
# Sound 2 Class
#################################################################

class Sound2(object):
    """
    A container for Sound 2 object.
    """

    def __init__(self, sound_text):
        """
        Initializes attributes of the Sound file: class, name, xmin, xmax
        size, transcript, total time.
        Utilizes text_type to guide how to parse the file.
        @type tier: a tier object; single item in the TextGrid list.
        @param text_type:  TextGrid format
        @param t_time:  Total time of TextGrid file.
        @param classid:  Type of tier (point or interval).
        @param nameid:  Name of tier.
        @param xmin:  xmin of the tier.
        @param xmax:  xmax of the tier.
        @param size:  Number of entries in the tier
        @param transcript:  The raw transcript for the tier.
        """

        self.sound_text = sound_text
        self.classid = ""
        self.nameid = ""
        self.xmin = 0
        self.xmax = 0
        self.nx = 0
        self.dx = 0
        self.x1 = 0
        self.ymin = 0
        self.ymax = 0
        self.ny = 0
        self.dy = 0
        self.y1 = 0
        self.z = None
        self.sound_info = ""
        self._make_info()

    def _make_info(self):

        trans = "([\S\s]*)"
        
        classid = " +class = \"(.*)\" *[\r\n]+"
        nameid = " +name = \"(.*)\" *[\r\n]+"
        xmin = " +xmin = (\d+\.?\d*[e\-\d*]*) *[\r\n]+"
        xmax = " +xmax = (\d+\.?\d*[e\-\d*]*) *[\r\n]+"
        nx = " +nx = (\d+\.?\d*[e\-\d*]*) *[\r\n]+"
        dx = " +dx = (\d+\.?\d*[e\-\d*]*) *[\r\n]+"
        x1 = " +x1 = (\d+\.?\d*[e\-\d*]*) *[\r\n]+"
        ymin = " +ymin = (\d+\.?\d*[e\-\d*]*) *[\r\n]+"
        ymax = " +ymax = (\d+\.?\d*[e\-\d*]*) *[\r\n]+"
        ny = " +ny = (\d+\.?\d*[e\-\d*]*) *[\r\n]+"
        dy = " +dy = (\d+\.?\d*[e\-\d*]*) *[\r\n]+"
        y1 = " +y1 = (\d+\.?\d*[e\-\d*]*) *[\r\n]+"
        pre_z = " +z \[\] \[\]: *[\r\n]+"
        z = " +z \[\d+\]: *[\r\n]+ +z (\[\d+\] \[\d+\] = \d+\.?\d*[e\-\d*]*) *[\r\n]+"
        
        m = re.compile(classid + nameid + xmin + xmax + nx + dx + x1 + ymin + ymax + ny + dy + y1 + pre_z + z)
        self.sound_info = m.findall(self.sound_text)[0]
        self.classid = self.sound_info[0]
        self.nameid = self.sound_info[1].strip()
        self.xmin = float(self.sound_info[2])
        self.xmax = float(self.sound_info[3])
        self.nx = int(self.sound_info[4])
        self.dx = float(self.sound_info[5])
        self.x1 = float(self.sound_info[6])
        self.ymin = float(self.sound_info[7])
        self.ymax = float(self.sound_info[8])
        self.ny = int(self.sound_info[9])
        self.dy = float(self.sound_info[10])
        self.y1 = float(self.sound_info[11])
        self.z = np.empty(shape=(self.ny, self.nx))
        # print(self.z.shape)
        
        zs = self.sound_info[12:]
        for z in zs:
            mm = re.compile("\[(\d+)\] \[(\d+)\] = (\d+\.?\d*[e\-\d*]*)")
            xyv = mm.findall(z)[0]
            x = int(xyv[0])
            y = int(xyv[1])
            v = float(xyv[2])
            self.z[x-1,y-1] = v

#################################################################
# Collection Class
#################################################################

class Collection(object):
    """
    Class to represent .Collection file, the files within can only be either 
    TextGrid type or Sound 2 type
    """

    def __init__(self, collection_text):

        self.collection_text = collection_text
        self.size = 0
        self.items = self._find_items() # Items are either TextGrid or Sound2
        assert int(self.size) == len(self.items), "Actual number of items {:d} does \
            not match the size attribute {:d} of the collection file".format(len(self.items), self.size)

    def __iter__(self):
        for item in self.items:
            yield item

    def next(self):
        if self.idx == (self.size - 1):
            raise StopIteration
        self.idx += 1
        return self.items[self.idx]

    def _load_items(self, header):
        """
        Iterates over each item and grabs tier information.
        """

        items = []

        item_re = header + "[\s\S]+?(?=" + header + "|$$)"
        m = re.compile(item_re)
        item_iter = m.finditer(self.collection_text)
        for iterator in item_iter:
            (begin, end) = iterator.span()
            item_info = self.collection_text[begin:end]
            classid = " +class = \"(.*)\" *[\r\n]+"
            m = re.compile(classid)
            try:
                item_class = m.findall(item_info)[0]
            except:
                print("ERR _load_items: "+ item_info)
            if item_class == "TextGrid":
                item_type = TextGrid
            elif item_class == "Sound 2":
                item_type = Sound2
            else:
                raise NotImplementedError("Only TextGrid and Sound 2 type are supported!")
            items.append(item_type(item_info))
        return items    

    def _find_items(self):
        """
        Splits the textgrid file into substrings corresponding to items.
        """

        # m = re.compile(r"""(?x)
        #    size\ =\ (.*)[\r\n]+
        #     """)
        size = "\n ?size = (\d+\.?\d*[e\-\d*]*) *[\r\n]+"
        m = re.compile(size)
        header = "\n    item \[\d+\]: *[\r\n]+"

        sizes = m.findall(self.collection_text)
        self.size = int(sizes[0])
        items = self._load_items(header) 
        
        return items