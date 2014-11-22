#!/usr/bin/python
import os.path, sys

# Hack the path to allow us to import RTBuild from our parent directory.
sys.path.append(os.path.realpath(os.path.join(__file__, "../../..")))

from RTBuild import *
from MakefileGenerator import *
from MSVCGenerator import *

# These must match up with the ones in config.h
COMPLEX_ARCH_X86 = 1
COMPLEX_ARCH_X64 = 2

COMPLEX_PLATFORM_WINDOWS = 1
COMPLEX_PLATFORM_NIX = 2
COMPLEX_PLATFORM_MAC = 3

COMPLEX_ENDIANNESS_LITTLE = 1
COMPLEX_ENDIANNESS_BIG = 2
COMPLEX_ENDIANNESS_MIXED = 3

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
                                "COMPLEX_ARCH=" + str(COMPLEX_ARCH_X64),
                                "COMPLEX_PLATFORM=" + str(COMPLEX_PLATFORM_NIX),
                                "COMPLEX_ENDIANNESS=" + str(COMPLEX_ENDIANNESS_LITTLE),
                                "COMPLEX_POSIX",
                                "COMPLEX_PLATSTRING=\"\\\"x86_64-generic-Linux\\\"\"",
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
                                "COMPLEX_ARCH=" + str(COMPLEX_ARCH_X86),
                                "COMPLEX_PLATFORM=" + str(COMPLEX_PLATFORM_NIX),
                                "COMPLEX_ENDIANNESS=" + str(COMPLEX_ENDIANNESS_LITTLE),
                                "COMPLEX_POSIX",
                                "COMPLEX_PLATSTRING=\"\\\"x86-generic-Linux\\\"\"",
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
                                "COMPLEX_ARCH=" + str(COMPLEX_ARCH_X64),
                                "COMPLEX_PLATFORM=" + str(COMPLEX_PLATFORM_WINDOWS),
                                "COMPLEX_ENDIANNESS=" + str(COMPLEX_ENDIANNESS_LITTLE),
                                "COMPLEX_PLATSTRING=\"\\\"x86_64-generic-Windows\\\"\"",
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
                                "COMPLEX_ARCH=" + str(COMPLEX_ARCH_X86),
                                "COMPLEX_PLATFORM=" + str(COMPLEX_PLATFORM_WINDOWS),
                                "COMPLEX_ENDIANNESS=" + str(COMPLEX_ENDIANNESS_LITTLE),
                                "COMPLEX_PLATSTRING=\"\\\"x86-generic-Windows\\\"\"",
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


DEBUG = True
RELEASE = False

cppProps = {"wall": "true", "wrn-unused-parameter": "false"}
cppDefs = []

if DEBUG:
    cppProps["optimise"] = "0"
    cppProps["lto"] = "false"
    cppDefs += ["COMPLEX_DEBUG"]
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
