import os
import unittest
import hashlib
from pathlib import Path

from zquest.extract import ZeldaClassicReader
from examples.trim_sections import trim_qst
from zquest.section_utils import SECTION_IDS

os.makedirs('.tmp', exist_ok=True)


def get_section_sizes(reader):
    return {id: header.size for (id, header) in reader.section_headers.items()}


def hash_file(file):
    return hashlib.md5(Path(file).read_bytes()).hexdigest()


class TestTrim(unittest.TestCase):
    def get_hash(self, sections):
        trim_qst('test_data/1st.qst', '.tmp/1st-trim-test.qst', sections)
        return hash_file('.tmp/1st-trim-test.qst')

    def test_trim_qst(self):
        expected_title = 'Original NES 1st Quest\x00st Quest'

        self.assertEqual(self.get_hash([]), hash_file('test_data/1st.qst'))

        self.assertEqual(self.get_hash(
            [SECTION_IDS.TILES]), '7196e5c6fcb9e6c0ef7dc2f1fd31a1d9')
        reader = ZeldaClassicReader('.tmp/1st-trim-test.qst', {
            'only_sections': [SECTION_IDS.HEADER, SECTION_IDS.MAPS],
        })
        reader.read_qst()
        self.assertEqual(reader.header.title, expected_title)
        self.assertEqual(len(reader.maps), 3)
        self.assertEqual(reader.tiles, None)
        self.assertEqual(get_section_sizes(reader), {
            b'HDR ': 2240, b'RULE': 20, b'STR ': 5978, b'DOOR': 607, b'DMAP': 122882,
            b'MISC': 1732, b'MCLR': 35, b'ICON': 8, b'ITEM': 45826, b'WPN ': 18178, b'MAP ': 555914,
            b'CMBO': 2722, b'CMBA': 18432, b'CSET': 330498, b'MIDI': 32, b'CHT ': 169, b'INIT': 1034,
            b'GUY ': 97792, b'LINK': 165, b'SUBS': 14074, b'FFSC': 18592, b'SFX ': 32, b'DROP': 1380, b'FAVS': 804,
        })

        self.assertEqual(self.get_hash(
            [SECTION_IDS.TILES, SECTION_IDS.MAPS]), '21623d5f9cefbe238d3d9c94de82d0ae')
        reader = ZeldaClassicReader('.tmp/1st-trim-test.qst', {
            'only_sections': [SECTION_IDS.HEADER],
        })
        reader.read_qst()
        self.assertEqual(reader.header.title, expected_title)
        self.assertEqual(reader.maps, None)
        self.assertEqual(get_section_sizes(reader), {
            b'HDR ': 2240, b'RULE': 20, b'STR ': 5978, b'DOOR': 607, b'DMAP': 122882,
            b'MISC': 1732, b'MCLR': 35, b'ICON': 8, b'ITEM': 45826, b'WPN ': 18178,
            b'CMBO': 2722, b'CMBA': 18432, b'CSET': 330498, b'MIDI': 32, b'CHT ': 169, b'INIT': 1034,
            b'GUY ': 97792, b'LINK': 165, b'SUBS': 14074, b'FFSC': 18592, b'SFX ': 32, b'DROP': 1380, b'FAVS': 804,
        })


if __name__ == '__main__':
    unittest.main()
