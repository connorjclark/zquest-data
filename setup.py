from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

# allegro_source_files = [
#   'allegro.c',
#   'file.c',
#   # 'unix/ufile.c',
#   'lzss.c',
#   'libc.c',
#   'unicode.c',
#   'config.c',
#   'mac/mdrv.c',
#   # 'mac/msnd.c',
#   # 'system.c',
# ]
# allegro_sources = [f'third_party/allegro/src/{x}' for x in allegro_source_files]

# allegro_include_files = [
#   'system.h',
#   'timer.h',
#   'keyboard.h',
#   'mouse.h',
#   'gfx.h',
#   'midi.h',
#   'digi.h',
#   'internal/alconfig.h',
#   'platform/almac.h',
# ]
# allegro_includes = [f'third_party/allegro/include/allegro/{x}' for x in allegro_include_files]

decode_extension = Extension(
  name='decode_wrapper',
  sources=['src/decode_wrapper.pyx', 'lib/file.c', 'third_party/allegro/src/unicode.c', 'third_party/allegro/src/libc.c', 'third_party/allegro/src/lzss.c', 'lib/al_file.c'],
  include_dirs=['lib', 'third_party/allegro/include'],
  # includes=["third_party/allegro/include/allegro/platform/almac.h"],
  # extra_compile_args=[f'-include{x}' for x in allegro_includes]
  # extra_compile_args=['-undefined dynamic_lookup'],
  # libraries=['allegro4_file'],
  # library_dirs=['third_party/allegro'],
  # extra_objects=["third_party/allegro/allegro4_file.a"]
)
setup(
  name='decode_wrapper',
  ext_modules=cythonize([decode_extension], language_level = '3'),
)
