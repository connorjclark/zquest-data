#!/bin/sh
set -e

# OPTIMIZE_FLAGS="-Oz -s ENVIRONMENT=web" # PRODUCTION
OPTIMIZE_FLAGS="-s ASSERTIONS=2 -s SAFE_HEAP=1 -s STACK_OVERFLOW_CHECK=1 -g3" # DEBUG

# TODO: only needed for config stuff, but that isn't working yet.
# PRELOAD_FILE="--preload-file output/modules/default@/modules"

# --preload-file output/modules/default@/modules \
# -DALLEGRO_MACOSX \
mkdir -p build/wasm
emcc -o build/wasm/zc.js $OPTIMIZE_FLAGS \
  -Wno-narrowing \
  -DALLEGRO_LITTLE_ENDIAN -D__TIMEZONE__ \
  -DALLEGRO_MACOSX \
  -Ithird_party/allegro/include \
  -s MODULARIZE -s ALLOW_MEMORY_GROWTH=1 -s EXPORT_ALL=1 \
  -s FORCE_FILESYSTEM=1 \
  -s EXPORTED_RUNTIME_METHODS='["ccall","cwrap","FS"]' \
  -s TOTAL_MEMORY=40108032 \
  -Wno-macro-redefined \
  -s ERROR_ON_UNDEFINED_SYMBOLS=0 \
  $PRELOAD_FILE \
  lib/decode3.c third_party/allegro/src/file.c third_party/allegro/src/unicode.c third_party/allegro/src/libc.c third_party/allegro/src/lzss.c third_party/allegro/src/unix/*.c


# lib/decode2.c third_party/allegro/src/allegro.c third_party/allegro/src/file.c third_party/allegro/src/lzss.c third_party/allegro/src/unicode.c third_party/allegro/src/libc.c third_party/allegro/src/unix/*.c

# $(ls src/*.cpp | grep -Ev "(Get_MapData|Set_Mapdata|LINUX_Console|colourdata)" | xargs -I {} echo {})
