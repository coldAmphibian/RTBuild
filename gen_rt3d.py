#!/usr/bin/python
from RTBuild import RTBuild
from MakefileGenerator import MakefileGenerator
from MSVCGenerator import MSVCGenerator

# These must match up with the ones in config.h
RT3D_ARCH_X86 = 1
RT3D_ARCH_X64 = 2

RT3D_PLATFORM_WINDOWS = 1
RT3D_PLATFORM_NIX = 2
RT3D_PLATFORM_MAC = 3
RT3D_PLATFORM_POSIX = 4

RT3D_ENDIANNESS_LITTLE = 1
RT3D_ENDIANNESS_BIG = 2
RT3D_ENDIANNESS_MIXED = 3

gcc_tools = \
    {
        "Linux":
            {
                "x86_64-generic":
                    {
                        "CC": "x86_64-linux-gnu-gcc",
                        "CFLAGS": [],
                        "CXX": "x86_64-linux-gnu-g++",
                        "CXXFLAGS": [],
                        "CPPFLAGS": ["-m64"],
                        "ASM": "yasm",
                        "ASMFLAGS": ["-f elf64"],
                        "AR": "x86_64-linux-gnu-gcc-ar",
                        "STRIP": "strip",
                        "LDFLAGS": ["-m64"],
                    },
                "x86-generic":
                    {
                        "CC": "x86_64-linux-gnu-gcc",
                        "CFLAGS": [],
                        "CXX": "x86_64-linux-gnu-g++",
                        "CXXFLAGS": [],
                        "CPPFLAGS": ["-m32"],
                        "ASM": "yasm",
                        "ASMFLAGS": ["-f elf32"],
                        "AR": "x86_64-linux-gnu-gcc-ar",
                        "STRIP": "strip",
                        "LDFLAGS": ["-m32"],
                    },
            },
        "Windows":
            {
                "x86_64-generic":
                    {
                        "CC": "x86_64-w64-mingw32-gcc",
                        "CFLAGS": [],
                        "CXX": "x86_64-w64-mingw32-g++",
                        "CXXFLAGS": [],
                        "CPPFLAGS": ["-m64"],
                        "ASM": "yasm",
                        "ASMFLAGS": ["-f win64"],
                        "AR": "x86_64-w64-mingw32-ar",
                        "STRIP": "x86_64-w64-mingw32-strip",
                        "LDFLAGS": ["-m64"],
                    },
                "x86-generic":
                    {
                        "CC": "i686-w64-mingw32-gcc",
                        "CFLAGS": [],
                        "CXX": "i686-w64-mingw32-g++",
                        "CXXFLAGS": [],
                        "CPPFLAGS": ["-m32"],
                        "ASM": "yasm",
                        "ASMFLAGS": ["-f win32"],
                        "AR": "i686-w64-mingw32-ar",
                        "STRIP": "i686-w64-mingw32-strip",
                        "LDFLAGS": ["-m32"],
                    },
            }
    }

