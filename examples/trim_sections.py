import argparse
from zquest.extract import ZeldaClassicReader
from zquest.section_utils import SECTION_IDS


def trim_qst(input_path, output_path, sections_to_trim):
    reader = ZeldaClassicReader(input_path, {'only_sections': []})
    reader.read_qst()

    ids = list(reader.section_headers)
    ids.sort(key=lambda id: -reader.section_headers[id].data_offset)

    data = reader.b.data.copy()
    for id in ids:
        if id not in sections_to_trim:
            continue

        section_header = reader.section_headers[id]
        section_start = section_header.offset
        section_end = section_header.data_offset + section_header.size
        del data[section_start:section_end]

    reader.b.data = data
    reader.save_qst_no_serialize(output_path)


if __name__ == '__main__':
    all_section_ids = [x for x in SECTION_IDS.__dict__.keys()]

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input', type=str)
    parser.add_argument('--output')
    parser.add_argument('--trim', nargs='*', choices=all_section_ids)
    args = parser.parse_args()

    sections_to_trim = [getattr(SECTION_IDS, s) for s in args.trim]
    trim_qst(args.input, args.output, sections_to_trim)
