#ifndef __PLATFORM_H__
#define __PLATFORM_H__

#define __STDC_FORMAT_MACROS
#define _FILE_OFFSET_BITS 64
#define _XOPEN_SOURCE 700

#include <stdlib.h>
#include <stdio.h>
#include <stdarg.h>
#include <stdint.h>
#include <inttypes.h>
#include <errno.h>
#include <string.h>
#include <assert.h>
#include <fcntl.h>
#include <wchar.h>
#include <time.h>
#include <ctype.h>
#include <sys/stat.h>

#if !defined(__cplusplus)
#	include <stdbool.h>
#else
#	include <new>
#	include <exception>
#	include <utility>
#	include <typeinfo>
#endif

#include "config.h"

/*#if COMPLEX_PLATFORM == COMPLEX_PLATFORM_NIX
#	define COMPLEX_POSIX
#elif COMPLEX_PLATFORM == COMPLEX_PLATFORM_MAC
#	define COMPLEX_POSIX
#elif COMPLEX_PLATFORM == COMPLEX_PLATFORM_WINDOWS
#	undef COMPLEX_POSIX
#endif*/

#if !defined(_WIN32)
#	define __fastcall __attribute__((fastcall))
#	define __forceinline __attribute__((always_inline))
#endif

#if COMPLEX_ARCH == COMPLEX_ARCH_X86
#	define ASMCALL __fastcall
#elif COMPLEX_ARCH == COMPLEX_ARCH_X64
#	define ASMCALL
#else
#	error "ERROR: Invalid architecture specified."
#endif

#if COMPLEX_PLATFORM == COMPLEX_PLATFORM_WINDOWS
#	if defined(_MSC_VER) /* For CL */
#		define DLLEXPORT __declspec(dllexport)
#		define DLLIMPORT __declspec(dllimport)
#		if _MSC_VER <= 1800 /* MSVC 2013 and below don't support noexcept */
#			define NOEXCEPT
#		endif
typedef SSIZE_T ssize_t;
#	elif defined(__GNUC__) /* For MinGW */
#		define DLLEXPORT __attribute__((dllexport))
#		define DLLIMPORT __attribute__((dllimport))
#	endif
typedef int64_t foff_t;
#else
typedef off_t foff_t;
#	define DLLEXPORT __attribute__((visibility("default")))
#	define DLLIMPORT
#endif

#ifndef NOEXCEPT
#	define NOEXCEPT noexcept
#endif

#if defined(COMPLEX_DEBUG)
#	if defined(_MSC_VER)
#		define DO_TRAP()	__asm { int 3 }
#	elif defined(__GNUC__)
#		define DO_TRAP()	asm volatile(".intel_syntax\nint 0x03\n.att_syntax")
#	endif
#endif

#endif /* __PLATFORM_H__ */
