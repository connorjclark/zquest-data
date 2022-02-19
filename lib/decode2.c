// https://github.com/ArmageddonGames/ZeldaClassic/blob/023dd17eaf6a969f47650cb6591cedd0baeaab64/src/zsys.cpp

#include <stdbool.h>
#include <stdio.h>
#include <allegro/file.h>
#include <emscripten.h>

// static int nojoy_ret0(void) { return 0; }
// static void nojoy_void(void) { }
// void* joystick_none =
// {
//    0,
//    "",
//    "",
//    "No joystick",
//    nojoy_ret0,
//    nojoy_void,
//    nojoy_ret0,
//    NULL, NULL,
//    NULL, NULL
// };

/* _al_malloc:
 *  Wrapper for when a program needs to manipulate memory that has been
 *  allocated by the Allegro DLL.
 */
// void *_al_malloc(size_t size)
// {
//    return malloc(size);
// }

// void _al_free(void *mem)
// {
//    free(mem);
// }

// /* error value, which will work even with DLL linkage */
// int *allegro_errno = NULL;

// /* get_executable_name:
//  *  Finds out the name of the current executable.
//  */
// void get_executable_name(char *output, int size)
// {
//   //  ASSERT(system_driver);
//   //  ASSERT(output);

//   //  if (system_driver->get_executable_name) {
//   //     system_driver->get_executable_name(output, size);
//   //  }
//   //  else {
//   //     output += usetc(output, '.');
//   //     output += usetc(output, '/');
//   //     usetc(output, 0);
//   //  }
// }

// /* _remove_exit_func:
//  *  Removes a function from the list that need to be called by allegro_exit().
//  */
// void _remove_exit_func(void (*func)(void))
// {
//   //  struct al_exit_func *iter = exit_func_list, *prev = NULL;

//   //  while (iter) {
//   //     if (iter->funcptr == func) {
// 	//  if (prev)
// 	//     prev->next = iter->next;
// 	//  else
// 	//     exit_func_list = iter->next;
// 	//  _AL_FREE(iter);
// 	//  return;
//   //     }
//   //     prev = iter;
//   //     iter = iter->next;
//   //  }
// }


// ---------------------------------------------------------------------

int main() {
  return 0;
}

#define EOF (-1)
#define ENC_METHOD_MAX 5

static int32_t seed = 0;
static int32_t enc_mask[ENC_METHOD_MAX] = {0x4C358938, 0x91B2A2D1, 0x4A7C1B87, 0xF93941E6, 0xFD095E94};
static int32_t pvalue[ENC_METHOD_MAX] = {0x62E9, 0x7D14, 0x1A82, 0x02BB, 0xE09C};
static int32_t qvalue[ENC_METHOD_MAX] = {0x3619, 0xA26B, 0xF03C, 0x7B12, 0x4E8F};
static char datapwd[8] = {('l' + 11), ('o' + 22), ('n' + 33), ('g' + 44), ('t' + 55), ('a' + 66), ('n' + 77), (0 + 88)};

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
  resolve_password(datapwd);
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
  printf("method: %d\n", method);

  FILE *normal_src = NULL, *dest = NULL;
  PACKFILE *packed_src = NULL;
  int tog = 0, c, r = 0, err;
  long size, i;
  short c1 = 0, c2 = 0, check1, check2;

  // open files
  size = file_size_ex_password(srcfile, password);
  printf("size: %ld\n", size);

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
  printf("seed: %d\n", seed);
  seed ^= enc_mask[method];
  printf("seed: %d\n", seed);

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
    // if (i % 100 == 0) printf("i = %ld c = %c\n", i, c);
    fputc(c, dest);

    if (i<10) printf("data: %d\n", c);
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

int decode(const char *qst_file, const char *destfname, int32_t method)
{
  // First, unencrypt the data using `decode_file_007`, storing the result
  // on disk at `destfname` (use the filesystem so that the original decoding
  // function doesn't have to change at all).
  const char *header = "Zelda Classic Quest File";

  char srcfname[] = "/tmp/fileXXXXXX";
  mkstemp(srcfname);
  // FILE* src = fopen(srcfname, "w");
  // for (int i = 0; i < size; i++)
  // {
  //   fputc(data[i], src);
  // }
  // fclose(src);

  // char destfname[] = "/tmp/fileXXXXXX";
  // mkstemp(destfname);
  // fclose(fopen(destfname , "w"));
  
  // printf("decode_file_007(%s, %s)\n", srcfname, destfname);
  int ret = decode_file_007(qst_file, srcfname, header, method, false, datapwd);
  if (ret != 0)
  {
    // printf("err decode_file_007: %d\n", ret);
    return ret;
  }

  // Second, decompress.
  PACKFILE *decoded = pack_fopen_password(srcfname, F_READ_PACKED, datapwd);

  FILE* dest = fopen(destfname, "w");
  char c;
  // 3833540
  for (int i = 0; i < 3833540; i++) {
    char c;
    if ((c = pack_getc(decoded)) == EOF) { 
      break;
    }
    if (i % 1000 == 0) printf("[%d] = %d %c\n", i, c, c);
    fputc(c, dest);
  }
  // while (pack_feof(decoded) != EOF) {
  //   fputc(c, dest);
  // }
  // while ((c = pack_getc(decoded)) != EOF) {
  //   fputc(c, dest);
  // }
  fclose(dest);

  return ret;
}

EMSCRIPTEN_KEEPALIVE
const char* read_qst_file() {
  printf("hi\n");
  const char* qstpath = "/quests/1st.qst";

  for (int32_t method = 0; method < 5; method++) {
    int result = decode(qstpath, "/quests/1st.qst.dat", method);
    if (result == 0) {
      return "OK";
    }
  }

  return "not OK";
}
