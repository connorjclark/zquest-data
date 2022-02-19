// https://github.com/ArmageddonGames/ZeldaClassic/blob/023dd17eaf6a969f47650cb6591cedd0baeaab64/src/zsys.cpp

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <allegro/file.h>
// #include <allegro/lzss.h>
#include <emscripten.h>


/* _al_malloc:
 *  Wrapper for when a program needs to manipulate memory that has been
 *  allocated by the Allegro DLL.
 */
void *_al_malloc(size_t size)
{
   return malloc(size);
}



/* _al_free:
 *  Wrapper for when a program needs to manipulate memory that has been
 *  allocated by the Allegro DLL.
 */
void _al_free(void *mem)
{
   free(mem);
}

int* allegro_errno = 0;

#define _AL_MALLOC_ATOMIC malloc

#define N            4096           /* 4k buffers for LZ compression */
#define F            18             /* upper limit for LZ match length */
#define THRESHOLD    2              /* LZ encode string into pos and length
				       if match size is greater than this */

// struct LZSS_UNPACK_DATA             /* for reading LZ files */
// {
//    int state;                       /* where have we got to? */
//    int i, j, k, r, c;
//    int flags;
//    unsigned char text_buf[N+F-1];   /* ring buffer, with F-1 extra bytes
// 				       for string comparison */
// };

// /* create_unpack_data:
//  *  Creates an LZSS_UNPACK_DATA structure.
//  */
// struct LZSS_UNPACK_DATA *create_lzss_unpack_data(void)
// {
//    struct LZSS_UNPACK_DATA *dat;
//    int c;

//    if ((dat = _AL_MALLOC_ATOMIC(sizeof(struct LZSS_UNPACK_DATA))) == NULL) {
//       // *allegro_errno = ENOMEM;
//       return NULL;
//    }

//    for (c=0; c < N - F; c++)
//       dat->text_buf[c] = 0;

//    dat->state = 0;

//    return dat;
// }

// /* lzss_read:
//  *  Unpacks from dat into buf, until either EOF is reached or s bytes have
//  *  been extracted. Returns the number of bytes added to the buffer
//  */
// int lzss_read(PACKFILE *file, struct LZSS_UNPACK_DATA *dat, int s, unsigned char *buf)
// {
//    int i = dat->i;
//    int j = dat->j;
//    int k = dat->k;
//    int r = dat->r;
//    int c = dat->c;
//    unsigned int flags = dat->flags;
//    int size = 0;

//    if (dat->state==2)
//       goto pos2;
//    else
//       if (dat->state==1)
// 	 goto pos1;

//    r = N-F;
//    flags = 0;

//    for (;;) {
//       if (((flags >>= 1) & 256) == 0) {
// 	 if ((c = pack_getc(file)) == EOF)
// 	    break;
  
// 	 if ((file->is_normal_packfile) && (file->normal.passpos) &&
// 	     (file->normal.flags & PACKFILE_FLAG_OLD_CRYPT))
// 	 {
// 	    c ^= *file->normal.passpos;
// 	    file->normal.passpos++;
// 	    if (!*file->normal.passpos)
// 	       file->normal.passpos = file->normal.passdata;
// 	 }

// 	 flags = c | 0xFF00;        /* uses higher byte to count eight */
//       }

//       if (flags & 1) {
// 	 if ((c = pack_getc(file)) == EOF)
// 	    break;
// 	 dat->text_buf[r++] = c;
// 	 r &= (N - 1);
// 	 *(buf++) = c;
// 	 if (++size >= s) {
// 	    dat->state = 1;
// 	    goto getout;
// 	 }
// 	 pos1:
// 	    ; 
//       }
//       else {
// 	 if ((i = pack_getc(file)) == EOF)
// 	    break;
// 	 if ((j = pack_getc(file)) == EOF)
// 	    break;
// 	 i |= ((j & 0xF0) << 4);
// 	 j = (j & 0x0F) + THRESHOLD;
// 	 for (k=0; k <= j; k++) {
// 	    c = dat->text_buf[(i + k) & (N - 1)];
// 	    dat->text_buf[r++] = c;
// 	    r &= (N - 1);
// 	    *(buf++) = c;
// 	    if (++size >= s) {
// 	       dat->state = 2;
// 	       goto getout;
// 	    }
// 	    pos2:
// 	       ; 
// 	 }
//       }
//    }

