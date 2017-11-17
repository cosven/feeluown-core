def exec_cmd(cmd):
    if cmd.action == 'ls':
        return '\n'.join(['local'])
    return 'Oops Unknown command!'
