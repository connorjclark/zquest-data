import io
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

# TODO: deprecated, remove.


def read_data(dest, section_version, descriptors):
    for key, read in descriptors.items():
        if key in dest:
            raise f'already using key: {key}'

        value = None
        if isinstance(read, dict):
            for version_threshold, read_option in read.items():
                if section_version >= version_threshold:
                    value = read_option()
                    if isinstance(value, tuple):
                        value = value[0]
                    break
        else:
            value = read()

        if value is not None:
            dest[key] = value


class ZeldaClassicReader:
    def __init__(self, path):
        self.b = Bytes(open(path))
        self.path = path
        self.section_fields = {}
        self.section_versions = {}
        self.section_cversions = {}
        self.section_offsets = {}
        self.section_lengths = {}
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

    # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zq_class.cpp#L11817

    def read_qst(self):
        # read the header and decompress the data
        # https://github.com/ArmageddonGames/ZeldaClassic/blob/023dd17eaf6a969f47650cb6591cedd0baeaab64/src/zsys.cpp#L676

        # preambles = [
        #   b'AG Zelda Classic Quest File',
        #   b'AG ZC Enhanced Quest File',
        #   b'Zelda Classic Quest File',
        # ]
        # assert_equal(preamble, self.b.read(len(preamble)))

        outpath = './output/decoded.data'
        (err, key) = py_decode(self.path, outpath)
        # Only bother with the stupid key (which we can set to be anything)
        # so the _exact_ same bytes can be written back and verify reading and
        # writing works without error.
        self.key = key
        if err != 0:
            raise Exception(f'error decoding: {err}')

        with open(outpath, "rb") as f:
            decoded = f.read()

        # remake the byte reader with the decoded data
        header_start = decoded.find(b'HDR')
        if header_start == -1:
            raise Exception('could not find HDR section')
        self.b = Bytes(io.BytesIO(decoded))
        self.b.f.seek(header_start)

        # actually read the file now
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
        # p_iputw = 2 bytes = b.read_int()

        zelda_version = section_bytes.read_int()
        build = section_bytes.read_byte()
        pw_hash = section_bytes.read_str(16)
        internal = section_bytes.read_int()
        quest_number = section_bytes.read_byte()
        version = section_bytes.read_str(9)
        min_version = section_bytes.read_str(9)
        title = section_bytes.read_str(65)
        author = section_bytes.read_str(65)
        use_keyfile = section_bytes.read_byte()

        self.version = Version(zelda_version, build)
        print(self.version)
        # ...

        print('internal', internal)
        print('quest_number', quest_number)
        print('zelda_version', zelda_version)
        print('min_version', min_version)
        print('title', title)
        print('author', author)

    def read_section_header(self):
        id = self.b.read(4)
        section_version = self.b.read_int()
        section_cversion = self.b.read_int()
        return (id, section_version, section_cversion)

    def read_section(self):
        offset = self.b.bytes_read()
        id, section_version, section_cversion = self.read_section_header()
        size = self.b.read_long()
        self.section_offsets[id] = offset
        self.section_versions[id] = section_version
        self.section_cversions[id] = section_cversion

        # Sometimes there is garbage data between sections.
        if not re.match("\w{3,4}", id.decode("ascii", errors="ignore")):
            print(f"garbage section id: {id}, skipping ahead some bytes...")
            while id not in vars(SECTION_IDS).values():
                self.b.advance(-12 + 1)
                id, section_version, section_cversion = self.read_section_header()
                size = self.b.read_long()

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
        }

        if size > self.b.length - self.b.bytes_read():
            print('section size is bigger than rest of data, clamping')
            size = self.b.length - self.b.bytes_read()

        self.section_lengths[id] = size
        section_bytes = Bytes(io.BytesIO(self.b.read(size)))
        if id in sections:
            print(f'{id} {section_version}\t{section_cversion}\t{size}')

            try:
                sections[id](section_bytes, section_version, section_cversion)
            except Exception as e:
                error = "".join(
                    traceback.TracebackException.from_exception(e).format())
                print(error)
                self.errors.append(error)

            remaining = size - section_bytes.bytes_read()
            if remaining != 0:
                print(
                    'section did not consume expected number of bytes. remaining:', remaining)
        else:
            # print('unknown section', id, size)
            pass

    # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zdefs.h#L1370
    # def tfbit_bits(self, tfbit):
    #   print(tfbit)
    #   sizes = [-1, 4, 8, 16, 24, 32, -1]
    #   return sizes[tfbit]

    # https://github.com/ArmageddonGames/ZeldaClassic/blob/b56ba20bc6be4a8e4bf01c7c681238d545069baf/src/tiles.cpp#L2579

    def tilesize(self, format):
        if format == 5:
            return 1024
        if format == 4:
            return 768
        if format >= 1 and format <= 3:
            return 64 << format

        return 256

    def read_gpak(self, section_version, section_cversion):
        pass

    # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zq_class.cpp#L9184

    def read_tiles(self, section_bytes, section_version, section_cversion):
        # ZC250MAXTILES = 32760
        # NEWMAXTILES = 214500

        if self.version >= Version(zelda_version=0x254, build=41):
            tiles_used = section_bytes.read_long()
        else:
            tiles_used = section_bytes.read_int()

        tiles = []
        while section_bytes.has_bytes():
            tile_format = 1
            if self.version > Version(zelda_version=0x211, build=4):
                tile_format = section_bytes.read_byte()

            pixels = section_bytes.read_array(1, self.tilesize(tile_format))

            match tile_format:
                case 1:
                    # 1 byte per 2 pixels
                    pixels_expanded = []
                    for val in pixels:
                        pixels_expanded.append(val & 0xF)
                        pixels_expanded.append((val >> 4) & 0xF)
                    pixels = pixels_expanded
                case 0 | 2 | 3:
                    pass
                case _:
                    raise Exception(f'unexpected format {tile_format}')

            tiles.append(pixels)

        self.tiles = tiles

    # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/qst.cpp#L13150

    def read_combos(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(
            section_bytes, SECTION_IDS.COMBOS, self.version, section_version)
        self.combos = data
        self.section_fields[SECTION_IDS.COMBOS] = fields

    # https://github.com/ArmageddonGames/ZeldaClassic/blob/bdac8e682ac1eda23d775dacc5e5e34b237b82c0/src/qst.cpp#L15411
    def read_csets(self, section_bytes, section_version, section_cversion):
        # https://github.com/ArmageddonGames/ZeldaClassic/blob/0fddc19a02ccf62c468d9201dd54dcb834b764ca/src/colors.h#L47
        newerpsTOTAL = (6701 << 4)*3
        MAXLEVELS = 512
        PALNAMESIZE = 17

        color_data = section_bytes.read_array(1, newerpsTOTAL)

        palnames = []
        for _ in range(MAXLEVELS):
            palnames.append(section_bytes.read_str(PALNAMESIZE))

        palcycles = section_bytes.read_int()

        cycles = []
        for _ in range(palcycles):
            cycles.append({
                'first': section_bytes.read_array(1, 3),
                'count': section_bytes.read_array(1, 3),
                'speed': section_bytes.read_array(1, 3),
            })

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

        self.csets = {
            'color_data': color_data,
            'palnames': palnames,
            'cycles': cycles,
            'cset_colors': cset_colors,
        }

    def read_dmaps(self, section_bytes, section_version, section_cversion):
        num_dmaps = section_bytes.read_int()

        self.dmaps = []
        for _ in range(num_dmaps):
            dmap = {}
            self.dmaps.append(dmap)

            if section_version < 9:
                raise 'TODO'

            read_data(dmap, section_version, {
                'map': lambda: section_bytes.read_byte(),
                'level': {
                    5: lambda: section_bytes.read_int(),
                    0: lambda: section_bytes.read_byte(),
                },
                'xoff': lambda: section_bytes.read_byte(),
                'compass': lambda: section_bytes.read_byte(),
                'color': {
                    9: lambda: section_bytes.read_int(),
                    0: lambda: section_bytes.read_byte(),
                },
                'midi': lambda: section_bytes.read_byte(),
                'cont': lambda: section_bytes.read_byte(),
                'type': lambda: section_bytes.read_byte(),
                'grid': lambda: section_bytes.read_array(1, 8),
            })

            if self.version < Version(zelda_version=0x192, build=41):
                raise 'TODO'

            read_data(dmap, section_version, {
                'name': lambda: section_bytes.read_str(21),
                'title': lambda: section_bytes.read_str(21),
                'intro': lambda: section_bytes.read_str(73),
            })

            dmap['minimap'] = []
            for __ in range(4):
                entry = {}
                dmap['minimap'].append(entry)

                read_data(entry, section_version, {
                    'tile': {
                        11: lambda: section_bytes.read_long(),
                        0: lambda: section_bytes.read_int(),
                    },
                    'cset': lambda: section_bytes.read_byte(),
                })

            read_data(dmap, section_version, {
                'tmusic': lambda: section_bytes.read_array(1, 56),
                'tmusictrack':       {2: lambda: section_bytes.read_byte()},
                'active_subscreen':  {2: lambda: section_bytes.read_byte()},
                'passive_subscreen': {2: lambda: section_bytes.read_byte()},
                'di':                {3: lambda: section_bytes.read_array(1, 32)},
                'flags': {
                    6: lambda: section_bytes.read_long(),
                    4: lambda: section_bytes.read_byte(),
                },
            })

            if self.version > Version(zelda_version=0x192, build=41) and self.version < Version(zelda_version=0x193):
                # padding
                section_bytes.read_byte()

            read_data(dmap, section_version, {
                'sideview':           {10: lambda: section_bytes.read_byte()},
                'script':             {12: lambda: section_bytes.read_int()},
                'initD':              {12: lambda: section_bytes.read_array(4, 8)},
                'initD_label':        {13: lambda: section_bytes.read_array(1, 8 * 65)},
                'active_sub_script':  {14: lambda: section_bytes.read_int()},
                'passive_sub_script': {14: lambda: section_bytes.read_int()},
                'sub_initD':          {14: lambda: section_bytes.read_array(4, 8)},
                'sub_initD_label':    {14: lambda: section_bytes.read_array(1, 8 * 65)},
            })

    def read_maps(self, section_bytes, section_version, section_cversion):
        data, fields = read_section(
            section_bytes, SECTION_IDS.MAPS, self.version, section_version)
        self.maps = data
        self.section_fields[SECTION_IDS.MAPS] = fields

    def read_guys(self, section_bytes, section_version, section_cversion):
        if section_version <= 3:
            raise 'TODO'

        guys = []
        for _ in range(512):
            guy = {}
            guy['name'] = section_bytes.read_str(64)
            guys.append(guy)

        for i in range(512):
            guy = guys[i]

            guy['flags'] = section_bytes.read_long()
            guy['flags2'] = section_bytes.read_long()
            if section_version >= 36:
                raise 'TODO'  # ?

            guy['tile'] = section_bytes.read_int()
            guy['width'] = section_bytes.read_byte()
            guy['height'] = section_bytes.read_byte()
            guy['s_tile'] = section_bytes.read_int()
            guy['s_width'] = section_bytes.read_byte()
            guy['s_height'] = section_bytes.read_byte()
            guy['e_tile'] = section_bytes.read_int()

            guy['e_width'] = section_bytes.read_byte()
            guy['e_height'] = section_bytes.read_byte()
            guy['hp'] = section_bytes.read_int()
            guy['family'] = section_bytes.read_int()
            guy['cset'] = section_bytes.read_int()
            guy['anim'] = section_bytes.read_int()
            guy['e_anim'] = section_bytes.read_int()
            guy['frate'] = section_bytes.read_int()
            guy['e_frate'] = section_bytes.read_int()

            guy['dp'] = section_bytes.read_int()
            guy['wdp'] = section_bytes.read_int()
            guy['weapon'] = section_bytes.read_int()

            guy['rate'] = section_bytes.read_int()
            guy['hrate'] = section_bytes.read_int()
            guy['step'] = section_bytes.read_int()

            guy['homing'] = section_bytes.read_int()
            guy['grumble'] = section_bytes.read_int()
            guy['item_set'] = section_bytes.read_int()

            if section_version >= 22:
                guy['misc'] = section_bytes.read_array(4, 10)
            else:
                raise 'TODO'

            guy['bgsfx'] = section_bytes.read_int()
            guy['bosspal'] = section_bytes.read_int()
            guy['extend'] = section_bytes.read_int()

            if section_version >= 16:
                guy['defense'] = section_bytes.read_array(1, 19)

            if section_version >= 18:
                guy['hitsfx'] = section_bytes.read_byte()
                guy['deadsfx'] = section_bytes.read_byte()

            if section_version >= 22:
                guy['misc11'] = section_bytes.read_long()
                guy['misc12'] = section_bytes.read_long()

            if section_version > 24:
                section_bytes.read_array(1, 41 - 19)

            if section_version > 25:
                guy['txsz'] = section_bytes.read_long()
                guy['tysz'] = section_bytes.read_long()
                guy['hxsz'] = section_bytes.read_long()
                guy['hysz'] = section_bytes.read_long()
                guy['hzsz'] = section_bytes.read_long()

            if section_version > 26:
                section_bytes.read_long()
                section_bytes.read_long()
                section_bytes.read_long()
                section_bytes.read_long()
                section_bytes.read_long()

            if section_version >= 30:
                guy['frozentile'] = section_bytes.read_long()
                guy['frozencset'] = section_bytes.read_long()
                guy['frozenclock'] = section_bytes.read_long()
                guy['frozenmisc'] = section_bytes.read_array(2, 10)

        self.guys = guys

    def read_weapons(self, section_bytes, section_version, section_cversion):
        weapons = []

        if section_version > 2:
            num_weapons = section_bytes.read_int()
            for _ in range(num_weapons):
                weapon = {}
                weapon['name'] = section_bytes.read_str(64)
                weapons.append(weapon)

                if section_version < 5:
                    raise 'TODO'

            for i in range(num_weapons):
                weapon = weapons[i]
                weapon['tile'] = section_bytes.read_int()
                weapon['misc'] = section_bytes.read_byte()
                weapon['csets'] = section_bytes.read_byte()
                weapon['frames'] = section_bytes.read_byte()
                weapon['speed'] = section_bytes.read_byte()
                weapon['type'] = section_bytes.read_byte()
                if section_version >= 7:
                    weapon['script'] = section_bytes.read_int()
                    weapon['newtile'] = section_bytes.read_long()
        else:
            raise 'TODO'

        self.weapons = weapons

    def read_link_sprites(self, section_bytes, section_version, section_cversion):
        if section_version >= 6:
            raise 'TODO'

        walk = []
        for _ in range(4):
            walk.append({
                'tile': section_bytes.read_int(),
                'flip': section_bytes.read_byte(),
                'extend': section_bytes.read_byte(),
            })

        stab = []
        for _ in range(4):
            stab.append({
                'tile': section_bytes.read_int(),
                'flip': section_bytes.read_byte(),
                'extend': section_bytes.read_byte(),
            })

        slash = []
        for _ in range(4):
            slash.append({
                'tile': section_bytes.read_int(),
                'flip': section_bytes.read_byte(),
                'extend': section_bytes.read_byte(),
            })

        self.link_sprites = {
            'walk': walk,
            'stab': stab,
            'slash': slash
        }

    def read_items(self, section_bytes, section_version, section_cversion):
        items = []

        num_items = section_bytes.read_int()
        for _ in range(num_items):
            item = {}
            item['name'] = section_bytes.read_str(64)
            items.append(item)

        for i in range(num_items):
            item = items[i]
            if section_version < 25:
                raise 'TODO'

            if section_version > 35:
                item['tile'] = section_bytes.read_long()
            else:
                item['tile'] = section_bytes.read_int()

            item['misc'] = [section_bytes.read_byte()]
            item['csets'] = section_bytes.read_byte()
            item['frames'] = section_bytes.read_byte()
            item['speed'] = section_bytes.read_byte()
            item['delay'] = section_bytes.read_byte()
            item['ltm'] = section_bytes.read_long()

            if section_version > 31:
                item['family'] = section_bytes.read_long()
            else:
                item['family'] = section_bytes.read_byte()

            item['family_type'] = section_bytes.read_byte()

            if section_version >= 31:
                item['power'] = section_bytes.read_long()
            else:
                item['power'] = section_bytes.read_byte()

            if section_version < 41:
                item['flags'] = section_bytes.read_int()
            else:
                item['flags'] = section_bytes.read_long()

            item['script'] = section_bytes.read_int()
            item['count'] = section_bytes.read_byte()
            item['amount'] = section_bytes.read_int()
            item['collect_script'] = section_bytes.read_int()

            item['setmax'] = section_bytes.read_int()
            item['max'] = section_bytes.read_int()
            item['playsound'] = section_bytes.read_byte()

            item['initiald'] = section_bytes.read_array(4, 8)
            item['initiala'] = section_bytes.read_array(1, 2)

            item['wpn'] = section_bytes.read_array(1, 10)
            item['pickup_hears'] = section_bytes.read_byte()

            item['misc'].extend(section_bytes.read_array(4, 2))
            item['magic'] = section_bytes.read_byte()
            item['misc'].extend(section_bytes.read_array(4, 8))

            item['usesound'] = section_bytes.read_byte()

            if section_version >= 26:
                item['useweapon'] = section_bytes.read_byte()
                item['usedefense'] = section_bytes.read_byte()
                item['weaprange'] = section_bytes.read_long()
                item['weapduration'] = section_bytes.read_long()
                item['weap_pattern'] = section_bytes.read_array(4, 10)

        self.items = items

    # "readtunes" in qst.cpp
    def read_midis(self, section_bytes, section_version, section_cversion):
        if section_version < 4:
            raise 'TODO'

        def access_bit(data, num):
            base = int(num // 8)
            shift = int(num % 8)
            return (data[base] & (1 << shift)) >> shift

        midis = {}
        midi_tracks = [None for _ in range(252)]

        midi_flags = section_bytes.read(32)
        # print([access_bit(midi_flags,i) for i in range(len(midi_flags)*8)])

        midis['tunes'] = []
        for i in range(252):
            tune = {}
            midis['tunes'].append(tune)

            if access_bit(midi_flags, i) == 0:
                continue

            tune['title'] = section_bytes.read_str(36)
            tune['start'] = section_bytes.read_long()
            tune['loop_start'] = section_bytes.read_long()
            tune['loop_end'] = section_bytes.read_long()
            tune['loop'] = section_bytes.read_int()
            tune['volume'] = section_bytes.read_int()

            if section_version >= 3:
                tune['flags'] = section_bytes.read_byte()

            tune['format'] = section_bytes.read_byte()
            if tune['format'] != 0:
                raise 'bad format'

            tune['divisions'] = section_bytes.read_signed_int_big_endian()

            midi_tracks[i] = []
            for _ in range(32):
                length = section_bytes.read_long_big_endian()
                data = section_bytes.read(length)
                midi_tracks[i].append(data)

        self.midis = midis
        self.midi_tracks = midi_tracks

    def save_qst(self, qst_path):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(serialize(self))
            err = py_encode(tmp.name, qst_path, self.key)
            if err != 0:
                raise Exception(f'error encoding: {err}')

    def to_json(self):
        data = {
            'errors': self.errors,
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
        }
        return pretty_json_format(data)
