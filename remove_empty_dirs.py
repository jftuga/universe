
# remove_empty_dirs.py
# -John Taylor
# Feb-4-2015

# recursively remove folders that do not contain any files

import os
REWT=r"Q:\000-OLD-FILES"
STUCK = []

def scan_and_remove():
    count=0
    for root, dirs, files in os.walk( REWT,topdown=False ):
        if not len(files) and not len(dirs):
            if root.find("DfsrPrivate") > 0:
                continue
            count += 1
            print(root)
            try:
                os.rmdir(root)
            except PermissionError as err:
                print(err)
                STUCK.append(root)

    return count
    
def main():
    cycles = 1
    count = 1
    total = 0

    while count:
        print()
        print("Scan cycle:", cycles)
        print("=" * 20)
        count = scan_and_remove()
        total += count
        print()
        if count:
            cycles += 1

    print()
    print("===")
    print("Total # of scan cycles:", cycles)
    print("Total # of directories removied:", total)
    print("===")
    if len(STUCK):
        print("Directories that could not be removed:")
        for d in STUCK:
            print("   ", d)
        print("===")
    print()

main()

