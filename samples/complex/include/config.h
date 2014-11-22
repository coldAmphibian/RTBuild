#ifndef __CONFIG_H__
#define __CONFIG_H__

/* These must match up with the ones in gen_complex.py */

/* PLATFORMS */
#define COMPLEX_PLATFORM_WINDOWS	1
#define COMPLEX_PLATFORM_NIX		2
#define COMPLEX_PLATFORM_MAC		3

/* Arch */
#define COMPLEX_ARCH_X86		1
#define COMPLEX_ARCH_X64		2

/* Endians */
#define COMPLEX_ENDIANNESS_LITTLE	1
#define COMPLEX_ENDIANNESS_BIG		2

#endif /* __CONFIG_H__ */