//    dat->state = 0;

//    getout:

//    dat->i = i;
//    dat->j = j;
//    dat->k = k;
//    dat->r = r;
//    dat->c = c;
//    dat->flags = flags;

//    return size;
// }

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

// uint64_t file_size_ex_password(const char *filename, const char *password)
// {
//   packfile_password(password);
//   uint64_t new_pf = file_size_ex(filename);
//   packfile_password("");
//   return new_pf;
// }

int decode_file_007(const char *srcfile, const char *destfile, const char *header, int method, bool packed, const char *password)
{
  FILE *normal_src = NULL, *dest = NULL;
  // PACKFILE *packed_src = NULL;
  int tog = 0, c, r = 0, err;
  long size, i;
  short c1 = 0, c2 = 0, check1, check2;

  // open files
  FILE* f = fopen(srcfile, "r");
  fseek(f, 0, SEEK_END); // seek to end of file
  size = ftell(f); // get current file pointer
  fseek(f, 0, SEEK_SET); // seek back to beginning of file
  fclose(f);

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
    // packed_src = pack_fopen_password(srcfile, F_READ_PACKED, password);

    // if (errno == EDOM)
    // {
    //   packed_src = pack_fopen_password(srcfile, F_READ, password);
    // }

    // if (!packed_src)
    // {
    //   return 1;
    // }
  }

  dest = fopen(destfile, "wb");

  if (!dest)
  {
    if (packed)
    {
      // pack_fclose(packed_src);
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
        // if ((c = pack_getc(packed_src)) == EOF)
        // {
        //   goto error;
        // }
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
    // if ((c = pack_getc(packed_src)) == EOF)
    // {
    //   goto error;
    // }
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
    // if ((c = pack_getc(packed_src)) == EOF)
    // {
    //   goto error;
    // }
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
    // if ((c = pack_getc(packed_src)) == EOF)
    // {
    //   goto error;
    // }
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
    // if ((c = pack_getc(packed_src)) == EOF)
    // {
    //   goto error;
    // }
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
      // if ((c = pack_getc(packed_src)) == EOF)
      // {
      //   goto error;
      // }
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
  }

  // read checksums
  if (packed)
  {
    // if ((c = pack_getc(packed_src)) == EOF)
    // {
    //   goto error;
    // }
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
    // if ((c = pack_getc(packed_src)) == EOF)
    // {
    //   goto error;
    // }
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
    // if ((c = pack_getc(packed_src)) == EOF)
    // {
    //   goto error;
    // }
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
    // if ((c = pack_getc(packed_src)) == EOF)
    // {
    //   goto error;
    // }
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
    // pack_fclose(packed_src);
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
    // pack_fclose(packed_src);
  }
  else
  {
    fclose(normal_src);
  }

  fclose(dest);
  // delete_file(destfile);
  return err;
}

int fget_4byteint(FILE* f) {
  int byte1 = fgetc(f);
  int byte2 = fgetc(f);
  int byte3 = fgetc(f);
  int byte4 = fgetc(f);
  return (byte1 << 24) + (byte2 << 16) + (byte3 << 8) + byte4;
}

