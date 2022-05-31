import io
import logging
import os
import re
import tempfile
import traceback
from .bytes import Bytes
from decode_wrapper import py_decode, py_encode
from .pretty_json import pretty_json_format
from .section_utils import SECTION_IDS, read_section, serialize
from .version import Version


def assert_equal(expected, actual):
    if expected != actual:
        raise Exception(f'expected {expected} but got {actual}')


class ZeldaClassicReader:
    def __init__(self, path):
        with open(path, 'rb') as f:
            self.b = Bytes(io.BytesIO(f.read()))

        self.path = path
        self.section_fields = {}
        self.section_versions = {}
        self.section_cversions = {}
        self.section_offsets = {}
        self.section_lengths = {}
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

        outpath = 'output/decoded.data'
        os.makedirs('output', exist_ok=True)
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
        self.b.f.close()
        self.b = Bytes(io.BytesIO(decoded))

        self.preamble = self.b.read(29)
        preambles = [
            b'AG Zelda Classic Quest File\n ',
            b'AG ZC Enhanced Quest File\n   ',
            b'Zelda Classic Quest File     ',
        ]
        if self.preamble not in preambles:
            raise Exception(f'unexpected preamble: {self.preamble}')

        if self.preamble == preambles[0]:
            # Really old qst files use a crappy format.
            # https://github.com/ArmageddonGames/ZeldaClassic/blob/2.55-master/src/qst.cpp#L20934
            self.read_header(self.b, None, None)
            # TODO: probably won't ever bother reading quests this old
            logging.warning(
                'qst file is pre-1.93, and is too old to read more than the header section')
            return

        # Skip ahead to the beginning of the HDR section.
        header_start = decoded.find(b'HDR ')
        if header_start == -1:
            raise Exception('could not find HDR section')
        self.b.f.seek(header_start)

        # actually read the data now
        while self.b.has_bytes():
            self.read_section()

    # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zq_class.cpp#L5414
    def read_zgp(self):
        id, section_version, section_cversion = self.read_section_header()
        assert_equal(SECTION_IDS.GRAPHICSPACK, id)

        while self.b.has_bytes():
            self.read_section()

    # https://github.com/ArmageddonGames/ZeldaClassic/blob/bdac8e682ac1eda23d775dacc5e5e34b237b82c0/src/zq_class.cpp#L6189
    # https://github.com/ArmageddonGames/ZeldaClassic/blob/20f9807a8e268172d0bd2b0461e417f1588b3882/src/qst.cpp#L2005
    # zdefs.h

    def read_header(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(section_bytes, SECTION_IDS.HEADER,
                                    Version(None, None, self.preamble), section_version)
        self.header = data
        self.section_fields[SECTION_IDS.HEADER] = fields

        if hasattr(self.header, 'build'):
            self.version = Version(self.header.zelda_version, self.header.build)
        else:
            self.version = Version(self.header.zelda_version)
        logging.debug(self.version)
        logging.debug(self.header.title)

    def read_section_header(self):
        id = self.b.read(4)
        section_version = self.b.read_int()
        section_cversion = self.b.read_int()
        return (id, section_version, section_cversion)

    def read_section(self):
        offset = self.b.bytes_read()
        id, section_version, section_cversion = self.read_section_header()
        size = self.b.read_long()

        # Sometimes there is garbage data between sections.
        if not re.match("\w{3,4}", id.decode("ascii", errors="ignore")):
            logging.warning(f"garbage section id: {id}, skipping ahead some bytes...")
            while id not in vars(SECTION_IDS).values():
                self.b.advance(-12 + 1)
                offset = self.b.bytes_read()
                id, section_version, section_cversion = self.read_section_header()
                size = self.b.read_long()

        self.section_offsets[id] = offset
        self.section_versions[id] = section_version
        self.section_cversions[id] = section_cversion

        sections = {
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
            SECTION_IDS.INITDATA: self.read_init,
            SECTION_IDS.STRINGS: self.read_str,
        }

        if size > self.b.length - self.b.bytes_read():
            logging.warning('section size is bigger than rest of data, clamping')
            size = self.b.length - self.b.bytes_read()

        self.section_lengths[id] = size
        section_bytes = Bytes(io.BytesIO(self.b.read(size)))
        if id in sections:
            ok = True
            logging.debug(f'{id} {section_version}\t{section_cversion}\t{size}')

            try:
                sections[id](section_bytes, section_version, section_cversion)
            except Exception as e:
                ok = False
                error = "".join(traceback.TracebackException.from_exception(e).format())
                logging.error(error)
                self.errors.append(error)

            remaining = size - section_bytes.bytes_read()
            if remaining != 0:
                ok = False
                logging.warning(
                    '%r section did not consume expected number of bytes. remaining: %r', id, remaining)

            self.section_ok[id] = ok
        else:
            logging.debug('unhandled section %r %r', id, size)
            pass

    def read_gpak(self, section_version, section_cversion):
        pass

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
        data, fields = read_section(section_bytes, SECTION_IDS.INITDATA,
                                    self.version, section_version)
        self.init = data
        self.section_fields[SECTION_IDS.INITDATA] = fields

    def read_str(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(section_bytes, SECTION_IDS.STRINGS,
                                    self.version, section_version)
        self.strings = data
        self.section_fields[SECTION_IDS.STRINGS] = fields

    def save_qst(self, qst_path):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(serialize(self))
            err = py_encode(tmp.name, qst_path, self.method, self.key)
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
