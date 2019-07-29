// https://github.com/ArmageddonGames/ZeldaClassic/blob/023dd17eaf6a969f47650cb6591cedd0baeaab64/src/zsys.cpp

#include <stdio.h>

#define EOF    (-1)
static const int ENC_METHOD_MAX = 5;

//#define MASK 0x4C358938
static int seed = 0;
//#define MASK 0x91B2A2D1
//static int seed = 7351962;
static int enc_mask[ENC_METHOD_MAX]= {0x4C358938,0x91B2A2D1,0x4A7C1B87,0xF93941E6,0xFD095E94};
static int pvalue[ENC_METHOD_MAX]= {0x62E9,0x7D14,0x1A82,0x02BB,0xE09C};
static int qvalue[ENC_METHOD_MAX]= {0x3619,0xA26B,0xF03C,0x7B12,0x4E8F};

int rand_007(int method)
{
    short BX = seed >> 8;
    short CX = (seed & 0xFF) << 8;
    signed char AL = seed >> 24;
    signed char C = AL >> 7;
    signed char D = BX >> 15;
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

int decode_file_007(const char *data, char *output, long size, int method)
{
    // declare some stuff to make the following code go mostly unchanged
    int packed = 1;
    FILE* normal_src = fmemopen((void*)data, size, "r");
    size_t outsize;
    FILE* dest = open_memstream (&output, &outsize);
    printf("size %ld\n", size);

    int tog = 0, c=0, r=0, err;
    long i;
    short c1 = 0, c2 = 0, check1, check2;
   
    if(size < 1)
    {
        return 1;
    }
    
    // already do this in python
    // size -= 8;                                                // get actual data size, minus key and checksums
    
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
    
    // Header is handled in python.
    // if(header)
    // {
    //     for(i=0; header[i]; i++)
    //     {
    //         if(packed)
    //         {
    //             // if((c=pack_getc(packed_src)) == EOF)
    //             // {
    //             //     goto error;
    //             // }
    //         }
    //         else
    //         {
    //             if((c=fgetc(normal_src)) == EOF)
    //             {
    //                 goto error;
    //             }
    //         }
            
    //         if((c&255) != header[i])
    //         {
    //             err = 6;
    //             goto error;
    //         }
            
    //         --size;
    //     }
    // }
    
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
    printf("outsize %ld\n", outsize);
    return err;
}
