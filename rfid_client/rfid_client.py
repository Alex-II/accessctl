import argparse, os, sys, logging


def set_up_logging(log_filepath = None, output_stdout = True):
    if output_stdout:
        pass

    if log_filepath:
        pass

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log_filepath', type=str, action='store', help='Give a filepath where to log stuff')


    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    if args.log_filepath:
        set_up_logging(args.log_filepath)
    else:
        set_up_logging(None)

if __name__ == "__main__":
    main()