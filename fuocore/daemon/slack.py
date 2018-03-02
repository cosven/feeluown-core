import logging

from slacker import Slacker

__alias__ = 'mac 全局快捷键'
__version__ = '0.0.1'
__desc__ = 'mac 全局快捷键'


slack = Slacker('xoxp-2191824058-10322528134-68442022244-0f9d632a47')


def sync_status(song):
    if song is None:
        status_text = u"好像暂停了？"
    else:
        status_text = song.title + ' - ' + \
            ','.join([artist.name for artist in (song.artists or [])])
    profile = u'{"status_text": "%s", "status_emoji": ":musical_note:"}' % \
        status_text
    try:
        slack.users.profile.set(profile=profile)
    except:  # noqa
        pass


def enable(app):
    app.playlist.song_changed.connect(sync_status)
    pass


def disable(app):
    logger = logging.getLogger(__name__)
    logger.info('the developer is so stupid, cant disable this plugin')
