// https://github.com/ArmageddonGames/ZeldaClassic/blob/023dd17eaf6a969f47650cb6591cedd0baeaab64/src/zsys.cpp

#include <stdbool.h>
#include <stdio.h>
#include <allegro/file.h>

#define EOF (-1)
#define ENC_METHOD_MAX 5

static int32_t seed = 0;
static int32_t enc_mask[ENC_METHOD_MAX] = {0x4C358938, 0x91B2A2D1, 0x4A7C1B87, 0xF93941E6, 0xFD095E94};
static int32_t pvalue[ENC_METHOD_MAX] = {0x62E9, 0x7D14, 0x1A82, 0x02BB, 0xE09C};
static int32_t qvalue[ENC_METHOD_MAX] = {0x3619, 0xA26B, 0xF03C, 0x7B12, 0x4E8F};
static char datapwd[8] = {('l' + 11), ('o' + 22), ('n' + 33), ('g' + 44), ('t' + 55), ('a' + 66), ('n' + 77), (0 + 88)};

int rand_007(int method)
{
  int16_t BX = seed >> 8;
  int16_t CX = (seed & 0xFF) << 8;
  int8_t AL = seed >> 24;
  int8_t C = AL >> 7;
  int8_t D = BX >> 15;
  AL <<= 1;
  BX = (BX << 1) | C;
  CX = (CX << 1) | D;
  CX += seed & 0xFFFF;
  BX += (seed >> 16) + C;
  //  CX += 0x62E9;
  //  BX += 0x3619 + D;
  CX += pvalue[method];
  BX += qvalue[method] + D;
  seed = (BX << 16) + CX;
  return (CX << 16) + BX;
}

PACKFILE *pack_fopen_password(const char *filename, const char *mode, const char *password) {
  printf("pw %s\n", password);
  printf("filename %s\n", filename);
	packfile_password(password);
	PACKFILE *new_pf = pack_fopen(filename, mode);
	packfile_password("");
	return new_pf;
}

uint64_t file_size_ex_password(const char *filename, const char *password)
{
  packfile_password(password);
  uint64_t new_pf = file_size_ex(filename);
  packfile_password("");
  return new_pf;
}

