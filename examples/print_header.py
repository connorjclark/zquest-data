import argparse
from zquest.extract import ZeldaClassicReader
from zquest.section_utils import SECTION_IDS

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('input', type=str)
args = parser.parse_args()

reader = ZeldaClassicReader(args.input, {'only_sections': [SECTION_IDS.HEADER]})
reader.read_qst()

for key, value in reader.header.__dict__.items():
    print(key.ljust(15), value)

print('\nSections:')
for header in reader.section_headers.values():
    id = header.id.decode('utf-8').strip()
    size = str(header.size)
    size_human = str(round(header.size / 1024))
    print(id.ljust(5), size.rjust(10), size_human.rjust(7), 'KB')
