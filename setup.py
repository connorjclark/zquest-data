from setuptools.command.install import install
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

class MyInstall(install):
  def run(self):
    # with tempfile.TemporaryDirectory() as tmpdir:
    #   print('created temporary directory', tmpdir)
      # subprocess.run(['git', 'clone', '--branch', '4.4.3.1', 'https://github.com/liballeg/allegro5.git', tmpdir], cwd=tmpdir)
      # subprocess.run(['cmake', '.'], cwd=tmpdir)
      # subprocess.run(['make'], cwd=tmpdir)
      # subprocess.run(['make', 'install'], cwd=tmpdir)
      # subprocess.run(['ldconfig'], cwd=tmpdir)

    install.run(self)


decode_extension = Extension(
  name='decode_wrapper',
  python_requires='>3.10.0',
  sources=[
    'src/decode_wrapper.pyx',
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
  name='decode_wrapper',
  version='0.1.0',
  install_requires=['numpy', 'Pillow'],
  ext_modules=cythonize([decode_extension], language_level = '3'),
  cmdclass={'install': MyInstall},
)
