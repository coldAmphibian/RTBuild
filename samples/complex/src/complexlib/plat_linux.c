#include "platform.h"
#include "complexlib/cdefs.h"
#include <dlfcn.h>

COMPLEXLIB_API int fs_fseeko(FILE *stream, foff_t offset, int whence)
{
	return fseeko(stream, offset, whence);
}

COMPLEXLIB_API void __plat_link_test(void)
{
	/* Check if dl is linking correctly. */
	(void)dlerror();
}
