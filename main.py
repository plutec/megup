from core import settings
import argparse

def parsing_args():
    parser = argparse.ArgumentParser(
                                description='Make a backup in Mega service.')
    parser.add_argument('-s', metavar='FOLDER', type=str, nargs=1,
                       help='backup origin folder', dest='syncfile')
    parser.add_argument('-v', dest='verbose', metavar="[1-5]", type=int, 
                        default=None, help='verbose level number')

    args = parser.parse_args()

    if args.verbose != None: #It is different of 0
        settings.set_config('global', 'log_level', str(args.verbose))

    return args

def main(options):
    
    #It's necesary charge after parse arguments
    from core import backup
    
    b = backup.Backup(settings.get_config('local', 'base_directory'))
    b.detect_mode()
    b.run()


if __name__ == '__main__':
    options = parsing_args()

    main(options)
