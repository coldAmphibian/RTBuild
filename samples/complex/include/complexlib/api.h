#ifndef __COMPLEXLIB_API_H__
#define __COMPLEXLIB_API_H__

#include "platform.h"
#ifdef COMPLEXLIB_EXPORTS
#	define COMPLEXLIB_API DLLEXPORT
#else
#	define COMPLEXLIB_API DLLIMPORT
#endif

#endif /* __COMPLEXLIB_API_H__ */
