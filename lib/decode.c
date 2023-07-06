/*
  Decodes a ZeldaClassic .qst file.
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
  - decode_file_007 https://github.com/ArmageddonGames/ZeldaClassic/blob/023dd17eaf6a969f47650cb6591cedd0baeaab64/src/zsys.cpp#L492
*/

#include <stdbool.h>
#include <stdio.h>
#include <allegro/file.h>

#define QH_IDSTR    "AG Zelda Classic Quest File\n "
#define QH_NEWIDSTR "AG ZC Enhanced Quest File\n   "
#define ENC_STR     "Zelda Classic Quest File"

enum {ENC_METHOD_192B104=0, ENC_METHOD_192B105, ENC_METHOD_192B185, ENC_METHOD_211B9, ENC_METHOD_211B18, ENC_METHOD_MAX};
enum
{
    qe_OK, qe_notfound, qe_invalid, qe_version, qe_obsolete,
    qe_missing, qe_internal, qe_pwd, qe_match, qe_minver,
    qe_nomem, qe_debug, qe_cancel, qe_silenterr, qe_no_qst
};

static int32_t seed = 0;
static int32_t method_out = 0;
static int32_t key_out = 0;
static int32_t enc_mask[ENC_METHOD_MAX] = {0x4C358938, 0x91B2A2D1, 0x4A7C1B87, 0xF93941E6, 0xFD095E94};
static int32_t pvalue[ENC_METHOD_MAX] = {0x62E9, 0x7D14, 0x1A82, 0x02BB, 0xE09C};
static int32_t qvalue[ENC_METHOD_MAX] = {0x3619, 0xA26B, 0xF03C, 0x7B12, 0x4E8F};
static char datapwd[8] = "longtan";

static int alle_errno = 0;

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
	PACKFILE *pf = pack_fopen(filename, mode);
	packfile_password("");
	return pf;
}

short fget_2byteint(FILE* f) {
  int byte1 = fgetc(f);
  int byte2 = fgetc(f);
  return (byte1 << 8) + byte2;
}

int fget_4byteint(FILE* f) {
  int byte1 = fgetc(f);
  int byte2 = fgetc(f);
  int byte3 = fgetc(f);
  int byte4 = fgetc(f);
  return (byte1 << 24) + (byte2 << 16) + (byte3 << 8) + byte4;
}

