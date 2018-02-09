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
