#include "platform.h"
#include "complexlib/api.h"
#include "complexlib/cdefs.h"

int COMPLEXLIB_API complex_foo(int bar)
{
	return complex_add(bar, 0xBAE) & 0xF00;
}
