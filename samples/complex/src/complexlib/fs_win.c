#include "platform.h"
#include "complexlib/cdefs.h"

COMPLEXLIB_API int fs_fseeko(FILE *stream, foff_t offset, int whence)
{
	return _fseeki64(stream, offset, whence);
}
