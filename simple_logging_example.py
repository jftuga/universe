import logging

LOGFILE="example.log"

def main():
    logging.basicConfig(filename=LOGFILE, format='%(asctime)s\t%(levelname)s\t%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    logging.info("a b c")

main()
