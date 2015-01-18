#!/usr/bin/python

"""
 " Makefile Generator for RTBuild
 "
 " Copyright (C) 2014, Zane van Iperen
 " Authors: Zane van Iperen <zane.vaniperen@uqconnect.edu.au>
 "
 " This program is free software; you can redistribute it and/or modify
 " it under the terms of the GNU General Public License version 2 as
 " published by the Free Software Foundation.
"""
import sys
import os
import subprocess

from RTBuild import BuildGenerator

class MakefileGenerator(BuildGenerator):
    def __init__(self, tools):
        BuildGenerator.__init__(self)
        self.m_Tools = tools

    def _decode_props(self, props):
        decProps = {}

        decProps["CPPFLAGS"]        = ["-fvisibility=hidden", "-mno-ms-bitfields"] + self._decode_c_common_props({p:props["PROPS"][p] for p in props["PROPS"] if p.startswith("cpp.")})
        decProps["CFLAGS"]          = self._decode_c_props({p:props["PROPS"][p] for p in props["PROPS"] if p.startswith("c.")})
        decProps["CXXFLAGS"]        = self._decode_cxx_props({p:props["PROPS"][p] for p in props["PROPS"] if p.startswith("cxx.")})
        decProps["CPPDEFS"]         = ["-D{0}".format(d) for d in props["CPPDEFS"]]
        decProps["CDEFS"]           = ["-D{0}".format(d) for d in props["CDEFS"]]
        decProps["CXXDEFS"]         = ["-D{0}".format(d) for d in props["CXXDEFS"]]
        decProps["INCLUDE_DIRS"]    = ["-I{0}".format(os.path.join(os.path.dirname(sys.argv[0]), i)) for i in props["INCLUDE_DIRS"]]
        decProps["STRIP_SYMBOLS"]   = props["STRIP_SYMBOLS"]
        decProps["DEBUG"]           = props["DEBUG"]
        return decProps

    def _decode_c_common_props(self, props, chained=False):
        out = []

        if "cpp.wall" in props and props["cpp.wall"] == "true":
            out += ["-Wall", "-Wextra"]

        if "cpp.werror" in props and props["cpp.werror"] == "true":
            out += ["-Werror"]

        if "cpp.wrn-unused-parameter" in props:
            if props["cpp.wrn-unused-parameter"] == "true":
                out += ["-Wunused-parameter"]
            else:
                out += ["-Wno-unused-parameter"]

        # These just happen to correspond
        if "cpp.optimise" in props:
            out += ["-O{0}".format(props["cpp.optimise"])]

        if "cpp.lto" in props:
            if props["cpp.lto"] == "true":
                out += ["-flto"]
            elif props["cpp.lto"] == "false":
                out += ["-fno-lto"]

        return out

    def _decode_c_props(self, props):
        out = self._decode_c_common_props(props)

        if "c.standard" in props:
            if props["c.standard"] == "C89":
                out += ["-std=c89"]
            elif props["c.standard"] == "C99":
                out += ["-std=c99"]
            elif props["c.standard"] == "C11":
                out += ["-std=c11"]

        return out

    def _decode_cxx_props(self, props):
        out = self._decode_c_common_props(props)

        if "cxx.standard" in props:
            if props["cxx.standard"] == "C++98":
                out += ["-std=c++98"]
            elif props["cxx.standard"] == "C++03":
                out += ["-std=c++03"]
            elif props["cxx.standard"] == "C++11":
                out += ["-std=c++11"]
            elif props["cxx.standard"] == "C++14":
                out += ["-std=c++14"]

        return out

    def generate(self, projects, targets, props, custTools):
        BuildGenerator.generate(self, projects, targets, props, custTools)
        self.m_RawProps = props
        self.m_Properties = self._decode_props(props)

        makefile = {".PHONY": {"deps": [], "commands": []}}

        for config in projects:
            currCfg = projects[config]
            for platform in currCfg:
                currPlat = currCfg[platform]
                for project in currPlat:
                    currProj = currPlat[project]
                    currProps = {"CFLAGS":self._decode_c_props({p:currProj["PROPS"][p] for p in currProj["PROPS"] if p.startswith("c.")}),
                                 "CXXFLAGS":self._decode_cxx_props({p:currProj["PROPS"][p] for p in currProj["PROPS"] if p.startswith("cxx.")}),
                                 "CPPFLAGS":self._decode_c_common_props({p:currProj["PROPS"][p] for p in currProj["PROPS"] if p.startswith("cpp.")})}

                    makefile[".PHONY"]["deps"] += [currProj["fullname"]]

                    for f in currProj["files"]:
                        self._generate_build_command(f, targets[config][platform], self.m_Tools[config][platform],
                                                     currProj, currProps)
                        #print f
                        #exit(1)
                        buildData = f["build"]

                        mTarget = makefile[buildData["objpath"]] = {"commands": [" ".join(l for l in c) for c in buildData["buildCommand"]]}

                        #RTBuild.niceprint(mTarget)
                        try:
                            if len(buildData["depCommand"]) != 0:
                                depString = subprocess.check_output(buildData["depCommand"], shell=False,
                                                                    universal_newlines=True).split(": ", 1)
                                if len(depString) != 2:
                                    raise Exception()

                                mTarget["deps"] = [i for i in
                                                   depString[1].strip().replace('\n', '').replace('\r', '').replace(
                                                       '\\', '').split(' ') if i != '']
                            else:
                                mTarget["deps"] = []

                        except Exception as e:
                            mTarget["deps"] = []
                            sys.stderr.write(
                                "WARNING: Unable to generate dependencies for {0}: {1}\n".format(currProj["fullname"],
                                                                                                 os.path.join(f["dir"],
                                                                                                              f[
                                                                                                                  "name"])))

                    makefile[currProj["fullname"]] = {"commands": ["mkdir -p \"{0}\"".format(currProj["outdir"]),
                                                                   "rm -rf \"{0}\"".format(currProj["outpath"])],
                                                      "deps": ([d["fullname"] for d in currProj["makeDeps"]] +
                                                                 [f["build"]["objpath"] for f in currProj["files"]])}
                                                               #[{True:os.path.relpath(os.path.join(currProj["projdir"], f["build"]["objpath"]), "."), False:f["build"]["objpath"]}[f["type"].startswith("custom")] for f in currProj["files"]])}

                    #print [f["build"]["objpath"] for f in currProj["files"] if f["type"].startswith("custom")]

                    #print [{True:os.path.relpath(os.path.join(currProj["projdir"], f["build"]["objpath"]), "."), False:f["build"]["objpath"]}[f["type"].startswith("custom")] for f in currProj["files"]]

        # Calculate the project deps
        for config in projects:
            currCfg = projects[config]
            for platform in currCfg:
                currPlat = currCfg[platform]
                for project in currPlat:
                    currProj = currPlat[project]
                    makeProj = makefile[currProj["fullname"]]
                    toolset = self.m_Tools[config][platform]
                    linkArgs, linkDirs = self._calc_ext_deps(currProj, projects[config][platform])

                    if currProj["type"] == "static":
                        makeProj["commands"] += ["\t{0} rs \"{1}\"".format(toolset["AR"],
                                                                           currProj["outpath"] + " ".join(
                                                                               [f["build"]["objpath"] for f in
                                                                                currProj["files"]]))]
                    else:

                        line = [toolset["CXX"]] + toolset["LDFLAGS"]

                        # Force static linking with libgcc and libstdc++
                        line += ["-static-libstdc++", "-static-libgcc"]

                        # Who's fucking idea was it not to add . to the search path by default?
                        line += ['-Wl,-rpath=.']

                        if currProj["type"] == "module":
                            line += ["-shared"]

                        # Add the output file name
                        line += ["-o", currProj["outpath"]]

                        # Add all of the object files
                        line += [f["build"]["objpath"] for f in currProj["files"] if f["link"] == "true"]

                        # Add the linker search paths, THEN the libraries
                        line += linkArgs
                        line += linkDirs

                        makeProj["commands"] += [" ".join(i for i in line)]

                        if props["STRIP_SYMBOLS"] == "true":
                            makeProj["commands"] += ["{0} -s {1}".format(toolset["STRIP"], currProj["outpath"])]
        #RTBuild.niceprint(makefile)
        #exit(1)
        f = open("Makefile", "wb")
        f.write("".join("{0}: {1}\n{2}\n\n".format(tgt, " ".join(d for d in makefile[tgt]["deps"]),
                                                   "\n".join("\t{0}".format(c) for c in makefile[tgt]["commands"])) for
                        tgt in makefile))
        f.close()

    def _calc_ext_deps(self, current, projects):
        """
        Calculate the command arguments for linking
        :param current: The current project.
        :param projects: The list of projects
        :return: A 2-tuple of the format ([libArgs], [dirs]) :raise Exception:
        """
        linkArgs = []
        dirs = []

        # Leave makeDeps first, we want system libraries linked after
        for i in current["makeDeps"] + current["linkDeps"]:
            if i["linktype"] == "static":
                linkArgs += ["-Wl,-Bstatic", "-l{0}".format(i["name"])]
            elif i["linktype"] == "dynamic":
                linkArgs += ["-Wl,-Bdynamic", "-l{0}".format(i["name"])]
            elif i["linktype"] == "symbolic":
                linkArgs += ["-Wl,-Bsymbolic", "-l{0}".format(i["name"])]
            elif i["linktype"] == "local":
                extProj = projects[i["name"]]
                if extProj["type"] == "static":
                    linkArgs += [extProj["outpath"]]
                elif extProj["type"] == "module":
                    linkArgs += ["-Wl,-Bdynamic", extProj["outpath"]]
            else:
                raise Exception("Invalid external library type: {0}".format(i["linktype"]))

            # Now add the library search directories
            if (i["search"] != "") and (i["linktype"] != "local"): dirs += [i["search"]]

        # Restore us to linking dynamically
        linkArgs += ["-Wl,-Bdynamic"]

        return linkArgs, dirs

    def _generate_build_command(self, fEntry, target, tools, project, props):
        buildData = fEntry["build"] = {}
        command = []

        buildData["buildCommand"] = []

        # Handle ASM files first, these are a special case.
        if fEntry["type"].startswith("custom"):
            fEntry["objdir"] = os.path.dirname(fEntry["output"])
            buildData["buildCommand"] += [["cd", project["projdir"], ";", "mkdir", "-p", fEntry["objdir"]] + [";"] + fEntry["command"]]
            #buildData["buildCommand"] += [["cd", project["projdir"]], [["mkdir", "-p", fEntry["objdir"], ";"] + fEntry["command"]], ["cd", os.path.relpath(".", project["projdir"])]]
            buildData["depCommand"] = []
            buildData["objpath"] = os.path.relpath(os.path.join(project["projdir"], fEntry["output"]), ".")

        # Now handle C, C++ files. These are done together, as they have so much in common
        elif fEntry["type"] in ["c", "cpp"]:
            buildFlags = self.m_Properties["INCLUDE_DIRS"] + ["-c"] + {True: ["-g"], False: []}[self.m_Properties["DEBUG"] == "true"] + self.m_Properties["CPPFLAGS"] + \
                         tools["CPPFLAGS"] + props["CPPFLAGS"]

            buildData["objpath"] = os.path.join(fEntry["objdir"], fEntry["name"] + ".o")

            buildData["buildCommand"] += [["mkdir", "-p", fEntry["objdir"]]]
            # Generate the build command
            depCommand = []

            if fEntry["type"] == "c":
                command += [tools["CC"]]
                depCommand += [tools["CC"]]
                buildFlags += self.m_Properties["CFLAGS"] + tools["CFLAGS"] + props["CFLAGS"] + self._decode_c_props(fEntry["PROPS"])
            elif fEntry["type"] == "cpp":
                command += [tools["CXX"]]
                depCommand += [tools["CXX"]]
                buildFlags += self.m_Properties["CXXFLAGS"] + tools["CXXFLAGS"] + props["CXXFLAGS"] + self._decode_cxx_props(fEntry["PROPS"])

            defFlags = ["-D{0}".format(d) for d in fEntry["defines"]]
            command += defFlags + buildFlags

            if project["type"] == "module" and tools["PICFLAG"] == "true":
                command += ["-fPIC"]

            depCommand += ["-MM"] + defFlags + buildFlags

            depCommand += [fEntry["fullpath"]]
            command += ["-o", buildData["objpath"], fEntry["fullpath"]]

            buildData["buildflags"] = buildFlags
            buildData["buildCommand"] += [command]
            buildData["depCommand"] = depCommand
