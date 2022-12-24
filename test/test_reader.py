import enum
import os
import unittest
import hashlib
from pathlib import Path
from copy import deepcopy

from zquest.extract import ZeldaClassicReader

os.makedirs('.tmp', exist_ok=True)


class TestReader(unittest.TestCase):
    def test_read_and_write_qst(self):
        reader = ZeldaClassicReader('test_data/1st.qst')
        reader.read_qst()
        self.assertEqual(reader.header.title, 'Original NES 1st Quest\x00st Quest')
        self.assertEqual(len(reader.combos), 160)
        self.assertEqual(reader.combos[0].tile, 316)
        self.assertEqual(len(reader.maps), 3)
        self.assertEqual(reader.maps[2].screens[0].color, 7)
        reader.save_qst('.tmp/1st-test.qst')

        reader = ZeldaClassicReader('.tmp/1st-test.qst')
        reader.read_qst()
        self.assertEqual(reader.header.title, 'Original NES 1st Quest\x00st Quest')
        self.assertEqual(len(reader.combos), 160)
        self.assertEqual(len(reader.maps), 3)
        self.assertEqual(reader.combos[0].tile, 316)

    def test_read_and_write_qst_no_delta(self):
        in_files = [
            'test_data/1st.qst',
            'test_data/Classic XD.qst',
            'test_data/lost_isle.qst',
            'test_data/firebird.qst',
            'test_data/bs/2.5/NewBS 3.1 - 1st Quest.qst',
            'test_data/1st-latest.qst',
            'test_data/InsertQuestTitleHere.qst',
        ]
        for in_file in in_files:
            reader = ZeldaClassicReader(in_file)
            reader.read_qst()
            reader.save_qst('.tmp/test.qst')

            original_hash = hashlib.md5(Path(in_file).read_bytes()).hexdigest()
            copy_hash = hashlib.md5(Path('.tmp/test.qst').read_bytes()).hexdigest()
            self.assertEqual(original_hash, copy_hash)

            for id, ok in reader.section_ok.items():
                # TODO fix these sections
                if in_file == 'test_data/InsertQuestTitleHere.qst':
                    if id in [b'INIT', b'GUY ']:
                        continue
                if in_file == 'test_data/1st-latest.qst':
                    if id in [b'INIT', b'CSET']:
                        continue
                if not ok:
                    raise Exception(f'{in_file}: failed to parse section {id}')

    def test_modify_qst(self):
        reader = ZeldaClassicReader('test_data/1st.qst')
        reader.read_qst()
        reader.combos[0].tile = 1234
        reader.maps[2].screens[0].color = 9
        reader.save_qst('.tmp/1st-test.qst')

        reader = ZeldaClassicReader('.tmp/1st-test.qst')
        reader.read_qst()
        self.assertEqual(len(reader.combos), 160)
        self.assertEqual(reader.combos[0].tile, 1234)
        self.assertEqual(reader.maps[2].screens[0].color, 9)

    def test_modify_qst_add_combo(self):
        reader = ZeldaClassicReader('test_data/1st.qst')
        reader.read_qst()
        reader.combos.append(deepcopy(reader.combos[0]))
        reader.save_qst('.tmp/1st-test.qst')

        reader = ZeldaClassicReader('.tmp/1st-test.qst')
        reader.read_qst()
        self.assertEqual(len(reader.combos), 161)
        self.assertEqual(reader.combos[0].tile, 316)
        self.assertEqual(reader.combos[160].tile, 316)
        self.assertEqual(reader.maps[2].screens[0].color, 7)

    def test_modify_qst_add_map(self):
        reader = ZeldaClassicReader('test_data/1st.qst')
        reader.read_qst()
        self.assertEqual(len(reader.maps), 3)
        self.assertEqual(reader.maps[0].screens[10].str, 6)
        reader.maps.append(deepcopy(reader.maps[0]))
        reader.save_qst('.tmp/1st-test.qst')

        reader = ZeldaClassicReader('.tmp/1st-test.qst')
        reader.read_qst()
        self.assertEqual(len(reader.maps), 4)
        self.assertEqual(reader.maps[0].screens[10].str, 6)
        self.assertEqual(reader.maps[3].screens[10].str, 6)
        self.assertEqual(reader.combos[0].tile, 316)


if __name__ == '__main__':
    unittest.main()
