complexapp_files = \
(
	{"name":"main.cpp", "type":"cpp", "configuration":"*", "platform":"*", "PROPS":{"wrn-unused-parameter":"false"}},
);

complexapp_deps = \
[
	{"name":"complexlib", "configuration":"*", "platform":"*", "search":"", "linktype":"local"},
];

def getProjectInfo():
	return {
		"name":			"complexapp",
		"outdir":		"bin/%CONFIGURATION%/%PLATFORM%",
		"outfile":		"%PROJECTNAME%%TARGETEXT%",
		"type":			"executable",
		"files":		complexapp_files,
		"INCLUDE_DIRS": [],
		"PROPS":		{},
		"CPPDEFS":		[],
		"CDEFS":		[],
		"CXXDEFS":		[],
		"deps":			complexapp_deps
		};

