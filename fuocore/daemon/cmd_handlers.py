from abc import ABC, abstractmethod

from fuocore.daemon.utils import to_identifier, get_provider_name


def exec_cmd(app, cmd):
    print('exec:', cmd)
    if cmd.action == 'ls':
        handler = ProvidersHandler(app)
    elif cmd.action == 'play':
        handler = PlayerHandler(app)
    else:
        return 'Oops Unknown command!'        
    return handler.handle(cmd)


class AbstractHandler(ABC):
    def __init__(self, app):
        self.app = app

    @abstractmethod
    def handle(self, cmd):
        pass


class ProvidersHandler(AbstractHandler):
    def handle(self, cmd):
        if not cmd.args:
            return self.list_providers()
        else:
            path = cmd.args[0]
            name = get_provider_name(path)
            provider = self.app.get_provider(name)
            return self.list_songs(provider)

    def list_providers(self):
        provider_names = (provider.name for provider in
                          self.app.list_providers())
        return '\n'.join(provider_names)

    def list_songs(self, provider):
        return '\n'.join((str(song) for song in provider.songs))


class PlayerHandler(AbstractHandler):
    def handle(self, cmd):
        song_path = cmd.args[0]
        song_id = to_identifier(song_path)
        self.app.play(song_id)
        return 'OK'