int decode_file_007(const char *srcfile, const char *destfile, const char *header, int method, bool packed, const char *password)
{
  FILE *normal_src = NULL, *dest = NULL;
  PACKFILE *packed_src = NULL;
  int tog = 0, c, r = 0, err;
  long size, i;
  short c1 = 0, c2 = 0, check1, check2;

  // open files
  size = file_size_ex_password(srcfile, password);
  printf("size %ld\n", size);

  if (size < 1)
  {
    return 1;
  }

  size -= 8; // get actual data size, minus key and checksums

  if (size < 1)
  {
    return 3;
  }

  if (!packed)
  {
    normal_src = fopen(srcfile, "rb");

    if (!normal_src)
    {
      return 1;
    }
  }
  else
  {
    printf("1..\n");
    packed_src = pack_fopen_password(srcfile, F_READ_PACKED, password);
    printf("2..\n");

    if (errno == EDOM)
    {
      packed_src = pack_fopen_password(srcfile, F_READ, password);
    }

    if (!packed_src)
    {
      return 1;
    }
  }

  printf("?1\n");
  printf("DESTFILE %s\n", destfile);
  dest = fopen(destfile, "wb");

  if (!dest)
  {
    if (packed)
    {
      pack_fclose(packed_src);
    }
    else
    {
      fclose(normal_src);
    }

    return 2;
  }

  // read the header
  err = 4;

  if (header)
  {
    for (i = 0; header[i]; i++)
    {
      if (packed)
      {
        if ((c = pack_getc(packed_src)) == EOF)
        {
          goto error;
        }
      }
      else
      {
        if ((c = fgetc(normal_src)) == EOF)
        {
          goto error;
        }
      }

      if (i < 20) printf("%c\n", c);
      if ((c & 255) != header[i])
      {
        err = 6;
        goto error;
      }

      --size;
    }
  }

  // read the key
  if (packed)
  {
    if ((c = pack_getc(packed_src)) == EOF)
    {
      goto error;
    }
  }
  else
  {
    if ((c = fgetc(normal_src)) == EOF)
    {
      goto error;
    }
  }

  seed = c << 24;

  if (packed)
  {
    if ((c = pack_getc(packed_src)) == EOF)
    {
      goto error;
    }
  }
  else
  {
    if ((c = fgetc(normal_src)) == EOF)
    {
      goto error;
    }
  }

  seed += (c & 255) << 16;

  if (packed)
  {
    if ((c = pack_getc(packed_src)) == EOF)
    {
      goto error;
    }
  }
  else
  {
    if ((c = fgetc(normal_src)) == EOF)
    {
      goto error;
    }
  }

  seed += (c & 255) << 8;

  if (packed)
  {
    if ((c = pack_getc(packed_src)) == EOF)
    {
      goto error;
    }
  }
  else
  {
    if ((c = fgetc(normal_src)) == EOF)
    {
      goto error;
    }
  }

  seed += c & 255;
  seed ^= enc_mask[method];

  // decode the data
  for (i = 0; i < size; i++)
  {
    if (packed)
    {
      if ((c = pack_getc(packed_src)) == EOF)
      {
        goto error;
      }
    }
    else
    {
      if ((c = fgetc(normal_src)) == EOF)
      {
        goto error;
      }
    }

    if (tog)
    {
      c -= r;
    }
    else
    {
      r = rand_007(method);
      c ^= r;
    }

    tog ^= 1;

    c &= 255;
    c1 += c;
    c2 = (c2 << 4) + (c2 >> 12) + c;

    // if (i < 20) printf("read %c\n", c);
    // if (i % 100 == 0) printf("i = %ld c = %c\n", i, c);
    int ec = fputc(c, dest);
    if (ec == EOF) {
      printf("err at i = %ld\n", i);
      printf("errno fgetc(dest): %d\n", errno);
      printf("ferror fgetc(dest): %d\n", ferror(dest));
      return 100;
    }
  }

  // read checksums
  if (packed)
  {
    if ((c = pack_getc(packed_src)) == EOF)
    {
      goto error;
    }
  }
  else
  {
    if ((c = fgetc(normal_src)) == EOF)
    {
      goto error;
    }
  }

  check1 = c << 8;

  if (packed)
  {
    if ((c = pack_getc(packed_src)) == EOF)
    {
      goto error;
    }
  }
  else
  {
    if ((c = fgetc(normal_src)) == EOF)
    {
      goto error;
    }
  }

  check1 += c & 255;

  if (packed)
  {
    if ((c = pack_getc(packed_src)) == EOF)
    {
      goto error;
    }
  }
  else
  {
    if ((c = fgetc(normal_src)) == EOF)
    {
      goto error;
    }
  }

  check2 = c << 8;

  if (packed)
  {
    if ((c = pack_getc(packed_src)) == EOF)
    {
      goto error;
    }
  }
  else
  {
    if ((c = fgetc(normal_src)) == EOF)
    {
      goto error;
    }
  }

  check2 += c & 255;

  // verify checksums
  r = rand_007(method);
  check1 ^= r;
  check2 -= r;
  check1 &= 0xFFFF;
  check2 &= 0xFFFF;

  if (check1 != c1 || check2 != c2)
  {
    err = 5;
    goto error;
  }

  if (packed)
  {
    pack_fclose(packed_src);
  }
  else
  {
    fclose(normal_src);
  }

  fclose(dest);
  return 0;

error:

  if (packed)
  {
    pack_fclose(packed_src);
  }
  else
  {
    fclose(normal_src);
  }

  fclose(dest);
  delete_file(destfile);
  return err;
}

int decode(const char *data, char *output, long size, int32_t method)
{
  const char *header = "Zelda Classic Quest File";

  char srcfname[] = "/tmp/fileXXXXXX";
  mkstemp(srcfname);
  FILE* src = fopen(srcfname, "w");
  for (int i = 0; i < size; i++)
  {
    fputc(data[i], src);
  }
  fclose(src);

  char destfname[] = "/tmp/fileXXXXXX";
  mkstemp(destfname);
  fclose(fopen(destfname , "w"));
  
  printf("start.... %s %s\n", srcfname, destfname);
  int ret = decode_file_007(srcfname, destfname, header, method, !true, datapwd);
  if (ret != 0)
  {
    printf("err decode_file_007: %d\n", ret);
    return ret;
  }

  // Copy from temporary to output buffer.
  FILE *decoded = fopen(destfname, "rb");
  FILE *dest = fmemopen((void *)output, size - 8, "w");
  printf("size = %ld\n", size);
  for (int i = 0; i < size; i++)
  {
    char c;
    if ((c = fgetc(decoded)) == EOF)
    {
      // printf("errno fgetc(decoded): %d\n", errno);
      // printf("ferror fgetc(decoded): %d\n", ferror(decoded));
      // fclose(decoded);
      // return 11;
    }

    // if (i > 880)
    //   printf("c = %d %c\n", c, c);
    // if (i > 880) printf("i = %d\n", i);
    fputc(c, dest);
  }
  fclose(decoded);
  // output[2] = 'a';
  return ret;
}
