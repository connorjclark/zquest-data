import logging
import re
import tempfile
import traceback
from typing import Dict
from dataclasses import dataclass
from .bytes import Bytes
from decode_wrapper import py_decode, py_encode
from .pretty_json import pretty_json_format
from .section_utils import SECTION_IDS, read_section, serialize
from .version import Version
from .bit_field import BitField
from .compat_rules import process_compat_rules
from . import constants

log = logging.getLogger('zquest')


def assert_equal(expected, actual):
    if expected != actual:
        raise Exception(f'expected {expected} but got {actual}')


@dataclass
class SectionHeader:
    id: bytes
    version: int
    cversion: int
    offset: int
    data_offset: int
    size: int
    extra: int


class ZeldaClassicReader:
    def __init__(self, path, opts={}):
        self.sections = {
            SECTION_IDS.HEADER: self.read_header,
            SECTION_IDS.TILES: self.read_tiles,
            SECTION_IDS.COMBOS: self.read_combos,
            SECTION_IDS.CSETS: self.read_csets,
            SECTION_IDS.DMAPS: self.read_dmaps,
            SECTION_IDS.MAPS: self.read_maps,
            SECTION_IDS.GUYS: self.read_guys,
            SECTION_IDS.WEAPONS: self.read_weapons,
            SECTION_IDS.LINKSPRITES: self.read_link_sprites,
            SECTION_IDS.ITEMS: self.read_items,
            SECTION_IDS.MIDIS: self.read_midis,
            SECTION_IDS.DOORS: self.read_doors,
            SECTION_IDS.RULES: self.read_rules,
            SECTION_IDS.INIT: self.read_init,
            SECTION_IDS.STRINGS: self.read_str,
        }

        with open(path, 'rb') as f:
            self.b = Bytes(bytearray(f.read()))

        self.path = path
        self.opts = opts
        self.section_fields = {}
        self.section_ok = {}
        self.errors = []
        self.combos = None
        self.tiles = None
        self.csets = None
        self.dmaps = None
        self.maps = None
        self.guys = None
        self.weapons = None
        self.link_sprites = None
        self.items = None
        self.midis = None
        self.rules = None
        self.init = None
        self.strings = None

    # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zq_class.cpp#L11817

    def read_qst(self):
        # read the header and decompress the data
        # https://github.com/ArmageddonGames/ZeldaClassic/blob/023dd17eaf6a969f47650cb6591cedd0baeaab64/src/zsys.cpp#L676

        with tempfile.TemporaryDirectory() as tmpdirname:
            outpath = f'{tmpdirname}/decoded.data'
            err, method, key = py_decode(self.path, outpath)

            # Only bother with the method or stupid key (which we can set to be anything)
            # so the _exact_ same bytes can be written back and verify reading and
            # writing works without error.
            self.method = method
            self.key = key
            if err != 0:
                raise Exception(f'error decoding: {err}')

            with open(outpath, "rb") as f:
                decoded = f.read()

        # remake the byte reader with the decoded data
        self.b = Bytes(bytearray(decoded))

        self.preamble = self.b.read(29)
        preambles = [
            b'AG Zelda Classic Quest File\n ',
            b'AG ZC Enhanced Quest File\n   ',
        ]
        if self.preamble not in preambles:
            raise Exception(f'unexpected preamble: {self.preamble}')

        # The preamble is actually 31 bytes, but we ignore the last two for comparison purposes above.
        self.b.advance(2)

        self.is_too_old = self.preamble == preambles[0]
        if self.is_too_old:
            # Really old qst files use a crappy format.
            # https://github.com/ArmageddonGames/ZQuestClassic/blob/6b0abe1f8a0f280ddc53647f2b9f5f2352b950eb/src/qst.cpp#L20934
            self.section_headers = {}

            # TODO read more of old quests
            for id in [SECTION_IDS.HEADER, SECTION_IDS.RULES]:
                self.section_headers[id] = SectionHeader(id=id, version=0, cversion=0,
                                                         offset=self.b.offset, data_offset=self.b.offset,
                                                         size=0, extra=None)
                self.sections[id](self.b, 0, 0)
                self.section_ok[id] = True

            log.warning(
                'qst file is pre-1.93, and is too old to read more than the header and rules sections')
            return

        if self.b.peek(4) != SECTION_IDS.HEADER:
            raise Exception('could not find HDR section')

        logging.debug('finding sections ...')
        self.section_headers = self.find_sections()

        first_section_id = next(iter(self.section_headers), None)
        if first_section_id != SECTION_IDS.HEADER:
            raise Exception(f'expected HDR to be first section, but got {first_section_id}')

        only_sections = self.opts['only_sections'] if 'only_sections' in self.opts else None
        for id in self.section_headers.keys():
            if id != SECTION_IDS.HEADER and only_sections != None and id not in only_sections:
                continue

            self.process_section(id)


    def find_sections(self):
        section_headers: Dict[bytes, SectionHeader] = {}
        start_of_sections_offset = self.b.offset
        previous_header = None

        while self.b.has_bytes():
            section_offset = self.b.offset
            header = self.read_section_header()

            # Sometimes there is garbage data between sections.
            # ex of a problematic qst file: 208/quests-1188722503-package-1st.qst (MAP section)
            if not re.match('\w{3,4}', header.id.decode('ascii', errors='ignore')):
                log.warning(
                    f'garbage section id: {header.id}, skipping ahead some bytes...')
                bytes_to_extend = 0
                while header and header.id not in vars(SECTION_IDS).values():
                    bytes_to_extend += 1
                    self.b.offset = section_offset + bytes_to_extend
                    try:
                        header = self.read_section_header()
                    except:
                        self.b.offset = section_offset
                        header = None

                log.warning(
                    f'found this many junk bytes between sections: {bytes_to_extend}')
                if previous_header:
                    log.warning(
                        f'assuming that the previous section ({previous_header.id}) size was wrong, and extended it:')
                    log.warning(
                        f'  {previous_header.size} -> {previous_header.size + bytes_to_extend}')
                    previous_header.size += bytes_to_extend
                else:
                    log.warning('just ignoring those bytes!')

            if not header:
                break

            if header.size > self.b.bytes_remaining():
                log.warning(
                    f'size for section id {header.id} is bigger than remaining, ignoring')
                break

            section_headers[header.id] = header
            previous_header = header
            self.b.advance(header.size)

        self.b.offset = start_of_sections_offset
        return section_headers

    # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zq_class.cpp#L5414
    def read_zgp(self):
        pass

    # https://github.com/ArmageddonGames/ZeldaClassic/blob/bdac8e682ac1eda23d775dacc5e5e34b237b82c0/src/zq_class.cpp#L6189
    # https://github.com/ArmageddonGames/ZeldaClassic/blob/20f9807a8e268172d0bd2b0461e417f1588b3882/src/qst.cpp#L2005
    # zdefs.h

    def read_header(self, section_bytes: Bytes, section_version, section_cversion):
        version = Version(None, None, self.preamble)
        # Older format needs zelda_version ahead of time to create the header field.
        if version.preamble == b'AG Zelda Classic Quest File\n ':
            offset = section_bytes.offset
            section_bytes.advance(1)
            version.zelda_version = section_bytes.read_int()
            section_bytes.offset = offset

        data, fields = read_section(
            section_bytes, SECTION_IDS.HEADER, version, section_version)
        self.header = data
        self.section_fields[SECTION_IDS.HEADER] = fields

        if hasattr(self.header, 'build'):
            self.version = Version(self.header.zelda_version, self.header.build)
        else:
            self.version = Version(self.header.zelda_version)
        log.debug(self.version)
        log.debug(self.header.title)


    def read_section_header(self):
        offset = self.b.offset
        id = bytes(self.b.read(4))
        version = self.b.read_int()
        cversion = self.b.read_int()
        if id == SECTION_IDS.RULES and version > 16:
            compatrule_version = self.b.read_long()
        else:
            compatrule_version = None
        size = self.b.read_long()
        data_offset = self.b.offset
        return SectionHeader(id=id, version=version, cversion=cversion,
                             offset=offset, data_offset=data_offset, size=size,
                             extra=compatrule_version)


    def process_section(self, id: bytes):
        header = self.section_headers[id]

        if id not in self.sections:
            log.debug(f'{id} v{header.version:<3}\t{header.size} (unhandled)')
            return

        log.debug(f'{id} v{header.version:<3}\t{header.size}')

        self.b.offset = header.data_offset
        section = self.sections[id]
        try:
            section(self.b, header.version, header.cversion)
            self.section_ok[id] = True
        except Exception as e:
            self.section_ok[id] = False
            error = ''.join(traceback.TracebackException.from_exception(e).format())
            log.error(error)
            self.errors.append(error)
            return

        bytes_read = self.b.offset - header.data_offset
        remaining = header.size - bytes_read
        if remaining != 0:
            self.section_ok[id] = False
            log.warning(
                f'{id} section did not consume expected number of bytes. remaining: {remaining}')


    # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zq_class.cpp#L9184
    def read_tiles(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(section_bytes, SECTION_IDS.TILES,
                                    self.version, section_version)
        self.tiles = data
        self.section_fields[SECTION_IDS.TILES] = fields

        for tile in self.tiles:
            format = tile.format if hasattr(tile, 'format') else 1
            compressed_pixels = tile.compressed_pixels
            match format:
                case 1:
                    # 1 byte per 2 pixels
                    pixels = []
                    for val in compressed_pixels:
                        pixels.append(val & 0xF)
                        pixels.append((val >> 4) & 0xF)
                    tile.pixels = pixels
                case 0 | 2 | 3:
                    tile.pixels = compressed_pixels
                case _:
                    raise Exception(f'unexpected format {format}')

    # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/qst.cpp#L13150

    def read_combos(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(section_bytes, SECTION_IDS.COMBOS,
                                    self.version, section_version)
        self.combos = data
        self.section_fields[SECTION_IDS.COMBOS] = fields

    # https://github.com/ArmageddonGames/ZeldaClassic/blob/bdac8e682ac1eda23d775dacc5e5e34b237b82c0/src/qst.cpp#L15411
    def read_csets(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(section_bytes, SECTION_IDS.CSETS,
                                    self.version, section_version)
        self.csets = data
        self.section_fields[SECTION_IDS.CSETS] = fields

        color_data = self.csets.color_data
        i = 0
        cset_colors = []
        while i < len(color_data):
            colors = []
            for _ in range(16):
                r = color_data[i] * 4
                i += 1
                g = color_data[i] * 4
                i += 1
                b = color_data[i] * 4
                i += 1
                a = 0 if _ == 0 else 255
                colors.append((r, g, b, a))

            if all(r + g + b == 0 for (r, g, b, a) in colors):
                colors = []

            cset_colors.append(colors)

        self.cset_colors = cset_colors

    def read_dmaps(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(section_bytes, SECTION_IDS.DMAPS, self.version, section_version)
        self.dmaps = data
        self.section_fields[SECTION_IDS.DMAPS] = fields

    def read_maps(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(section_bytes, SECTION_IDS.MAPS, self.version, section_version)
        self.maps = data
        self.section_fields[SECTION_IDS.MAPS] = fields

    def read_guys(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(section_bytes, SECTION_IDS.GUYS, self.version, section_version)
        self.guys = data
        self.section_fields[SECTION_IDS.GUYS] = fields

    def read_weapons(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(section_bytes, SECTION_IDS.WEAPONS,
                                    self.version, section_version)
        self.weapons = data
        self.section_fields[SECTION_IDS.WEAPONS] = fields

    def read_link_sprites(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(section_bytes, SECTION_IDS.LINKSPRITES,
                                    self.version, section_version)
        self.link_sprites = data
        self.section_fields[SECTION_IDS.LINKSPRITES] = fields

    def read_items(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(section_bytes, SECTION_IDS.ITEMS, self.version, section_version)
        self.items = data
        self.section_fields[SECTION_IDS.ITEMS] = fields

    def read_midis(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(section_bytes, SECTION_IDS.MIDIS, self.version, section_version)
        self.midis = data
        self.section_fields[SECTION_IDS.MIDIS] = fields

    def read_doors(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(section_bytes, SECTION_IDS.DOORS, self.version, section_version)
        self.doors = data
        self.section_fields[SECTION_IDS.DOORS] = fields

    def read_rules(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(section_bytes, SECTION_IDS.RULES, self.version, section_version)
        self.rules = data
        self.section_fields[SECTION_IDS.RULES] = fields

    def read_init(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(section_bytes, SECTION_IDS.INIT,
                                    self.version, section_version)
        self.init = data
        self.section_fields[SECTION_IDS.INIT] = fields

    def read_str(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(section_bytes, SECTION_IDS.STRINGS,
                                    self.version, section_version)
        self.strings = data
        self.section_fields[SECTION_IDS.STRINGS] = fields

    def save_qst(self, qst_path):
        if self.is_too_old:
            raise Exception(f'pre-1.93 quests currently cannot be saved')

        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(serialize(self))
            err = py_encode(tmp.name, qst_path, self.method, self.key)
            if err != 0:
                raise Exception(f'error encoding: {err}')

    def save_qst_no_serialize(self, qst_path):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(self.b.data)
            err = py_encode(tmp.name, qst_path, self.method, self.key)
            if err != 0:
                raise Exception(f'error encoding: {err}')

    def save_qst_no_serialize_no_compression(self, qst_path):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(self.b.data)
            err = py_encode(tmp.name, qst_path, -2, self.key)
            if err != 0:
                raise Exception(f'error encoding: {err}')

    def to_json(self):
        data = {
            'errors': self.errors,
            'header': self.header,
            'combos': self.combos,
            'tiles': self.tiles,
            'csets': self.csets,
            'dmaps': self.dmaps,
            'maps': self.maps,
            'guys': self.guys,
            'weapons': self.weapons,
            'link_sprites': self.link_sprites,
            'items': self.items,
            'midis': self.midis,
            'rules': self.rules,
            'init': self.init,
            'strings': self.strings,
        }
        return pretty_json_format(data)

    def get_quest_rules(self):
        if not self.rules:
            raise Exception('qst is too old')

        return BitField(constants.quest_rules, self.rules)

    def get_quest_rules_post_compat(self):
        """
            Many QRs are force set when the .qst is read. This function
            mimics that behavior.

            See:
            https://github.com/ArmageddonGames/ZQuestClassic/blob/3e20ca69332b818e8799746d7d1e3dfdf8e3afa5/src/qst.cpp#L2979-L2979
        """
        if not self.rules:
            raise Exception('qst is too old')

        rule_bytes = bytearray(100)
        rule_bytes[0:len(self.rules)] = self.rules
        rules = BitField(constants.quest_rules, rule_bytes)
        process_compat_rules(self, rules)
        return rules
