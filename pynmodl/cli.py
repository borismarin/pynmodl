"""NMODL parser/compiler.

Usage:
  pynmodl <command> <modfile>
  pynmodl (-h | --help)

Options:
  -h --help         Show this screen.
"""
from docopt import docopt


def pynmodl():
    arguments = docopt(__doc__, options_first=True, version='0.0.1')

    if arguments['<command>'] == 'compile':
        print('COMPILE!')
    elif arguments['<command>'] == 'validate':
        print('VALIDATE!')
    else:
        exit("{0} is not a command. See 'pynmodl --help'.".format(
            arguments['<command>']))


if __name__ == '__main__':
    pynmodl()
