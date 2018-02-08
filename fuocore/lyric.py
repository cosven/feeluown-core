import re


def parse(content):
    """
    Reference: https://github.com/osdlyrics/osdlyrics/blob/master/python/lrc.py
    """
    ms_sentence_map = dict()
    sentence_pattern = re.compile(r'\[(\d+(:\d+){0,2}(\.\d+)?)\]')
    lines = content.splitlines()
    for line in lines:
        m = sentence_pattern.search(line, 0)
        if m:
            time_str = m.group(1)
            mileseconds = 0
            unit = 1000
            for num in time_str.split(':').reverse():
                mileseconds += float(num) * unit
                unit *= 60
            sentence = line[m.end():]
            ms_sentence_map[mileseconds] = sentence
    return ms_sentence_map


def _find_in_sorted_list(element, l):
    """
    find a range that element in and return the start element
    """
    length = len(l)
    for index, current in enumerate(l):
        if any((index == 0 and element <= current,
                index >= length - 1)) or \
                (current <= element < l[index+1]):
            return current


class LyricHelper(object):
    def __init__(self, lyric):
        self.lyric = lyric
        self._p_s_map = None  # position sentence map

    def get_s(self, position):
        """get sentence by position"""
        if not self.lyric:
            return ''
        if self._p_s_map is None:
            self._p_s_map = parse(self.lyric)
        positions = self._p_s_map.keys()  # sorted
        return _find_in_sorted_list(position, positions)
