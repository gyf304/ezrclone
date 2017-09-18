import os
import sys
import json
import argparse

from add import add
from reset import reset
from pushpull import push, pull
from init import init

COMMANDS = {
    'add': add,
    'reset': reset,
    'push': push,
    'pull': pull,
    'init': init
}

ARGS = [
    (('command', ), {'choices': list(COMMANDS)}),
    (('-q', '--quiet'), {'action': 'store_true'}),
    (('-y', '--yes'), {'action': 'store_true'}),
    (('-v', '--verbose'), {'action': 'count', 'default': 0})
]


def main():
    parser = argparse.ArgumentParser()
    for (args, kwargs) in ARGS:
        parser.add_argument(*args, **kwargs)
    parser.add_argument('options', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    yes = args.yes or args.quiet
    out_file = sys.stdout
    err_file = sys.stderr
    ret = 1
    if args.quiet:
        null_file = open(os.devnull, 'w')
        out_file = null_file
        err_file = null_file
    try:
        ret = COMMANDS[args.command](options=args.options, out_file=out_file,
                                     err_file=err_file, verbose=args.verbose, yes=yes)
    except KeyboardInterrupt:
        print('Quitting', file=err_file)
    finally:
        if args.quiet:
            null_file.close()
        sys.exit(ret)


if __name__ == '__main__':
    main()