/*
  A qst file is encoded in two layers.
  1) The top layer is from Zelda Classic. It is defined by the method decode_file_007.
     [0-24]    Preamble "Zelda Classic Quest File"
     [25-28]   Initial decoding seed value.
     [29-X]    Allegro-encoded payload (AKA "packed" file)
     [last 4]  Checksum
  2) The bottom layer is a "compressed packed file" from Allegro 4. The entire payload
     is XOR'd with a password. Once that is done, the first four bytes are "slh!", followed
     by a lzss compressed representation of the payload.

  Helpful links:
  - https://www.allegro.cc/forums/thread/479372
  - lzss_read
*/
int decode(const char *qst_file, const char *destfname, int32_t method)
{
  const char *preamble = "Zelda Classic Quest File";

  FILE* f = fopen(qst_file, "r");
  fseek(f, 0, SEEK_END);
  int size = ftell(f);
  fseek(f, 0, SEEK_SET);

  // First check that the file starts with the correct preamble.
  for (int i = 0; preamble[i]; i++) {
    char ch = fgetc(f);
    if (ch != preamble[i]) {
      return 1;
    }

    printf("%c %c\n", preamble[i], ch);
  }

  // Get the seed value used to decode the top layer of encoding.
  seed = fget_4byteint(f);
  seed ^= enc_mask[method];
  size -= 4;

  printf("size: %d\n", size);
  printf("seed: %d\n", seed);

  FILE* packfile_data = fopen("/tmp/packfile_data", "w");
  bool tog = false;
  int r = 0;
  short c1 = 0;
  short c2 = 0;
  for (int i = 0; i < size; i++) {
    int c = fgetc(f);

    if (tog)
    {
      c -= r;
    }
    else
    {
      r = rand_007(method);
      c ^= r;
    }

    tog = !tog;

    c &= 255;
    c1 += c;
    c2 = (c2 << 4) + (c2 >> 12) + c;
    fputc(c, packfile_data);
    // printf("%d\n", c);
  }

  /*
  def decrypt(data, password):
  2	 
  3	  out_data = ""
  4	 
  5	  pass_index = 0
  6	  for c in data:
  7	    out_data += chr(ord(c) ^ ord(password[pass_index]))
  8	    pass_index = (pass_index + 1) % len(password)
  9	 
  10	  # header
  11	  mask = 0
  12	  for i in range(len(password)):
  13	    mask ^= (long(ord(password<i>)) << ((i & 3) * 8))
  14	  pos = 0
  15	  for i in range(4):
  16	    mask ^= long(ord(password[pos])) << (24-i*8)
  17	    pos = (pos + 1) % len(password)
  18	  mask ^= 42 # new_format???
  19	  h = (ord(out_data[0]) << 24 | ord(out_data[1]) << 16 | ord(out_data[2]) << 8 | ord(out_data[3])) ^ mask
  20	  out_data_h = chr(h >> 24) + chr(h >> 16 & 0xFF) + chr(h >> 8 & 0xFF) + chr(h & 0xFF)
  */

  // fclose(packfile_data);

  // pack_fopen_password("/tmp/packfile_data", F_READ_PACKED, datapwd);


  fseek(packfile_data, 0, SEEK_SET);
  fclose(packfile_data);


  // unsigned char buf[10];
  // struct LZSS_UNPACK_DATA *dat = create_lzss_unpack_data();
  struct PACKFILE *packfile = pack_fopen_password("/tmp/packfile_data", F_READ_PACKED, datapwd);


  for (int i = 0; i < 100; i++) {
    char c;
    if ((c = pack_getc(packfile)) == EOF) { 
      break;
    }
    printf("%c\n", c);
  }
  // lzss_read(&packfile, dat, 10, buf);

  // for (int i = 0; i < size; i++) {
  //   int c = buf[i];
  //   if (i < 5) printf("%c\n", c);
  // }

  return 0;

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
  int ret = decode_file_007(qst_file, srcfname, preamble, method, false, datapwd);
  if (ret != 0)
  {
    // printf("err decode_file_007: %d\n", ret);
    return ret;
  }

  // Second, decompress.
  // PACKFILE *decoded = pack_fopen_password(srcfname, F_READ_PACKED, datapwd);

  FILE* dest = fopen(destfname, "w");
  char c;
  // 3833540
  // for (int i = 0; i < 3833540; i++) {
  //   char c;
  //   if ((c = pack_getc(decoded)) == EOF) { 
  //     break;
  //   }
  //   if (i % 1000 == 0) printf("[%d] = %d %c\n", i, c, c);
  //   fputc(c, dest);
  // }
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

  for (int32_t method = 4; method >= 0; method--) {
    int result = decode(qstpath, "/quests/1st.qst.dat", method);
    if (result == 0) {
      return "OK";
    }
  }

  return "not OK";
}
