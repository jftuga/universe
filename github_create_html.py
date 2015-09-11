
# github_create_html.py
# -John Taylor
# Sept-11-2015

# Create an HTML file containing a table with filenames and descriptions
# Example: github_create_html.py > gh-manifest.html

import sys,configparser,os.path

fname_ini = "gh-__REPO__.ini"


##########################################################################

def header(repo_name=""):
	print("<html>")
	print("<title>Manifest</title>")
	print("<body>")
	print("<h2>%s - Manifest</h2>" %(repo_name))
	print("<hr noshade /><br />")
	print()
	print("<table border='1' cellpadding='3' cellspacing='3'>")
	print("<th>File</th>")
	print("<th>Description</th>")
	print()

##########################################################################

def footer(fcount):
	print("</table>")
	print("<br /><br />")
	print("file count: %s" % (fcount))
	print("<br /><br />")
	print("</body>")
	print("</html>")
	print()

##########################################################################

def url(fname):
	return "<a href='%s'>%s</a>" % (fname,fname)

##########################################################################

def table_add(fname, desc):
	print("<tr>")
	print("<td>%s</td>" % (url(fname)))
	print("<td>%s</td>" % (desc))
	print("</tr>")
	print()

##########################################################################

def main():
	global fname_ini

	if len(sys.argv) == 1:
		tmp1 = os.path.dirname(os.path.realpath(__file__))
		repo_name = tmp1.split(os.sep)[-1:][0]
		fname_ini = fname_ini.replace("__REPO__",repo_name)
		
	elif len(sys.argv) == 2:
		repo_name = sys.argv[1]
		fname_ini = fname_ini.replace("__REPO__",repo_name)
	else:
		print(); print("Usage: %s [ repo ]" % (sys.argv[0])); print()
		return 1

	#print(); print("ini file: %s" % (fname_ini)); print()

	config = configparser.ConfigParser()
	if os.path.exists(fname_ini):
		config.read(fname_ini)

	header(repo_name)
	count = 0
	for section in sorted(config.sections(), key=lambda s:s.lower()):
		if "desc" not in config[section]: continue
		table_add(section,config[section]["desc"])
		count += 1
	footer(count)


	return 0

##########################################################################

if "__main__" == __name__:
	sys.exit( main() )

