from setuptools.command.install import install
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import os
import subprocess

class MyInstall(install):
  def run(self):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    allegro_dir = f'{script_dir}/third_party/allegro'
    subprocess.run(['git', 'clone', '--depth', '1', '--branch', '4.4.3.1', 'https://github.com/liballeg/allegro5.git', allegro_dir])
    subprocess.run(['cmake', '.'], cwd=allegro_dir)
    install.run(self)


decode_extension = Extension(
  name='decode_wrapper',
  python_requires='>3.10.0',
  sources=[
    'src/zquest/decode_wrapper.pyx',
    'lib/decode.c',
    'lib/allegro_shims.c',
    'third_party/allegro/src/unicode.c',
    'third_party/allegro/src/file.c',
    'third_party/allegro/src/lzss.c',
    'third_party/allegro/src/libc.c',
  ],
  include_dirs=['lib', 'third_party/allegro/include'],
)
setup(
  name='zquest',
  version='0.1.0',
  url='https://github.com/connorjclark/zquest-data',
  install_requires=['numpy', 'Pillow'],
  ext_modules=cythonize([decode_extension], language_level = '3'),
  cmdclass={'install': MyInstall},
)
