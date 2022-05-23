import context
from zquest.field import F

from zquest.section_utils import SECTION_IDS, get_section_field
from zquest.version import Version

positive_infinity = float('inf')
version = Version(zelda_version=positive_infinity, build=positive_infinity)

for id in vars(SECTION_IDS).values():
    try:
        field = get_section_field(id, version, positive_infinity)
        print(f'section {id}')
        print(field)
        print('\n')
    except:
        # TODO: haven't yet migrated all sections to new field structure
        pass
