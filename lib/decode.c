// https://github.com/ArmageddonGames/ZeldaClassic/blob/023dd17eaf6a969f47650cb6591cedd0baeaab64/src/zsys.cpp

#include <stdio.h>
// #include <allegro.h>
#include <allegro/file.h>

#define EOF    (-1)
static const int ENC_METHOD_MAX = 5;

static int32_t seed = 0;
static int32_t enc_mask[ENC_METHOD_MAX]= {0x4C358938,0x91B2A2D1,0x4A7C1B87,0xF93941E6,0xFD095E94};
static int32_t pvalue[ENC_METHOD_MAX]= {0x62E9,0x7D14,0x1A82,0x02BB,0xE09C};
static int32_t qvalue[ENC_METHOD_MAX]= {0x3619,0xA26B,0xF03C,0x7B12,0x4E8F};
static char datapwd[8]   = { ('l'+11),('o'+22),('n'+33),('g'+44),('t'+55),('a'+66),('n'+77),(0+88) };

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

int decode_file_007(const char *data, char *output_file, long size, int32_t method)
{
    // declare some stuff to make the following code go mostly unchanged
    const char* header = "Zelda Classic Quest File";
    int32_t packed = 0;
    FILE* normal_src = fmemopen((void*)data, size, "r");
    FILE* dest = fopen(output_file, "r");

    int32_t tog = 0, c = 0, r = 0, err = 0;
    long i = 0;
    int16_t c1 = 0, c2 = 0, check1 = 0, check2 = 0;
   
    if(size < 1)
    {
        return 1;
    }
    
    size -= 8;                                                // get actual data size, minus key and checksums
    
    if(size < 1)
    {
        return 3;
    }
    
    // if(!packed)
    // {
    //     normal_src = fopen(srcfile, "rb");
        
    //     if(!normal_src)
    //     {
    //         return 1;
    //     }
    // }
    // else
    // {
    //     // packed_src = pack_fopen_password(srcfile, F_READ_PACKED,password);
        
    //     // if(errno==EDOM)
    //     // {
    //     //     packed_src = pack_fopen_password(srcfile, F_READ,password);
    //     // }
        
    //     // if(!packed_src)
    //     // {
    //     //     return 1;
    //     // }
    // }
    
    // dest = fopen(destfile, "wb");
    
    // if(!dest)
    // {
    //     if(packed)
    //     {
    //         // pack_fclose(packed_src);
    //     }
    //     else
    //     {
    //         fclose(normal_src);
    //     }
        
    //     return 2;
    // }
    
    // read the header
    err = 4;
    
    if(header)
    {
        for(i=0; header[i]; i++)
        {
            if(packed)
            {
                // if((c=pack_getc(packed_src)) == EOF)
                // {
                //     goto error;
                // }
            }
            else
            {
                if((c=fgetc(normal_src)) == EOF)
                {
                    goto error;
                }
            }
            
            printf("c = %d %c\n", c, c);
            if((c&255) != header[i])
            {
                err = 6;
                goto error;
            }
            
            --size;
        }
    }
    
    // read the key
    if(packed)
    {
        // if((c=pack_getc(packed_src)) == EOF)
        // {
        //     goto error;
        // }
    }
    else
    {
        if((c=fgetc(normal_src)) == EOF)
        {
            goto error;
        }
    }
    
    seed = c << 24;
    
    if(packed)
    {
        // if((c=pack_getc(packed_src)) == EOF)
        // {
        //     goto error;
        // }
    }
    else
    {
        if((c=fgetc(normal_src)) == EOF)
        {
            goto error;
        }
    }
    
    seed += (c & 255) << 16;
    
    if(packed)
    {
        // if((c=pack_getc(packed_src)) == EOF)
        // {
        //     goto error;
        // }
    }
    else
    {
        if((c=fgetc(normal_src)) == EOF)
        {
            goto error;
        }
    }
    
    seed += (c & 255) << 8;
    
    if(packed)
    {
        // if((c=pack_getc(packed_src)) == EOF)
        // {
        //     goto error;
        // }
    }
    else
    {
        if((c=fgetc(normal_src)) == EOF)
        {
            goto error;
        }
    }
    
    seed += c & 255;
    seed ^= enc_mask[method];
    
    // decode the data
    printf("seed = %d\n", seed);
    printf("size = %ld\n", size);
    for(i=0; i<size; i++)
    {
        if(packed)
        {
            // if((c=pack_getc(packed_src)) == EOF)
            // {
            //     goto error;
            // }
        }
        else
        {
            if((c=fgetc(normal_src)) == EOF)
            {
                goto error;
            }
        }
        
        if(tog)
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
        
        if (i < 20) printf("c = %d %c\n", c, c);
        fputc(c, dest);
    }
    
    // read checksums
    if(packed)
    {
        // if((c=pack_getc(packed_src)) == EOF)
        // {
        //     goto error;
        // }
    }
    else
    {
        if((c=fgetc(normal_src)) == EOF)
        {
            goto error;
        }
    }
    
    check1 = c << 8;
    
    if(packed)
    {
        // if((c=pack_getc(packed_src)) == EOF)
        // {
        //     goto error;
        // }
    }
    else
    {
        if((c=fgetc(normal_src)) == EOF)
        {
            goto error;
        }
    }
    
    check1 += c & 255;
    
    if(packed)
    {
    //     if((c=pack_getc(packed_src)) == EOF)
    //     {
    //         goto error;
    //     }
    }
    else
    {
        if((c=fgetc(normal_src)) == EOF)
        {
            goto error;
        }
    }
    
    check2 = c << 8;
    
    if(packed)
    {
        // if((c=pack_getc(packed_src)) == EOF)
        // {
        //     goto error;
        // }
    }
    else
    {
        if((c=fgetc(normal_src)) == EOF)
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
    
    printf("%d == %d and %d == %d\n", check1, c1, check2, c2);
    if(check1 != c1 || check2 != c2)
    {
        err = 5;
        goto error;
    }
    
    // if(packed)
    // {
    //     // pack_fclose(packed_src);
    // }
    // else
    // {
    //     fclose(normal_src);
    // }
    
    // fclose(dest);
    // return dest;
    return 0;
    
error:

    // if(packed)
    // {
    //     // pack_fclose(packed_src);
    // }
    // else
    // {
    //     fclose(normal_src);
    // }
    
    // fclose(dest);
    // delete_file(destfile);
    return err;
}

int decode(const char *data, char *output, long size, int32_t method)
{
  // Unencrypt the data.
  char tmpfilename[32];
  tempname(tmpfilename);
  int ret = decode_file_007(data, tmpfilename, size, method);

  // Uncompress the data.
  packfile_password(datapwd);
  PACKFILE* uncompressed = pack_fopen(tmpfilename, F_READ_PACKED);
  packfile_password("");

  // Copy from temporary to output buffer.
  FILE* dest = fmemopen ((void*)output, size - 8, "r");
  for (int i=0; i<size; i++)
  {
      char c;
      if((c=fgetc(uncompressed)) == EOF)
      {
          return 11;
      }
      
      if (i < 20) printf("c = %d %c\n", c, c);
      fputc(c, dest);
  }
  return ret;
}
