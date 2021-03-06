#!/usr/bin/python

import sys, os
# Hack the path to allow us to import RTBuild from our parent directory.
sys.path.append(os.path.realpath(os.path.join(__file__, "../../..")))

from MakefileGenerator import *
from MSVCGenerator import *
from RTBuild import *

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
                        "PICFLAG": "true",
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
                        "PICFLAG": "true",
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
                        "PICFLAG": "false",
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
                        "PICFLAG": "false",
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
                    },
            }
    }


class YASMTool(CustomTool):
    def generate_build_command(self, fEntry, target, globalProps, configuration, platform, subProc):

        if target["OBJEXT"] == ".o":
            if fnmatch.fnmatch(platform, "x86-*"):
                outFormat = "elf32"
            elif fnmatch.fnmatch(platform, "x86_64-*"):
                outFormat = "elf64"
        elif target["OBJEXT"] == ".obj":
            if fnmatch.fnmatch(platform, "x86-*"):
                outFormat = "win32"
            elif fnmatch.fnmatch(platform, "x86_64-*"):
                outFormat = "win64"

        return [subProc(i) for i in ["yasm", "-f", outFormat, "-o", "%OUT%", "%IN%"]]

    def get_tool_name(self):
        return "yasm"

DEBUG = True
RELEASE = False

props = {"cpp.wall": "true", "cpp.wrn-unused-parameter": "false", "c.standard": "C99", "cxx.standard": "C++11"}

cppDefs = []

if DEBUG:
    props["cpp.optimise"] = "0"
    props["cpp.lto"] = "false"
    cppDefs += ["COMPLEX_DEBUG"]
elif RELEASE:
    props["cpp.optimise"] = "3"
    props["cpp.lto"] = "true"
    props["cpp.werror"] = "true"

build = RTBuild(".", targets, [], [YASMTool()],
                PROPS=props,
                CPPDEFS = cppDefs,
                CDEFS = [],
                CXXDEFS = [],

                INCLUDE_DIRS=["include"],
                STRIP_SYMBOLS={True:"false", False:"true"}[DEBUG],
                DEBUG={True: "true", False: "false"}[DEBUG]
)

#build.generate(MSVCGenerator(["Windows"], {"x64":["x86_64-*"], "Win32":["x86-*"]}))
build.generate(MakefileGenerator(gcc_tools))
