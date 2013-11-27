from core import backup, settings
import argparse

def parsing_args():
    parser = argparse.ArgumentParser(
                                description='Make a backup in Mega service.')
    parser.add_argument('-s', metavar='FILE', type=str, nargs=1,
                       help='backup origin folder', dest='syncfile')
    parser.add_argument('-v', dest='verbose', metavar="X", type=int, default=5,
                       help='verbose level number')

    args = parser.parse_args()
    #print args
    return args

def main():

    b = backup.Backup(settings.get_config('local', 'base_directory'))
    b.detect_mode()
    b.run()


if __name__ == '__main__':
    options = parsing_args()
    main()
