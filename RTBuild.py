#!/usr/bin/python

"""
 " Main RTBuild Program.
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
import fnmatch
import copy
import xml.etree.ElementTree as XMLTree


class RTBuild(object):
    """Initialise a new instance of RTBuild
    :param folder: The starting folder, relative to the execution directory.
    :param buildTargets: A list of all the supported targets. See examples for more information.
    :param exclDirs: A list of directories that are excluded from search, relative to the execution directory.
    """
    def __init__(self, folder, buildTargets, exclDirs=None, customTools=None, **properties):

        if exclDirs is None:
            exclDirs = []

        if customTools is None:
            customTools = []

        self.m_RawProjects = {}
        self.m_ProcessedProjects = {}
        self.m_BuildTargets = buildTargets
        self.m_CustomTools = {}

        for tool in customTools:
            self._register_custom_tool(tool)

        self._define_default_properties()
        self.m_GlobalProps = self._calculate_global_properties(**properties)


        self._traverse_folder(folder, [os.path.realpath(p) for p in exclDirs])
        self._preprocess_projects()

    def _register_custom_tool(self, tool):
        """
        Register a custom tool.
        :param tool: The custom tool to register.
        :raise Exception: If isinstance(type(tool), CustomTool) != true
            of if a duplicate tool is added.

        :type tool: CustomTool
        """
        if isinstance(type(tool), CustomTool):
            raise Exception("Invalid custom tool")

        name = tool.get_tool_name()

        if name in self.m_CustomTools:
            raise Exception("Duplicate tool with name {0}".format(name))

        self.m_CustomTools[name] = tool

    def _define_default_properties(self):
        """
        This should be pretty self-explanatory...
        :return:
        """
        defProps = {}
        props = {}
        # Define all the CPP properties
        props["cpp.optimise"]                = {"values": ['0', '1', '2', '3', 's'],     "default": '2'}
        props["cpp.werror"]                  = {"values": ["true", "false"],             "default": "false"}
        props["cpp.wall"]                    = {"values": ["true", "false"],             "default": "false"}
        props["cpp.lto"]                     = {"values": ["true", "false"],             "default": "false"}
        props["cpp.wrn-unused-parameter"]    = {"values": ["true", "false"],             "default": "true"}

        # Define all the C properties
        props["c.standard"]                  = {"values": ["C89", "C99", "C11"],         "default": "C99"}

        # Define all the CXX properties
        props["cxx.standard"]        = {"values": ["C++98", "C++03", "C++11", "C++14"],   "default": "C++03"}

        defProps["PROPS"]           = props
        defProps["INCLUDE_DIRS"]    = []
        defProps["CPPDEFS"]         = []
        defProps["CDEFS"]           = []
        defProps["CXXDEFS"]         = []
        defProps["STRIP_SYMBOLS"]   = "false"
        defProps["DEBUG"]           = "false"

        self.m_DefaultProperties = defProps

    def _validate_property(self, property, value):

        # Ignore unknown properties
        if property not in self.m_DefaultProperties["PROPS"]:
            #raise Exception("Invalid/Unknown property \"{0}\" in section {1}".format(property, section))
            return

        defProp = self.m_DefaultProperties["PROPS"][property]

        if type(defProp) == dict:
            if value not in defProp["values"]:
                raise Exception("Unknown value \"{0}\" for property \"{1}\"".format(value, property))
        elif type(defProp) == list:
            pass
        elif type(defProp) == str:
            pass
        else:
            raise Exception("Invalid property type, got {0}".format(type(defProp)))

    def _calculate_global_properties(self, **props):
        """
        Calculate the global properties.
        :param props: The user properties dictionary.
        :return: The global properties.
        """
        def union_prop_dict(name, d1, d2):
            """
            Union the user properties and default properties dictionaries, validating each value on the way.
            :param name: The name of the property group.
            :param d1: The users properties dictionary.
            :param d2: The default properties dictionary.
            :return: The validated union of the two.
            """

            outDict = {}

            # Do the union, this will ignore any unknown keys in d1
            for key in d2:
                # If the user hasn't given us a value, use the default.
                if key not in d1:
                    outDict[key] = d2[key]["default"]
                # If they have given us a value, validate it.
                elif d1[key] not in d2[key]["values"]:
                    raise Exception("Invalid or unknown value for \"{0}\" in property group {1}.".format(key, name))
                else:
                    outDict[key] = d1[key]
            return outDict

        globProps = {}
        for section in props:
            # Ignore any unknown properties
            if section not in self.m_DefaultProperties:
                continue

            user = props[section]
            default = self.m_DefaultProperties[section]

            # Make sure the user has given us the correct type
            if type(user) != type(default):
                raise Exception(
                    "Property type conflict for {0}. Expected {1}, got {2}.".format(section, type(default),
                                                                                             type(user)))

            if type(user) == dict:
                globProps[section] = union_prop_dict(section, user, self.m_DefaultProperties[section])
            elif type(user) == list:
                globProps[section] = copy.deepcopy(user)
            elif type(user) == str:
                globProps[section] = user
            else:
                raise Exception("Invalid property type {0}.".format(type(user)))

        return globProps

    @staticmethod
    def _ss_global_apply(string):
        # There's no global substitutions as of yet
        return string

    def _ss_project_apply(self, string, project, configuration, platform, exclude=None):
        """
        Apply project-level string substitutions.
        :param string: The string to process.
        :param project: The project.
        :return:
        """

        if exclude is None:
            exclude = []

        string = self._ss_global_apply(string)

        targetInfo = self.m_BuildTargets[configuration][platform]

        if "%INTDIR%" not in exclude:
            string = string.replace("%INTDIR%", project["intdir"])

        if "%CONFIGURATION%" not in exclude:
            string = string.replace("%CONFIGURATION%", configuration)

        if "%PLATFORM%" not in exclude:
            string = string.replace("%PLATFORM%", platform)

        if "%PROJECTNAME%" not in exclude:
            string = string.replace("%PROJECTNAME%", project["name"])


        if "%TARGETEXT%" not in exclude:
            if project["type"] == "static":
                string = string.replace("%TARGETEXT%", "%LIBEXT%")
            elif project["type"] == "module":
                string = string.replace("%TARGETEXT%", "%DLLEXT%")
            elif project["type"] == "executable":
                string = string.replace("%TARGETEXT%", "%EXEEXT%")

        if "%LIBEXT%" not in exclude:
            string = string.replace("%LIBEXT%", targetInfo["LIBEXT"])

        if "%DLLEXT%" not in exclude:
            string = string.replace("%DLLEXT%", targetInfo["DLLEXT"])

        if "%EXEEXT%" not in exclude:
            string = string.replace("%EXEEXT%", targetInfo["EXEEXT"])

        if "%OBJECT%" not in exclude:
            string = string.replace("%OBJEXT%", targetInfo["OBJEXT"])

        return string

    def _ss_file_apply(self, string, fEntry, project, configuration, platform, exclude=None):
        """
        Apply file-level string substitutions
        :param string:
        :param fEntry:
        :param project:
        :param configuration:
        :param platform:
        :return:
        """

        if exclude is None:
            exclude = []

        string = self._ss_project_apply(string, project, configuration, platform, ["%INTDIR%"] + exclude)

        # %INTDIR% relative to the solution root
        intdir = self._ss_project_apply("%INTDIR%", project, configuration, platform)

        # %INTDIR% is relative to the solution root, so make it relative to the project root
        intdir_local = os.path.relpath(intdir, project["projdir"])

        #print "Operating on {0}. %INTDIR% = {1}, localintdir = {2}".format(string, intdir, intdir_local)
        if "%INTDIR%" not in exclude:
            string = string.replace("%INTDIR%", intdir_local)

        targetInfo = self.m_BuildTargets[configuration][platform]


        # Remember %IN% should be relative to the project directory
        if "%IN%" not in exclude:
            string = string.replace("%IN%", fEntry["input"])

        if "%OUT%" not in exclude:
            string = string.replace("%OUT%", fEntry["output"])

        return string

    def _traverse_folder(self, folder, excl, top=None):
        """
        Traverse a folder structure, importing any buildfile.py files
        along the way.

        :param folder: The folder to search.
        :param excl: A list of directories to exclude
        :param top: The top directory, used for os.path.relpath()
        :raise Exception: If an error occurs.
        """

        def __isExcluded(child):
            for i in excl:
                if os.path.realpath(child).startswith(i):
                    return True
            return False

        if top == None:
            oldFlag = True
            top = os.getcwd()
        else:
            oldFlag = False

        os.chdir(folder)
        fileList = [f for f in os.listdir(".")]

        for f in fileList:
            if os.path.isdir(f):
                if not __isExcluded(f):
                    self._traverse_folder(f, excl, top)
            elif os.path.isfile(f) and f == "buildfile.py":
                try:
                    path = os.path.dirname(os.path.relpath(f, top))
                    # Add the project
                    project = RTBuild.__dynamic_import(os.path.realpath(f)).__dict__["getProjectInfo"]()
                    if project is not None:
                        self._add_project(project, path)

                    RTBuild.__delete_module("buildfile")
                except ImportError as e:
                    raise Exception("Unable to load \"{0}\": {1}.\n".format(f, str(e)))
                except KeyError as e:
                    raise Exception("Unable to load \"{0}\": Method {1} does not exist.\n".format(f, str(e)))

        os.chdir("..")

        if oldFlag:
            os.chdir(top)

    def _add_project(self, project, path):
        """
        Add a project
        :param project: The project to add.
        :param path: A string containing the path to the project, NOT including
        the trailing buildfile.py. Should be a directory.
        :raise Exception: If
        """
        if project["name"] in self.m_RawProjects:
            raise Exception("Duplicate project name {0}".format(project["name"]))

        p = self.m_RawProjects[project["name"]] = project
        p["projdir"] = path

    def _preprocess_projects(self):
        # Pass 1: Collate all the project information

        # For each configuration...
        for config in self.m_BuildTargets:
            target = self.m_BuildTargets[config]

            procConfig = self.m_ProcessedProjects[config] = {}

            # ...on each platform...
            for platform in target:
                procPlat = procConfig[platform] = {}
                currPlat = target[platform]
                # ...with each project...
                for project in self.m_RawProjects:
                    rawProject = self.m_RawProjects[project]
                    procProj = procPlat[project] = {"fullname": "{0}-{1}-{2}".format(platform, config, project)}

                    # These have to be done before the string substitutions
                    procProj["intdir"] = os.path.join("build", "{0}-{1}".format(platform, config), project)
                    procProj["name"] = project
                    procProj["projdir"] = rawProject["projdir"]
                    procProj["CDEFS"] = rawProject["CDEFS"]
                    procProj["CXXDEFS"] = rawProject["CXXDEFS"]
                    procProj["CPPDEFS"] = rawProject["CPPDEFS"]
                    procProj["type"] = rawProject["type"]

                    if procProj["type"] not in ["static", "module", "executable"]:
                        raise Exception("Invalid project type {0}".format(procProj["type"]))

                    procProj["outdir"] = self._ss_project_apply(rawProject["outdir"], procProj, config, platform)
                    procProj["outfile"] = self._ss_project_apply(rawProject["outfile"], procProj, config, platform)
                    procProj["outpath"] = os.path.join(procProj["outdir"], procProj["outfile"])

                    procProj["INCLUDE_DIRS"] = [self._ss_project_apply(i, procProj, config, platform) for i in rawProject["INCLUDE_DIRS"]]

                    for key in rawProject["PROPS"]:
                        self._validate_property(key, rawProject["PROPS"][key])

                    procProj["PROPS"] = rawProject["PROPS"]

                    procProj["makeDeps"] = [
                        {"name": i["name"],
                         "fullname": "{0}-{1}-{2}".format(platform, config, i["name"]),
                         "search": i["search"],
                         "linktype": i["linktype"],
                         "config": config,
                         "platform": platform} for i in rawProject["deps"] if
                        i["linktype"] == "local" and fnmatch.fnmatch(config, i["configuration"]) and fnmatch.fnmatch(
                            platform, i["platform"])]
                    procProj["linkDeps"] = [
                        {"name": i["name"],
                         "fullname": i["name"],
                         "linktype": i["linktype"],
                         "search": i["search"]} for
                        i in rawProject["deps"] if
                        i["linktype"] != "local" and fnmatch.fnmatch(config, i["configuration"]) and fnmatch.fnmatch(
                            platform, i["platform"])]

                    procProj["files"] = []
                    # ...and for each file...
                    for f in rawProject["files"]:
                        # Validate the file
                        if "name" not in f:
                            raise Exception("In project {0}: File without name.".format(project))
                        if "type" not in f:
                            raise Exception("In project {0}: File {1} without type.".format(project, f["name"]))
                        if f["type"] not in ["c", "cpp", "h", "hpp", "none"] and not f["type"].startswith("custom:"):
                            raise Exception("In project {0}: Invalid type {1} for {2}".format(project, f["type"], f["name"]))

                        # Process the file
                        fEntry = {"fullpath": os.path.relpath(os.path.join(procProj["projdir"], f["name"])), "type":f["type"][:]}
                        fileDir, fileName = os.path.split(f["name"])
                        fEntry["dir"] = fileDir
                        fEntry["name"] = fileName[:]
                        fEntry["input"] = f["name"]

                        # Validate the per-file properties
                        for key in f.get("PROPS", {}):
                            self._validate_property(key, f["PROPS"][key])

                        fEntry["PROPS"] = copy.deepcopy(f.get("PROPS", {}))

                        # If we're a header or a generic file, then add us regardless
                        if f["type"] in ["h", "hpp", "none"]:
                            fEntry["link"] = "false"
                            procProj["files"].append(fEntry)
                        # Otherwise, only add us if our conditions match
                        elif fnmatch.fnmatch(config, f["configuration"]) and fnmatch.fnmatch(platform, f["platform"]):
                            linkFlag = False
                            # Handle Custom Tools
                            if fEntry["type"].startswith("custom"):
                                tmp = fEntry["type"].split(":", 1)
                                if len(tmp) != 2:
                                    raise Exception("In project {0}: Custom file \"{1}\" without tool.".format(project, fEntry["fullpath"]))

                                try:
                                    custTool = self.m_CustomTools[tmp[1]]
                                except KeyError as e:
                                    raise Exception("In project {0}: Unknown custom tool \"{1}\"".format(project, tmp[1]))

                                def subProc(s):
                                    return RTBuild._ss_file_apply(self, s, fEntry, procProj, config, platform, exclude=[])

                                fEntry["output"] = RTBuild._ss_file_apply(self, f["output"], fEntry, procProj, config, platform, exclude=["%OUT%"])
                                fEntry["command"] = custTool.generate_build_command(fEntry, currPlat, self.m_GlobalProps, config, platform, subProc)

                                if f["link"] == "true":
                                    linkFlag = True
                            # Handle C/C++
                            elif fEntry["type"] in ["c", "cpp"]:
                                linkFlag = True
                                fEntry["defines"] = currPlat["CPPDEFS"] + procProj["CPPDEFS"]

                                if fEntry["type"] == "c":
                                    fEntry["defines"] += currPlat["CDEFS"] + procProj["CDEFS"]
                                elif fEntry["type"] == "cpp":
                                    fEntry["defines"] += currPlat["CXXDEFS"] + procProj["CXXDEFS"]
                                fEntry["objdir"] = os.path.join(procProj["intdir"], rawProject["projdir"], fileDir)
                            fEntry["link"] = {True:"true", False:"false"}[linkFlag]
                            procProj["files"].append(fEntry)

    def generate(self, generator):
        if isinstance(type(generator), BuildGenerator):
            raise Exception("Invalid generator")

        generator.generate(self.m_ProcessedProjects, self.m_BuildTargets, self.m_GlobalProps, self.m_CustomTools)

    def dump(self):
        RTBuild.niceprint(self.m_ProcessedProjects)

    @staticmethod
    def niceprint(x):
        if type(x) == XMLTree.Element:
            import xml.dom.minidom

            print xml.dom.minidom.parseString(XMLTree.tostring(x, 'utf-8')).toprettyxml(indent='\t')
        else:
            import pprint

            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(x)

    @staticmethod
    def __dynamic_import(path):
        sys.path.append(os.path.dirname(path))
        try:
            imp = __import__(os.path.basename(path)[0:-3])
        finally:
            del sys.path[-1]

        return imp

    @staticmethod
    def __delete_module(modname, paranoid=None):
        # Taken from https://mail.python.org/pipermail/tutor/2006-August/048596.html
        try:
            thismod = sys.modules[modname]
        except KeyError:
            raise ValueError(modname)
        these_symbols = dir(thismod)
        if paranoid:
            try:
                paranoid[:]  # sequence support
            except:
                raise ValueError('must supply a finite list for paranoid')
            else:
                these_symbols = paranoid[:]
        del sys.modules[modname]
        for mod in sys.modules.values():
            try:
                delattr(mod, modname)
            except AttributeError:
                pass
            if paranoid:
                for symbol in these_symbols:
                    if symbol[:2] == '__':  # ignore special symbols
                        continue
                    try:
                        delattr(mod, symbol)
                    except AttributeError:
                        pass


class CustomTool(object):
    """
    The interface for a custom tool.
    """

    def __init__(self):
        pass

    def generate_build_command(self, fEntry, target, globalProps, configuration, platform, subProc):
        """
        Generate a build command.
        :param fEntry: The file information.
        :param target: The target information.
        :param globalProps The global properties.
        :param configuration The current configuration.
        :param platform The current platform.
        :param subProc A callback to apply any substitutions. subProc(str)

        :type fEntry: dict
        :type target: dict
        :type configuration: str
        :type platform: str
        :type subProc: function

        :returns An list of the command elements, similar to C's argv.
        """

    def get_tool_name(self):
        """
        Get the name of the tool associated with this class.
        :raise Exception: If the base class version is called directly.
        """
        raise Exception("class CustomTool cannot be initialised")


class BuildGenerator(object):
    """
    The interface for a generator.
    """

    def __init__(self):
        self.m_Properties = self.m_CustomTools = self.m_Targets = self.m_Projects = None

    def generate(self, projects, targets, props, custTools):
        self.m_Projects = copy.deepcopy(projects)
        self.m_Targets = copy.deepcopy(targets)
        self.m_Properties = copy.deepcopy(props)
        self.m_CustomTools = copy.deepcopy(custTools)
