import sys,platform,sqlite3,os

def py_version_check():
        v = platform.python_version()[:3]
        if "3.2" != v and "3.3" != v and "3.4" != v and "3.5" != v:
                print("\n")
                print("Error #32701: You must run this program with Python 3.2 or newer")
                print("              You are currently running version: Python %s" % (platform.python_version()))
                print("\n")
                sys.exit()

def py_info():
        print()
        print("="*50)
        print("Oper Sys : %s %s" % (platform.system(), platform.release()))
        print("Platform : %s %s" % (platform.python_implementation(),platform.python_version()))
        print("SQLite   : %s" % (sqlite3.sqlite_version))
        print("Encoding : %s" % (sys.stdout.encoding))
        print("="*50)
        print()

if "__main__" == __name__:
        py_version_check()
        py_info()
