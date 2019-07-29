from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

decode_extension = Extension(
  name="decode_wrapper",
  sources=["src/decode_wrapper.pyx"],
  include_dirs=["lib"]
  # extra_compile_args=['-m32']
)
setup(
  name="decode_wrapper",
  ext_modules=cythonize([decode_extension], language_level = "3"),
)
