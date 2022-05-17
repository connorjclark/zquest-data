#include <allegro.h>
#include <sys/stat.h>

int *allegro_errno;
SYSTEM_DRIVER *system_driver = NULL;
void _add_exit_func(void (*func)(void), AL_CONST char *desc) {}
void _remove_exit_func(void (*func)(void), AL_CONST char *desc) {}

void get_executable_name(char *output, int size) {}

int _al_file_isok(const char *filename) { return TRUE; }

uint64_t _al_file_size_ex(AL_CONST char *filename)
{
  struct stat stat_buf;
  int rc = stat(filename, &stat_buf);
  return rc == 0 ? stat_buf.st_size : -1;
}

time_t _al_file_time(AL_CONST char *filename)
{
  struct stat stat_buf;
  int rc = stat(filename, &stat_buf);
  return rc == 0 ? stat_buf.st_mtime : 0;
}

void _al_free(void *mem)
{
  free(mem);
}

void *_al_malloc(size_t size)
{
  return malloc(size);
}

void *_al_realloc(void *mem, size_t size)
{
  return realloc(mem, size);
}

char *_al_strdup(AL_CONST char *string)
{
  char *newstring = _al_malloc(strlen(string) + 1);

  if (newstring)
    strcpy(newstring, string);

  return newstring;
}

void _al_getdcwd(int drive, char *buf, int size) {}

int al_findfirst(AL_CONST char *pattern, struct al_ffblk *info, int attrib) { return 0; }
int al_findnext(struct al_ffblk *info) { return 0; }
void al_findclose(struct al_ffblk *info) {}
