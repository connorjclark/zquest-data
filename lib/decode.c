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

int32_t encrypt_id(long x, int new_format)
{
   char* the_password = datapwd;
   int32_t mask = 0;
   int i, pos;

   printf("the_password: %s\n", the_password);
   if (the_password[0]) {
      for (i=0; the_password[i]; i++)
	 mask ^= ((int32_t)the_password[i] << ((i&3) * 8));

      for (i=0, pos=0; i<4; i++) {
	 mask ^= (int32_t)the_password[pos++] << (24-i*8);
	 if (!the_password[pos])
	    pos = 0;
      }

      if (new_format)
	 mask ^= 42;
   }

   printf("mask: %d\n", mask);

   return x ^ mask;
}

void resolve_password(char *pwd)
{
  for(int i=0; i<8; i++)
    pwd[i]-=(i+1)*11;
}

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
	packfile_password(password);

  #define F_PACK_MAGIC    0x736C6821L    /* magic number for packed files */
  #define F_NOPACK_MAGIC  0x736C682EL    /* magic number for autodetect */

  encrypt_id(F_PACK_MAGIC, TRUE);
  encrypt_id(F_NOPACK_MAGIC, TRUE);
  encrypt_id(F_PACK_MAGIC, FALSE);
  encrypt_id(F_NOPACK_MAGIC, FALSE);

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
    packed_src = pack_fopen_password(srcfile, F_READ_PACKED, password);

    if (errno == EDOM)
    {
      packed_src = pack_fopen_password(srcfile, F_READ, password);
    }

    if (!packed_src)
    {
      return 1;
    }
  }

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

      // if (i < 20) printf("%c\n", c);
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
  printf("decode_007 seed %d\n", seed);

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

    if (i == 5){
      printf("decode_007 ==== i = %d\n", i);
      printf("c BEFORE %d\n", c);
    }
    c &= 255;
    if (i == 5){
      printf("c AFTER %d\n", c);
    }
    c1 += c;
    c2 = (c2 << 4) + (c2 >> 12) + c;
    // if (i % 100 == 0) printf("i = %ld c = %c\n", i, c);
    fputc(c, dest);

    if (i < 20) {
      printf("decode_007 result %d = %d\n", i, c);
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

extern static char the_password[256] = EMPTY_STRING;
bool resolvedpwd = false;

int decode(const char *data, char *output, long size, int32_t method)
{
  if (!resolvedpwd) {
    resolve_password(datapwd);
    resolvedpwd = true;
  }

  // First, unencrypt the data using `decode_file_007`, storing the result
  // on disk at `destfname` (use the filesystem so that the original decoding
  // function doesn't have to change at all).
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
  
  // printf("decode_file_007(%s, %s)\n", srcfname, destfname);
  int ret = decode_file_007(srcfname, destfname, header, method, false, datapwd);
  if (ret != 0)
  {
    // printf("err decode_file_007: %d\n", ret);
    return ret;
  }

  printf("datapwd: ");
  for (int i = 0; i < sizeof datapwd; i++) {
    // printf("%x (%d) ", datapwd[i], datapwd[i]);
    printf("%d ", datapwd[i]);
  }
  printf("\n");

  FILE* f = fopen(destfname, "rb");
  int decodedlen = 0;
  while (true) {
    int byte = fgetc(f);
    if (byte == EOF) break;

    if (decodedlen < 20) {
      printf("byte %d = %d\n", decodedlen, byte);
    }
    decodedlen += 1;
  }
  printf("len = %d\n", decodedlen);
  fclose(f);

  // Second, decompress.
  PACKFILE *decoded = pack_fopen_password(destfname, F_READ_PACKED, datapwd);

  // Copy from temporary to output buffer.
  // FILE *decoded = fopen(destfname, "rb");
  // TODO: shouldn't just guess how big the output will be ...
  FILE *dest = fmemopen((void *)output, size * 5, "w");
  // printf("size = %ld\n", size);
  for (int i = 0; i < size*5; i++)
  {
    char c;
    if ((c = pack_getc(decoded)) == EOF)
    {
      // printf("errno fgetc(decoded): %d at i = %d\n", c, i);
      // printf("ferror fgetc(decoded): %d\n", ferror(decoded));
      // fclose(decoded);
      // return 11;
      // break;
    }

    // if (i < 20)
    //   printf("c = %d %c\n", c, c);
    // if (i > 880) printf("i = %d\n", i);
    fputc(c, dest);
  }
  pack_fclose(decoded);
  return ret;
}
