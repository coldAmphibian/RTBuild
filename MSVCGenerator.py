#!/usr/bin/python

"""
 " MSBuild Project Generator for RTBuild
 "
 " Copyright (C) 2014, Zane van Iperen
 " Authors: Zane van Iperen <zane.vaniperen@uqconnect.edu.au>
 "
 " This program is free software; you can redistribute it and/or modify
 " it under the terms of the GNU General Public License version 2 as
 " published by the Free Software Foundation.
"""

import os
import fnmatch
import copy
import xml.etree.ElementTree as XMLTree
from RTBuild import BuildGenerator

def generate_guid():
    """
    Generate a MSBuild-formatted GUID
    :return: A MSBuild-formatted GUID
    :rtype: str
    """
    import uuid
    return "{{{0}}}".format(str(uuid.uuid4()).upper())

class VCXFilter(object):
    """
    Represents a MSBuild filters file.
    """
    def __init__(self):
        self.m_Root = XMLTree.Element("Project", ToolsVersion="4.0", xmlns="http://schemas.microsoft.com/developer/msbuild/2003")
        self.m_Filters = set()

        self.m_Defs = XMLTree.Element("ItemGroup")
        self.m_Files = XMLTree.Element("ItemGroup")

        self.m_Root.append(self.m_Defs)
        self.m_Root.append(self.m_Files)

    def add_file(self, file, type, filter):
        """
        Add a file to the filter.
        :param file: The name of the file.
        :param type: The type of the file, i.e. "ClCompile"
        :param filter: The name of the filter, i.e. "Platform\Windows"

        :type file: str
        :type type: str
        :type filter: str
        """
        components = filter.split('\\')
        for i in range(len(components)):
            self.m_Filters.add("\\".join(c for c in components[0:len(components) - i]))

        entry = XMLTree.Element(type, Include=file)
        if filter not in [None, ""]:
            tmp = XMLTree.Element("Filter")
            tmp.text = filter
            entry.append(tmp)

        self.m_Files.append(entry)

    def write(self, file):
        """
        Write the filters to the specified file.
        :param file: The name of the output file.

        :type file: str
        """
        for filter in self.m_Filters:
            element = XMLTree.Element("Filter", Include=filter)
            guid = XMLTree.Element("UniqueIdentifier")
            guid.text = generate_guid()
            element.append(guid)
            self.m_Defs.append(element)

        import xml.dom.minidom
        f = open(file, "w")
        f.write(xml.dom.minidom.parseString(XMLTree.tostring(self.m_Root, 'utf-8')).toprettyxml(indent='\t'))
        f.close()

