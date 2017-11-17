class Cmd(object):
    def __init__(self, action, *args, **kwargs):
        self.action = action


class CmdParser(object):

    @classmethod
    def parse(cls, cmd_str):
        cmd_str = cmd_str.strip()
        cmd_parts = cmd_str.split(' ', 1)
        if not cmd_parts:
            return None
        return Cmd(*cmd_parts)


