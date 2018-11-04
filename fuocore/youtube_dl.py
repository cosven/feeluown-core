# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

import youtube_dl
from youtube_dl.utils import DownloadError

logger = logging.getLogger(__name__)


class Logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def propress_hook(d):
    """
    A list of functions that get called on download
    progress, with a dictionary with the entries
    * status: One of "downloading", "error", or "finished".

    If status is one of "downloading", or "finished", the
    following properties may also be present:
    * filename: The final filename (always present)
    * tmpfilename: The filename we're currently writing to
    """
    if d['downloading'] == 'downloading':
        logger.info('downloading and write to {}'.format(d['filename']))
    if d['status'] == 'finished':
        logger.info('Done downloading, now converting ...')


def gen_options():
    default_tpl = '~/Music/local/%(title)s.%(ext)s'
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': default_tpl,
        'verbose': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': Logger(),
        'progress_hooks': [propress_hook],
    }
    return ydl_opts


def download(url):
    opts = gen_options()
    with youtube_dl.YoutubeDL(opts) as ydl:
        try:
            ydl.download([url])
        except DownloadError as e:
            logger.exception("error dowloading vedio: {}".format(e.message))


if __name__ == '__main__':
    import sys
    url = sys.argv[1]
    download(url)
