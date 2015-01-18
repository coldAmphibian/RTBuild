#ifndef __COMPLEXLIB_CDEFS_H__
#define __COMPLEXLIB_CDEFS_H__

#include "platform.h"
#include "api.h"

#if defined(__cplusplus)
extern "C" {
#endif

int COMPLEXLIB_API complex_foo(int bar);
int COMPLEXLIB_API complex_add(int a, int b);
void COMPLEXLIB_API __plat_link_test(void);
#if defined(__cplusplus)
}
#endif

#endif /* __COMPLEXLIB_CDEFS_H__ */
