import context
import argparse

from zquest.section_utils import SECTION_IDS, get_section_field
from zquest.version import Version

positive_infinity = float('inf')

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--version', type=lambda x: int(x, 16), default=positive_infinity)
parser.add_argument('--build', type=int, default=positive_infinity)
args = parser.parse_args()

version = Version(zelda_version=args.version, build=args.build)

for id in vars(SECTION_IDS).values():
    try:
        field = get_section_field(id, version, positive_infinity)
        print(f'section {id}')
        print(field)
        print('\n')
    except:
        # TODO: haven't yet migrated all sections to new field structure
        pass
