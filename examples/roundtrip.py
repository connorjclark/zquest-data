import sys
import hashlib
from pathlib import Path
from zquest.extract import ZeldaClassicReader

in_file = sys.argv[1]
print(in_file)
reader = ZeldaClassicReader(in_file)
reader.read_qst()
reader.save_qst('.tmp/roundtrip.qst')

original_hash = hashlib.md5(Path(in_file).read_bytes()).hexdigest()
copy_hash = hashlib.md5(Path('.tmp/roundtrip.qst').read_bytes()).hexdigest()
if original_hash != copy_hash:
    print(f'roundtrip failed for {in_file}')
    exit(1)
