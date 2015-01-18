complexlib_files = \
(
	# C
	{"name":"foo.c", "type":"c", "configuration":"*", "platform":"*", "PROPS":{}},
	{"name":"plat_win.c", "type":"c", "configuration":"Windows", "platform":"*", "PROPS":{}},
	{"name":"plat_linux.c", "type":"c", "configuration":"Linux", "platform":"*", "PROPS":{}},
	{"name":"add.c", "type":"c", "configuration":"*", "platform":"*", "PROPS":{}},
	# x86-specific
	{"name":"arch/x86/asmadd_win.asm", "type":"custom:yasm", "configuration":"Windows", "platform":"x86-*",
	 "output":"%INTDIR%/%IN%%OBJEXT%", "add_output":[], "add_inputs":[], "link":"true"},
        {"name":"arch/x86/asmadd_lin.asm", "type":"custom:yasm", "configuration":"Linux", "platform":"x86-*",
         "output":"%INTDIR%/%IN%%OBJEXT%", "add_output":[], "add_inputs":[], "link":"true"},
	# x86_64-specific
	{"name":"arch/x86_64/asmadd.asm", "type":"custom:yasm", "configuration":"*", "platform":"x86_64-*",
	 "output":"%INTDIR%/%IN%%OBJEXT%", "add_output":[], "add_inputs":[], "link":"true"},

);

complexlib_deps = \
[
	{"name":"dl", "configuration":"Linux", "platform":"*", "search":"", "linktype":"dynamic"},
];

def getProjectInfo():
	return {
		"name":		"complexlib",
		"outdir":	"bin/%CONFIGURATION%/%PLATFORM%",
		"outfile":	"%PROJECTNAME%%TARGETEXT%",
		"type":		"module",
		"files":	complexlib_files,
		"PROPS":	{},
		"CPPDEFS":	["COMPLEXLIB_EXPORTS"],
		"CDEFS":	[],
		"CXXDEFS":	[],
		"deps":		complexlib_deps,
		}
