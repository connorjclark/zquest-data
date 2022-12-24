import argparse
from zquest.extract import ZeldaClassicReader

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('input', type=str)
args = parser.parse_args()

reader = ZeldaClassicReader(args.input)
reader.read_qst()

print(reader.header)
