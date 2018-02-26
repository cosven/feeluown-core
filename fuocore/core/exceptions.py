class FuocoreException(Exception):

    def __str__(self):
        if self.args:
            return self.args[0]

        if hasattr(self, 'defualt_msg'):
            return self.defualt_msg


class NoBackendError(FuocoreException):
    defualt_msg = 'No backend have been set'
