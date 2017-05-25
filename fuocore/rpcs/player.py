from aiozmq import rpc

from fuocore.engine import get_backend


class PlayerHandler(rpc.AttrHandler):

    @rpc.method
    def current_song(self):
        player = get_backend()
        if player is None or player.playlist.current_song is None:
            return None

        return player.playlist.current_song.serialize()