int try_decode(const char *qst_file, const char *destfname, int32_t method, bool packed, const char *password)
{
  if (packed)
    return -1;

  const char *preamble = "Zelda Classic Quest File";
  int c;
  method_out = method;

  FILE* f = fopen(qst_file, "r");
  fseek(f, 0, SEEK_END);
  uint64_t size = ftell(f);
  fseek(f, 0, SEEK_SET);
  
  // First check that the file starts with the correct preamble.
  for (int i = 0; preamble[i]; i++) {
    c = fgetc(f);
    if (c != preamble[i]) {
      printf("no preamble\n");
      return 1;
    }
  }

  // Get the seed value used to decode the top layer of encoding.
  seed = fget_4byteint(f);
  seed ^= enc_mask[method];
  key_out = seed;

  // 4 bytes for seed, 4 bytes for checksum
  size -= 8;
  size -= strlen(preamble);

  FILE* packfile_data = fopen(destfname, "w");
  bool tog = false;
  int r = 0;
  short c1 = 0;
  short c2 = 0;
  for (int i = 0; i < size; i++) {
    c = fgetc(f);
    if (c == EOF) {
      // Should never happen.
      return 2;
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

    tog = !tog;

    c &= 255;
    c1 += c;
    c2 = (c2 << 4) + (c2 >> 12) + c;
    fputc(c, packfile_data);
  }

  // Checksums.
  short check1 = fget_2byteint(f);
  short check2 = fget_2byteint(f);
  r = rand_007(method);
  check1 ^= r;
  check2 -= r;
  check1 &= 0xFFFF;
  check2 &= 0xFFFF;
  if (check1 != c1 || check2 != c2) {
    return 5;
  }

  fclose(f);
  fclose(packfile_data);

  return 0;
}

int32_t encode_file_007(const char *srcfile, const char *destfile, int32_t key2, const char *header, int32_t method) {
  FILE *src, *dest;
  int32_t tog = 0, c, r = 0;
  int16_t c1 = 0, c2 = 0;

  seed = key2;
  src = fopen(srcfile, "rb");

  if (!src)
    return 1;

  dest = fopen(destfile, "wb");

  if (!dest) {
    fclose(src);
    return 2;
  }

  // write the header
  if (header) {
    for (c = 0; header[c]; c++)
      fputc(header[c], dest);
  }

  // write the key, XORed with MASK
  key2 ^= enc_mask[method];
  fputc(key2 >> 24, dest);
  fputc((key2 >> 16) & 255, dest);
  fputc((key2 >> 8) & 255, dest);
  fputc(key2 & 255, dest);

  // encode the data
  while ((c = fgetc(src)) != EOF) {
    c1 += c;
    c2 = (c2 << 4) + (c2 >> 12) + c;

    if (tog)
      c += r;
    else {
      r = rand_007(method);
      c ^= r;
    }

    tog ^= 1;

    fputc(c, dest);
  }

  // write the checksums
  r = rand_007(method);
  c1 ^= r;
  c2 += r;
  fputc(c1 >> 8, dest);
  fputc(c1 & 255, dest);
  fputc(c2 >> 8, dest);
  fputc(c2 & 255, dest);

  fclose(src);
  fclose(dest);
  return 0;
}


/*
	.qst file history

	.qst files have always been compressed using allegro's packfiles.

	At some point, an encoding layer was added. The two layers look like this:

		1) The top layer is from us. See decode_file_007.
			[0-24]    Preamble "Zelda Classic Quest File"
			[25-28]   Initial decoding seed value.
			[29-X]    Allegro-encoded payload (AKA "packed" file)
			[last 4]  Checksum

		2) The bottom layer is a "compressed packed file" from Allegro 4. The entire payload
			is XOR'd with a password (datapwd). Once that is undone, the first four bytes are "slh!",
			followed by a lzss compressed representation of the payload (from allergo' packfile compression).
			The oldest quests skip the password part.

	Simply, the job of this function is to peel away the top layer.

	With this second layer of encryption, the data isn't any more secure, and adds a significant delay
	in opening and saving files. There is no version field, so they decryption key is
	found via trial-by-error (very slow!)

	There are other file types of interest:
		- .zqt: quest template files, skips top-layer encryption pass
		- .qsu: "unencoded" (and uncompressed) files; skips encryption and compression (also makes the longtan password moot)
		- .qu?: same as above. automated backup files
		- .qb?: same as above. automated backup files
		- .qt?: compressed and encrypted (or not encrypted, as of May 2023)

	May 2023: .qst files are now saved without the top layer encoding, and no allegro packfile password. The first bytes of these
	files are now "slh!.AG ZC Enhanced Quest File".
	The following command will take an existing qst file and upgrade it: `./zquest -unencrypt-qst <input> <output>`
*/
PACKFILE *open_quest_file(int32_t *open_error, const char *filename)
{
	// Note: although this is primarily for loading .qst files, it can also handle all of the
	// file types mentioned in the comment above. No need to be told if the file being loaded
	// is encrypted or compressed, we can do some simple and fast checks to determine how to load it.
	bool top_layer_compressed = false;
	bool compressed = false;
	bool encrypted = false;

	// Input files may or may not include a top layer, which may or may not be compressed.
	// Additionally, the bottom layer may or may not be compressed, and may or may not be encoded
	// with an allegro packfile password (longtan).
	// We peek into this file to read the header - we'll either see the top layer's header (ENC_STR)
	// or the bottom layer's header (QH_IDSTR or QH_NEWIDSTR).
	// Newly saved .qst files enjoy a fast path here, where there is no top layer at all.

	bool id_came_from_compressed_file = false;
	const char* packfile_password = "";
	char id[32];
	id[0] = id[31] = '\0';
	PACKFILE* pf = pack_fopen_password(filename, F_READ_PACKED, "");
	if (!pf)
		pf = pack_fopen_password(filename, F_READ_PACKED, packfile_password = datapwd);
	if (pf)
	{
		id_came_from_compressed_file = true;
		if (!pack_fread(id, sizeof(id)-1, pf))
		{
			pack_fclose(pf);
			return NULL;
		}
		pack_fclose(pf);
	}
	else
	{
		FILE* f = fopen(filename, "rb");
		if (!f) 
		{
			*open_error=qe_notfound;
			return NULL;
		}
		if (!fread(id, sizeof(char), sizeof(id)-1, f))
		{
			fclose(f);
			return NULL;
		}
		fclose(f);
	}

	if (strstr(id, QH_NEWIDSTR) || strstr(id, QH_IDSTR))
	{
		// The given file is already just the bottom layer - nothing more to do.
		// There's no way to rewind a packfile, so just open it again.
		if (id_came_from_compressed_file)
		{
      method_out = -1;
			return pack_fopen_password(filename, F_READ_PACKED, packfile_password);
		}
		else
		{
      method_out = -1;
			return pack_fopen_password(filename, F_READ, "");
		}
	}
	else if (strstr(id, ENC_STR))
	{
		top_layer_compressed = id_came_from_compressed_file;
		compressed = true;
		encrypted = true;
	}
	else if (id_came_from_compressed_file && strstr(id, "slh!\xff"))
	{
		// We must be reading the compressed contents of an allegro dataobject file. ex: `classic_qst.dat#NESQST_NEW_QST`.
		// Let's extract the content and re-open as a separate file, so allegro will uncompress correctly.

		char tmpfilename[L_tmpnam];
		tmpnam(tmpfilename);
		FILE* tf = fopen(tmpfilename, "wb");
		PACKFILE* pf = pack_fopen_password(filename, F_READ_PACKED, packfile_password);

		int c;
		while ((c = pack_getc(pf)) != EOF)
		{
			fputc(c, tf);
		}
		fclose(tf);
		pack_fclose(pf);
	
		
		// not good: temp file storage leak. Callers don't know to delete temp files anymore.
		// We should put qsu in the dat file, or use a separate .qst file for new qst.
    method_out = -1;
		return pack_fopen_password(tmpfilename, F_READ_PACKED, "");
	}
	else
	{
		// Unexpected, this is going to fail some header check later.
	}

	// Everything below here is legacy code - recently saved quest files will have
	// returned by now.

	char tmpfilename[L_tmpnam];
	tmpnam(tmpfilename);
	char percent_done[30];
	int32_t current_method=0;
    
	PACKFILE *f;
	const char *passwd= encrypted ? datapwd : "";
    
	// oldquest flag is set when an unencrypted qst file is suspected.
	bool oldquest = false;
	int32_t ret;
    
	if(encrypted)
	{
		ret = try_decode(filename, tmpfilename, ENC_METHOD_MAX-1, top_layer_compressed, passwd);
        
		if(ret)
		{
			switch(ret)
			{
			case 1:
				*open_error=qe_notfound;
				return NULL;
                
			case 2:
				*open_error=qe_internal;
				return NULL;
				// be sure not to delete tmpfilename now...
			}
            
			if(ret==5)                                              //old encryption?
			{
				current_method++;
				ret = try_decode(filename, tmpfilename, ENC_METHOD_211B9, strstr(filename, ".dat#")!=NULL, passwd);
			}
            
			if(ret==5)                                              //old encryption?
			{
				current_method++;
				ret = try_decode(filename, tmpfilename, ENC_METHOD_192B185, strstr(filename, ".dat#")!=NULL, passwd);
			}
            
			if(ret==5)                                              //old encryption?
			{
				current_method++;
				ret = try_decode(filename, tmpfilename, ENC_METHOD_192B105, strstr(filename, ".dat#")!=NULL, passwd);
			}
            
			if(ret==5)                                              //old encryption?
			{
				current_method++;
				ret = try_decode(filename, tmpfilename, ENC_METHOD_192B104, strstr(filename, ".dat#")!=NULL, passwd);
			}
            
			if(ret)
			{
				oldquest = true;
				passwd="";
			}
		}
        
	}
	else
	{
		oldquest = true;
	}
    
	f = pack_fopen_password(oldquest ? filename : tmpfilename, compressed ? F_READ_PACKED : F_READ, passwd);
	if(!f)
	{
		if((compressed==1)&&(errno==EDOM))
		{
			f = pack_fopen_password(oldquest ? filename : tmpfilename, F_READ, passwd);
		}
        
		if(!f)
		{
			if(!oldquest)
			{
				delete_file(tmpfilename);
			}
			*open_error=qe_invalid;
			return NULL;
		}
	}
    
	if(!oldquest)
	{
		delete_file(tmpfilename);
	}
    
    
	return f;
}

int decode(const char* qstpath, const char* outpath) {
  FILE* f;
  int c;

  allegro_errno = &alle_errno;

  int err;
  struct PACKFILE *packfile = open_quest_file(&err, qstpath);
  if (!packfile)
    return -1;

  f = fopen(outpath, "w");
  if (!f)
    return -2;

  while ((c = pack_getc(packfile)) != EOF) {
    fputc(c, f);
  }
  fclose(f);
  pack_fclose(packfile);

  return 0;
}

int get_decoded_method() {
  return method_out;
}

int get_decoded_key() {
  return key_out;
}

int encode(const char* inputpath, const char* outpath, int method, int key) {
  allegro_errno = &alle_errno;

  if (method == -1 || method == -2)
  {
    PACKFILE *pf = pack_fopen(outpath, method == -1 ? F_WRITE_PACKED : F_WRITE);

    FILE *f = fopen(inputpath, "rb");
    int c;
    while ((c = getc(f)) != EOF) {
      pack_putc(c, pf);
    }
    fclose(f);
    pack_fclose(pf);
    return 0;
  }

  PACKFILE *pf = pack_fopen_password("/tmp/qst.compressed", F_WRITE_PACKED, datapwd);

  FILE *f = fopen(inputpath, "rb");
  int c;
  while ((c = getc(f)) != EOF) {
    pack_putc(c, pf);
  }
  fclose(f);
  pack_fclose(pf);

  return encode_file_007("/tmp/qst.compressed", outpath, key, "Zelda Classic Quest File", method);
}
