import argparse
from zquest.extract import ZeldaClassicReader
from zquest.section_utils import SECTION_IDS

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('input', type=str)
args = parser.parse_args()

reader = ZeldaClassicReader(args.input, {'only_sections': [SECTION_IDS.HEADER]})
reader.read_qst()

print(reader.header)