class MSVCGenerator(BuildGenerator):
    def __init__(self, winConfig, winPlatform):
        BuildGenerator.__init__(self)

        self.m_WinConfig = copy.deepcopy(winConfig)
        self.m_WinPlatform = copy.deepcopy(winPlatform)

    def _preprocess(self):
        vcxProj = {}
        for config in self.m_Projects:
            if True not in [fnmatch.fnmatch(config, i) for i in self.m_WinConfig]:
                continue

            currCfg = self.m_Projects[config]
            for platform in currCfg:

                vFlag = False
                for p in self.m_WinPlatform:
                    vFlag = True in [fnmatch.fnmatch(platform, m) for m in self.m_WinPlatform[p]]
                    if vFlag: break

                if not vFlag:
                    continue

                currPlat = currCfg[platform]
                for project in currPlat:
                    currProj = currPlat[project]

                    if project not in vcxProj:
                        vcxProj[project] = {"guid":generate_guid(),
                                            "vcxPath":os.path.relpath(os.path.join(currProj["projdir"], project + ".vcxproj"), "."),
                                            "vcxDir":currProj["projdir"],
                                            "configs":{},
                                            "vcxDeps":{},
                                            "name":project,
                                            "intdir":currProj["intdir"]}

                    vcx = vcxProj[project]

                    if config not in vcx["configs"]:
                        vcx["configs"][config] = {}

                    vcx["configs"][config][platform] = self._process_props(vcx, currProj)
                    vcx["vcxDeps"] = [copy.deepcopy(dep) for dep in currProj["makeDeps"]]

                    vcx["files"] = {}


                    for cfg in self.m_Projects:
                        for plats in self.m_Projects[cfg]:

                            projFiles = self.m_Projects[cfg][plats][project]["files"]

                            for f in projFiles:
                                if f["fullpath"] not in vcx["files"]:
                                    vcx["files"][f["fullpath"]] = {}

                                vf = vcx["files"][f["fullpath"]]

                                if "configs" not in vf:
                                    vf["configs"] = {}

                                if cfg not in vf["configs"]:
                                    vf["configs"][cfg] = {}

                                vf["configs"][cfg][plats] = f

                                vf["type"] = f["type"]
                                vf["fullpath"] = f["fullpath"]
                                vf["name"] = f["name"]
                                vf["dir"] = f["dir"]
                                vf["link"] = f["link"]

                                #if vf["type"].startswith("custom"):

        return vcxProj

    def generate(self, projects, targets, props, custTools):
        BuildGenerator.generate(self, projects, targets, props, custTools)

        solName = "Solution.sln"
        solGUID = generate_guid()

        self.m_VCXProjects = self._preprocess()

        globalLines = []
        tmpLines, platforms = self._globgen_sol_config()
        globalLines += tmpLines
        globalLines += self._globgen_sol_proj(platforms)
        globalLines += self._globgen_sol_prop()

        projectLines = self._projgen(solGUID)

        f = open(solName, "w")

        # Write the header
        f.write("Microsoft Visual Studio Solution File, Format Version 12.00\n")
        f.write("# Visual Studio 2013\n")

        # Write the Project Entries
        f.write("".join("%s\n" % i for i in projectLines))

        # Write the Global section
        f.write("Global\n")
        f.write("".join("\t%s\n" % l for l in globalLines))
        f.write("EndGlobal\n")

        f.close()

        self._generate_msvc_projects(self.m_VCXProjects, projects, platforms, targets)

    def _process_props(self, vcxProj, rawProj):
        outDict = {}
        outDict["PROPS"] = dict(self.m_Properties["PROPS"].items() + rawProj["PROPS"].items())
        #outDict["CPROPS"] = dict(self.m_Properties["CPROPS"].items() + rawProj["CPROPS"].items())
        #outDict["CXXPROPS"] = dict(self.m_Properties["CXXPROPS"].items() + rawProj["CXXPROPS"].items())
        return outDict

    def _generate_msvc_projects(self, vcxProjects, rawProjects, platforms, targets):
        propDict = {}

        for projName in vcxProjects:
            vcxProj = vcxProjects[projName]

            root = XMLTree.Element("Project", DefaultTargets="Build", ToolsVersion="12.0", xmlns="http://schemas.microsoft.com/developer/msbuild/2003")
            vcxFilter = VCXFilter()
            # Add the project configurations
            self._add_configurations(root, vcxProj, platforms)

            # Add the "Globals" PropertyGroup
            globalProps = XMLTree.Element("PropertyGroup", Label="Globals")
            root.append(globalProps)

            tmp = XMLTree.Element("ProjectGuid")

            tmp.text = vcxProj["guid"]
            globalProps.append(tmp)

            tmp = XMLTree.Element("RootNamespace")
            tmp.text = projName
            globalProps.append(tmp)

            root.append(XMLTree.Element("Import", Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props"))

            # Add the "General" property page and generate the project properties
            for p in platforms:
                makProj = rawProjects[p["config"]][p["platform"]][projName]

                if p["config"] not in propDict:
                    propDict[p["config"]] = {}

                if p["platform"] not in propDict[p["config"]]:
                    propDict[p["config"]][p["platform"]] = {}

                props = vcxProj["configs"][p["config"]][p["platform"]]

                tmp = XMLTree.Element("PropertyGroup", Condition="'$(Configuration)|$(Platform)'=='{0}'".format(p["project_target"]), Label="Configuration")
                root.append(tmp)

                # No unicode 5 u
                tmp2 = XMLTree.Element("CharacterSet")
                tmp2.text = "NotSet"
                tmp.append(tmp2)

                tmp2 = XMLTree.Element("PlatformToolset")
                tmp2.text = "v120"
                tmp.append(tmp2)

                tmp2 = XMLTree.Element("ConfigurationType")
                type = makProj["type"]
                if type == "executable":
                    tmp2.text = "Application"
                elif type == "module":
                    tmp2.text = "DynamicLibrary"
                elif type == "static":
                    tmp2.text = "StaticLibrary"
                else:
                    tmp2.text = "Unknown"
                tmp.append(tmp2)

                tmp2 = XMLTree.Element("UseDebugLibraries")
                tmp2.text = self.m_Properties["DEBUG"]
                tmp.append(tmp2)

                genProps = self._generate_props(props["PROPS"])
                for prop in genProps:
                    e = XMLTree.Element(prop)
                    e.text = genProps[prop]
                    tmp.append(e)

                """
                <TreatWarningAsError Condition="'$(Configuration)|$(Platform)'=='x86_64-generic-Windows|x64'">true</TreatWarningAsError>
                <WarningLevel Condition="'$(Configuration)|$(Platform)'=='x86_64-generic-Windows|x64'">EnableAllWarnings</WarningLevel>
                """
            tmp = XMLTree.Element("Import", Project="$(VCTargetsPath)\Microsoft.Cpp.props")
            root.append(tmp)

            for p in platforms:
                tmp = XMLTree.Element("ImportGroup", Label="PropertySheets", Condition="'$(Configuration)|$(Platform)'=='{0}'".format(p["project_target"]))
                tmp2 = XMLTree.Element("Import", Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props",
                                       Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')",
                                       Label="LocalAppDataPlatform")
                tmp.append(tmp2)
                root.append(tmp)

            root.append(XMLTree.Element("PropertyGroup", Label="UserMacros"))

            makProj = {}

            # Do the project-wide properties. Note that these have to be done AFTER the ImportGroup thingos
            for p in platforms:
                proj = vcxProj
                makProj = rawProjects[p["config"]][p["platform"]][projName]

                tmp = XMLTree.Element("PropertyGroup", Condition="'$(Configuration)|$(Platform)'=='{0}'".format(p["project_target"]))
                root.append(tmp)

                tmp2 = XMLTree.Element("OutDir")
                tmp2.text = os.path.join(os.path.relpath(makProj["outdir"], vcxProj["vcxDir"]), "")
                tmp.append(tmp2)

                name, ext = os.path.splitext(makProj["outfile"])

                tmp2 = XMLTree.Element("TargetName")
                tmp2.text = name
                tmp.append(tmp2)

                tmp2 = XMLTree.Element("TargetExt")
                tmp2.text = ext
                tmp.append(tmp2)

                tmp2 = XMLTree.Element("IntDir")
                tmp2.text = os.path.join(os.path.relpath(makProj["intdir"], vcxProj["vcxDir"]), "")
                tmp.append(tmp2)
            for p in platforms:
                tmp = XMLTree.Element("ItemDefinitionGroup", Condition="'$(Configuration)|$(Platform)'=='{0}'".format(p["project_target"]))
                root.append(tmp)
                tmp2 = XMLTree.Element("ClCompile")
                tmp.append(tmp2)

                tmp3 = XMLTree.Element("AdditionalIncludeDirectories")
                tmp3.text = ";".join([os.path.relpath(i, os.path.dirname(vcxProj["vcxPath"])) for i in self.m_Properties["INCLUDE_DIRS"]])
                tmp2.append(tmp3)

                tmp3 = XMLTree.Element("PreprocessorDefinitions")
                makProj = rawProjects[p["config"]][p["platform"]][projName]
                tmp3.text = ";".join(d for d in (targets[p["config"]][p["platform"]]["CPPDEFS"] + self.m_Properties["CPPDEFS"]) + makProj["CPPDEFS"])
                tmp2.append(tmp3)

            root.append(XMLTree.Element("Import", Project="$(VCTargetsPath)\Microsoft.Cpp.targets"))

            # Now we can finally add the files
            tmp = XMLTree.Element("ItemGroup")
            root.append(tmp)

            for fName in vcxProj["files"]:
                f = vcxProj["files"][fName]
                if f["type"].startswith("custom"):
                    self._write_custom_target(tmp, f, vcxProj, rawProjects, platforms, targets)
                elif f["type"] in ["c", "cpp"]:
                    self._write_clcompile_target(tmp, f, vcxProj, rawProjects, platforms, targets)

                self._write_filter(f, vcxFilter)

            # Add inter-project deps
            tmp = XMLTree.Element("ItemGroup")
            for dep in vcxProj["vcxDeps"]:
                depProj = vcxProjects[dep["name"]]
                tmp2 = XMLTree.Element("ProjectReference", Include=os.path.relpath(depProj["vcxPath"], vcxProj["vcxDir"]))
                tmp.append(tmp2)
                tmp3 = XMLTree.Element("Project")
                tmp2.append(tmp3)
                tmp3.text = depProj["guid"]
            root.append(tmp)

            import xml.dom.minidom
            vcxFile = open(vcxProj["vcxPath"], "w")

            vcxFile.write(xml.dom.minidom.parseString(XMLTree.tostring(root, 'utf-8')).toprettyxml(indent='\t'))
            vcxFile.close()

            vcxFilter.write(vcxProj["vcxPath"] + ".filters")

    def _write_filter(self, f, outFilter):
        """

        :param f:
        :param outFilter:
        :return:

        :type outFilter: VCXFilter
        """
        inFile = os.path.join(f["dir"], f["name"])
        if f["type"] in ["c", "cpp"]:
            type = "ClCompile"
        else:
            type = "CustomBuild"

        # Get the filter out of any config:platform pair, they should all
        # be the same anyway
        for config in f["configs"]:
            for plat in f["configs"][config]:
                tmp = f["configs"][config][plat]
                if "ide.filter" in tmp["PROPS"]:
                    outFilter.add_file(inFile, type, tmp["PROPS"]["ide.filter"].replace('/', '\\'))
                break
            break

    def _write_clcompile_target(self, root, f, vcxProj, rawProjects, platforms, targets):
        inFile = os.path.join(f["dir"], f["name"])
        tmp = XMLTree.Element("ClCompile", Include=inFile)
        for p in platforms:
            condString = "'$(Configuration)|$(Platform)'=='{0}'".format(p["project_target"])
            vcxFile = vcxProj["files"][f["fullpath"]]
            try:
                vf = vcxFile["configs"][p["config"]][p["platform"]]
                output = os.path.join(vf["objdir"], vf["name"] + ".obj")
            except KeyError as e:
                tmp2 = XMLTree.Element("ExcludedFromBuild", Condition=condString)
                tmp2.text = "true"
                tmp.append(tmp2)
                continue

            tmp2 = XMLTree.Element("ExcludedFromBuild", Condition=condString)
            tmp2.text = "false"
            tmp.append(tmp2)

            tmp2 = XMLTree.Element("ObjectFileName", Condition=condString)
            tmp2.text = os.path.relpath(output, vcxProj["vcxDir"])
            tmp.append(tmp2)

            [tmp.append(i) for i in self._generate_optimisation(vf["PROPS"], condString)]
            # TODO TODO

        root.append(tmp)

    @staticmethod
    def _generate_props(props):
        ret = {}
        if "cpp.lto" in props:
            ret["WholeProgramOptimisation"] = props["cpp.lto"]

        if "cpp.optimise" in props:
            level = props["cpp.optimise"]
            if level == "0":
                tmp = "Disabled"
            elif level == "1":
                tmp = "Custom"
                ret["FavorSizeOrSpeed"] = "Speed"
            elif level == "2":
                tmp = "MaxSpeed"
            elif level == "3":
                tmp = "Full"
            elif level == "s":
                tmp = "MinSpace"
            else:
                tmp = "Fuck."

            ret["Optimization"] = tmp

        if "cpp.werror" in props:
            ret["TreatWarningAsError"] = props["cpp.werror"]

        if "cpp.wall" in props:
            if props["cpp.wall"] == "true":
                ret["WarningLevel"] = "EnableAllWarnings"

        ret["DisableSpecificWarnings"] = ""
        ret["AdditionalOptions"] = ""
        if "cpp.wrn-unused-parameter" in props:
            if props["cpp.wrn-unused-parameter"] == "true":
                # FIXME: MSVC has no proper option for this.
                ret["AdditionalOptions"] += "/w14100 "
            else:
                ret["DisableSpecificWarnings"] += "4100;"
            pass

        ret["DisableSpecificWarnings"] += "%(DisableSpecificWarnings)"
        ret["AdditionalOptions"] += "%(AdditionalOptions)"
        return ret

    def _generate_optimisation(self, props, cond):

        ret = []
        gen = self._generate_props(props)
        for p in gen:
            e = XMLTree.Element(p, Condition=cond)
            e.text = gen[p]
            ret.append(e)

        return ret

    def _write_custom_target(self, root, f, vcxProj, rawProjects, platforms, targets):
        inFile = os.path.join(f["dir"], f["name"])
        tmp = XMLTree.Element("CustomBuild", Include=inFile)
        for p in platforms:
            condString = "'$(Configuration)|$(Platform)'=='{0}'".format(p["project_target"])
            vcxFile = vcxProj["files"][f["fullpath"]]
            try:
                vf = vcxFile["configs"][p["config"]][p["platform"]]
                #output = os.path.join(vf["objdir"], vf["name"] + ".obj")
            except KeyError as e:
                tmp2 = XMLTree.Element("ExcludedFromBuild", Condition=condString)
                tmp2.text = "true"
                tmp.append(tmp2)
                continue

            tmp2 = XMLTree.Element("Command", Condition=condString)
            tmp2.text = " ".join(f for f in vf["command"])
            tmp.append(tmp2)

            tmp2 = XMLTree.Element("Outputs", Condition=condString)
            tmp2.text = vf["output"]
            tmp.append(tmp2)

            tmp2 = XMLTree.Element("ExcludedFromBuild", Condition=condString)
            tmp2.text = "false"
            tmp.append(tmp2)

            tmp2 = XMLTree.Element("LinkObjects", Condition=condString)
            tmp2.text = vf["link"]
            tmp.append(tmp2)

            tmp2 = XMLTree.Element("Message", Condition=condString)
            tmp2.text = "Building \"{0}\"".format(inFile)
            tmp.append(tmp2)

        root.append(tmp)

    def _globgen_sol_config(self):
        retLines = ["GlobalSection(SolutionConfigurationPlatforms) = preSolution"]
        tmpDict = {}

        for projName in self.m_VCXProjects:
            project = self.m_VCXProjects[projName]
            for cfg in project["configs"]:
                for plat in project["configs"][cfg]:
                    for _vcxPlat in self.m_WinPlatform:
                        if True in [fnmatch.fnmatch(plat, mPlat) for mPlat in self.m_WinPlatform[_vcxPlat]]:
                            #print projName, cfg, plat, _vcxPlat
                            uKey = "{0}-{1}".format(plat, cfg)

                            # There will never not be a match, so there's no point checking
                            tmpDict[uKey] = {"config":cfg, "platform":plat, "vcxPlat":_vcxPlat, "project":"{0}-{1}".format(plat, cfg),
                                             "project_target":"{0}-{1}|{2}".format(plat, cfg, _vcxPlat)}
                            line = "\t{0} = {0}".format(tmpDict[uKey]["project_target"])
                            if line not in retLines:
                                retLines += [line]

        return retLines + ["EndGlobalSection"], [tmpDict[k] for k in tmpDict]

    def _globgen_sol_prop(self):
        # Generates the "GlobalSection(SolutionProperties)" section
        return ["GlobalSelection(SolutionProperties) = preSolution", "\tHideSolutionNode = FALSE",
                "EndGlobalSection"]

    def _globgen_sol_proj(self, vcxPlats):
        # Generates the "GlobalSection(ProjectConfigurationPlatforms)" section
        retLines = ["GlobalSection(ProjectConfigurationPlatforms) = postSolution"]

        for projName in self.m_VCXProjects:
            retLines += [
                "\t{0}.{1}.ActiveCfg = {1}".format(self.m_VCXProjects[projName]["guid"], p["project_target"])
                for p in vcxPlats]
            retLines += [
                "\t{0}.{1}.Build.0 = {1}".format(self.m_VCXProjects[projName]["guid"], p["project_target"]) for
                p in vcxPlats]
        return retLines + ["EndGlobalSection"]

    def _projgen(self, solGUID):
        retLines = []

        for proj in self.m_VCXProjects:
            retLines += ["Project(\"{0}\") = \"{1}\", \"{2}\", \"{3}\"".format(
                solGUID, proj, self.m_VCXProjects[proj]["vcxPath"],
                self.m_VCXProjects[proj]["guid"])]
            retLines += self._projgen_deps(proj, self.m_VCXProjects)
            retLines += ["EndProject"]

        return retLines

    @staticmethod
    def _projgen_deps(proj, vcxProjects):

        retLines = ["\tProjectSection(ProjectDependencies) = postProject"]

        for dep in vcxProjects[proj]["vcxDeps"]:
            if dep["linktype"] != "local":
                continue

            retLines += ["\t\t{0} = {0}".format(vcxProjects[dep['name']]["guid"])]

        if len(retLines) == 1:
            return ""

        return retLines + ["\tEndProjectSection"]

    def _add_configurations(self, root, vcxProj, platforms):
        configGroup = XMLTree.Element("ItemGroup", Label="ProjectConfigurations")
        for p in platforms:
            #print p
            projectConfiguration = XMLTree.Element("ProjectConfiguration", Include=p["project_target"])
            configuration = XMLTree.Element("Configuration")
            configuration.text = p["project"]
            platform = XMLTree.Element("Platform")
            platform.text = p["vcxPlat"]
            projectConfiguration.append(configuration)
            projectConfiguration.append(platform)

            configGroup.append(projectConfiguration)

        root.append(configGroup)