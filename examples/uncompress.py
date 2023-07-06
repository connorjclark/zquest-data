import argparse
from zquest.extract import ZeldaClassicReader


def uncompress_qst(input_path, output_path):
    reader = ZeldaClassicReader(input_path, {'only_sections': []})
    reader.read_qst()
    reader.save_qst_no_serialize_no_compression(output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input', type=str)
    parser.add_argument('--output')
    args = parser.parse_args()

    uncompress_qst(args.input, args.output)
