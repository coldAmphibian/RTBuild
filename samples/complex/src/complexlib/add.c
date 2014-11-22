#include "platform.h"
#include "complexlib/api.h"

#if COMPLEX_ARCH == COMPLEX_ARCH_X86
extern int ASMCALL asmadd(int a, int b);
#	define __asmadd__ asmadd
#elif COMPLEX_ARCH == COMPLEX_ARCH_X64
extern int ASMCALL asmadd_win32(int a, int b);
extern int ASMCALL asmadd_sysv(int a, int b);
#	if COMPLEX_PLATFORM == COMPLEX_PLATFORM_WINDOWS
#		define __asmadd__ asmadd_win32
#	else
#		define __asmadd__ asmadd_sysv
#	endif
#endif

int COMPLEXLIB_API complex_add(int a, int b)
{
	return __asmadd__(a, b);
}

#undef __asmadd__