targets = \
    {
        "Linux":
            {
                "x86_64-generic":
                    {
                        "CPROPS": {},
                        "CXXPROPS": {},
                        "CPPPROPS": {},
                        "CDEFS": [],
                        "CXXDEFS": [],
                        "CPPDEFS":
                            [
                                "RT3D_ARCH=" + str(RT3D_ARCH_X64),
                                "RT3D_PLATFORM=" + str(RT3D_PLATFORM_NIX),
                                "RT3D_ENDIANNESS=" + str(RT3D_ENDIANNESS_LITTLE),
                                "RT3D_POSIX",
                                "RT3D_PLATSTRING=\"x86_64-generic-Linux\"",
                            ],
                        "EXEEXT": "",
                        "DLLEXT": ".so",
                        "LIBEXT": ".a",
                        "OBJEXT": ".o",
                        "CUSTOMTOOLS":
                        {
                            "yasm": { "EXE": "yasm", "FLAGS": ["-f", "elf64", "-o", "%OUT%", "%IN%"] },
                            "nasm": { "EXE": "nasm", "FLAGS": ["-f", "elf64", "-o", "%OUT%", "%IN%"] },
                        },
                    },
                "x86-generic":
                    {
                        "CPROPS": {},
                        "CXXPROPS": {},
                        "CPPPROPS": {},
                        "CDEFS": [],
                        "CXXDEFS": [],
                        "CPPDEFS":
                            [
                                "RT3D_ARCH=" + str(RT3D_ARCH_X86),
                                "RT3D_PLATFORM=" + str(RT3D_PLATFORM_NIX),
                                "RT3D_ENDIANNESS=" + str(RT3D_ENDIANNESS_LITTLE),
                                "RT3D_POSIX",
                                "RT3D_PLATSTRING=\"x86-generic-Linux\"",
                            ],
                        "EXEEXT": "",
                        "DLLEXT": ".so",
                        "LIBEXT": ".a",
                        "OBJEXT": ".o",
                        "CUSTOMTOOLS":
                        {
                            "yasm": { "EXE": "yasm", "FLAGS": ["-f", "elf32", "-o", "%OUT%", "%IN%"] },
                            "nasm": { "EXE": "nasm", "FLAGS": ["-f", "elf32", "-o", "%OUT%", "%IN%"] },
                        },
                    },
            },
        "Windows":
            {
                "x86_64-generic":
                    {
                        "CPROPS": {},
                        "CXXPROPS": {},
                        "CPPPROPS": {},
                        "CDEFS": [],
                        "CXXDEFS": [],
                        "CPPDEFS":
                            [
                                "RT3D_ARCH=" + str(RT3D_ARCH_X64),
                                "RT3D_PLATFORM=" + str(RT3D_PLATFORM_WINDOWS),
                                "RT3D_ENDIANNESS=" + str(RT3D_ENDIANNESS_LITTLE),
                                "RT3D_PLATSTRING=\"x86_64-generic-Windows\"",
                            ],
                        "EXEEXT": ".exe",
                        "DLLEXT": ".dll",
                        "LIBEXT": ".a",
                        "OBJEXT": ".obj",
                        "CUSTOMTOOLS":
                        {
                            "yasm": { "EXE": "yasm", "FLAGS": ["-f", "win64", "-o", "%OUT%", "%IN%"] },
                            "nasm": { "EXE": "nasm", "FLAGS": ["-f", "win64", "-o", "%OUT%", "%IN%"] },
                        },
                    },
                "x86-generic":
                    {
                        "CPROPS": {},
                        "CXXPROPS": {},
                        "CPPPROPS": {},
                        "CDEFS": [],
                        "CXXDEFS": [],
                        "CPPDEFS":
                            [
                                "RT3D_ARCH=" + str(RT3D_ARCH_X86),
                                "RT3D_PLATFORM=" + str(RT3D_PLATFORM_WINDOWS),
                                "RT3D_ENDIANNESS=" + str(RT3D_ENDIANNESS_LITTLE),
                                "RT3D_PLATSTRING=\"x86-generic-Windows\"",
                            ],
                        "EXEEXT": ".exe",
                        "DLLEXT": ".dll",
                        "LIBEXT": ".a",
                        "OBJEXT": ".obj",
                        "CUSTOMTOOLS":
                        {
                            "yasm": { "EXE": "yasm", "FLAGS": ["-f", "win32", "-o", "%OUT%", "%IN%"] },
                            "nasm": { "EXE": "nasm", "FLAGS": ["-f", "win32", "-o", "%OUT%", "%IN%"] },
                        },
                    },
            }
    }


DEBUG = False
RELEASE = True

cppProps = {"wall": "true", "wrn-unused-parameter": "false"}
cppDefs = []

if DEBUG:
    cppProps["optimise"] = "0"
    cppProps["lto"] = "false"
    cppDefs += ["RT3D_DEBUG"]
elif RELEASE:
    cppProps["optimise"] = "3"
    cppProps["lto"] = "true"
    cppProps["werror"] = "true"

build = RTBuild(".", targets,
                CPPPROPS=cppProps,
                CPROPS={"standard": "C99"},
                CXXPROPS={"standard": "C++11"},

                CPPDEFS = cppDefs,
                CDEFS = [],
                CXXDEFS = [],

                INCLUDE_DIRS=["include"],
                STRIP_SYMBOLS={True:"false", False:"true"}[DEBUG],
                DEBUG={True: "true", False: "false"}[DEBUG]
)

build.generate(MSVCGenerator(["Windows"], {"x64":["x86_64-*"], "Win32":["x86-*"]}))
build.generate(MakefileGenerator(gcc_tools))
