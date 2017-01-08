#!/usr/bin/env python3

# duu.py
# Directory Usage Utility
# -John Taylor

# Display directory usage (in kilobytes)

import os, sys, locale, argparse, time, statistics, concurrent.futures
from os.path import join, getsize, isdir, splitext
from collections import defaultdict
from datetime import timedelta

pgm_version = "2.12"
pgm_date = "Jan-6-2017 20:35"

# keep trace of file/directory stats, extensions, and total number of directories processed
all_stats = {}
all_extensions = {}
all_dir_count = 0

#############################################################################

def safe_print(data:str,isError:bool=False) -> None:
    """Return a string suitable for output to the console

    Args:
        data: the input string, which may include Unicode characters

        isError: output to STDERR if true

    Returns:
        None
    """

    dest = sys.stdout if not isError else sys.stderr
    # can also use 'replace' instead of 'ignore' for errors= parameter
    print( str(data).encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding), file=dest )

#############################################################################


def fmt(n:float,precision:int=2,no_comma:bool=False) -> str:
    """Adds commas to a number and truncates it's precision
        Example: 112233.4455 into 112,233.45

    Args:
        n: the number to be converted

        precision: the number of decimal places to keep

        no_comma: add commas unless false

    Returns:
        The newly formatted number
    """

    tmp = "%." + "%s" % (precision) + "f"
    if no_comma:
        return int(n)
    return locale.format(tmp, n, grouping=True)

#############################################################################

def display_threaded_extensions() -> None:
    """Iterates through all_extensions to find the extension with the longest length: longest
        also combines all sublists of all_extensions into one large list: combined

    Returns:
        None
    """

    longest = ""
    longest_len = 0
    combined = defaultdict(int)
    for key in all_extensions:
        for val in all_extensions[key]:
            combined[val] += all_extensions[key][val]
            if len(val) > longest_len:
                longest = val
                longest_len = len(val)

    display_extentions(longest,combined)

    return len(combined)

#############################################################################

def display_extentions(longest_ext:str,extensions:dict) -> None:
    """Outputs number of occurrences for each file extension
        Sorted from highest count to lowest

    Args:
        longest_ext: the longest strlen extension, used to determine spacing

        extenstions: all file extensions, key=extension, val=number of occurrences

    Returns:
        None
    """
    print()
    print("file extensions")
    print("=" * 15)
    width = len(longest_ext)+2
    for e in sorted(extensions, key=extensions.get, reverse=True):
        spc = width - len(e)
        print("%s%s%s" % (e," "*spc,extensions[e]))

#############################################################################

def display_threaded_summary(unique_ext_count:int=0) -> (int, int):
    """Sums the counts for each entry in all_stats: file,error,directory,total_bytes
        (all_stats includes these stats for each individual directory)

    Args:
        unique_ext_count: total number of unique file extensions

    Returns:
        The total number of files seen, total number of directories seen
    """
    file_count = 0
    err_count = 0
    dir_count = 0
    total_bytes = 0
    stats_file_sizes = []

    for entry in all_stats.keys():
        file_count += all_stats[entry][0]
        err_count += all_stats[entry][1]
        dir_count += all_stats[entry][2]
        total_bytes += all_stats[entry][3]
        if all_stats[entry][4]:
            stats_file_sizes += all_stats[entry][5]

    stats = False if not len(stats_file_sizes) else True
    display_summary(file_count,err_count,dir_count,total_bytes,stats,stats_file_sizes,unique_ext_count)

    return file_count, dir_count

#############################################################################

def display_summary(file_count:int,err_count:int,dir_count:int,total_bytes:int,stats:bool,stats_file_sizes:list,unique_ext_count:int) -> None:
    """Outputs the total number of files, directories as well as file sizes

    Args:
        file_count, err_count, dir_count, total_bytes: total number of files, errors, directories, and bytes

        stats: true if -S cmd-line parameter is invoked

        stats_file_sizes: list of every file size

        unique_ext_count: count of unique file extensions

    Returns:
        None
    """
    print()
    print("summary")
    print("=" * 7)

    print("files         : %s" % ( fmt(file_count,0) ))
    print("directories   : %s" % ( fmt(dir_count,0) ))
    if err_count:
        percent = err_count / (err_count+file_count)
        print("read errors   : %s (%s%%)" % ( err_count, fmt(percent,2) ))

    print("bytes         : %s" % ( fmt(total_bytes,0) ))
    # comparison values are about 90.909% of kilo,mega,giga, and terabyte
    if total_bytes > 1126:
        print("kilobytes     : %s" % ( fmt(total_bytes / 1024.0 )))
    if total_bytes > 1153433:
        print("megabytes     : %s" % ( fmt(total_bytes / 1024 ** 2 )))
    if total_bytes > 1181116006:
        print("gigabytes     : %s" % ( fmt(total_bytes / 1024.0 ** 3)))
    if total_bytes > 1209462790144:
        print("terabytes     : %s" % ( fmt(total_bytes / 1024.0 ** 4)))
    if total_bytes > 1238489897107456:
        print("petabytes     : %s" % ( fmt(total_bytes / 1024.0 ** 5)))
    if unique_ext_count:
        print("unique extens : %s" % (fmt(unique_ext_count,0)))
    
    # if cmd-line includes -S
    if stats and len(stats_file_sizes):
        display_file_stats(stats_file_sizes)

#############################################################################

def convert_size(n:int) -> str:
    """Convert file size to human readable format

    Args:
        n: the number that needs to be converted

    Returns:
        string with unit size appended to end of number
        k=kilo, m=mega, g=giga, t=tera, p=peta
    """

    sizes = ( 0,1126,1153433,1181116006,1209462790144,1238489897107456 )
    unit  = ( "", "k", "m", "g", "t", "p" )
    
    val = None
    for i in range(0,len(sizes)-1):
        if n >= sizes[i] and n < sizes[i+1]:
            val = unit[i]
            if 0 == i:
                new_size = "%s" % (n)
            else:
                new_size = "%s%s" % (fmt(n / 1024.0 ** i,0),val)
    
    # for files larger than the last unit
    if None == val:
        val = unit[i+1]
        new_size = "%s%s" % (fmt(n / 1024.0 ** (i+1),0),val)

    return new_size

#############################################################################

def display_file_stats(stats_file_sizes:list) -> None:
    """Outputs mathematical statistics for all files
    
    Args:
        stats_file_sizes: list of every file size

    Returns:
        None
    """
    print()
    print("file statistics (in bytes)")
    print("=" * 26)

    try:
        mean = statistics.mean(stats_file_sizes)
    except:
        print("mean          : N/A")
    else:
        print("mean          : %s" % fmt(mean,0))

    try:
        median = statistics.median(stats_file_sizes)
    except:
        print("median        : N/A")
    else:
        print("median        : %s" % fmt(median,0))

    try:
        mode = statistics.mode(stats_file_sizes)
    except:
        print("mode          : N/A")
    else:
        print("mode          : %s" % fmt(mode,0))

    try:
        stdev = statistics.stdev(stats_file_sizes)
    except:
        print("stdev         : N/A")
    else:
        print("stdev         : %s" % fmt(stdev,0))

#############################################################################

def display_runtime_statistics(time_start:time.time, time_end:time.time, file_count:int, dir_count:int, threads:int) -> None:
    """Outputs information about how long the pgm ran for

    Args:
        time_start, time_end: starting and ending program times
        
        file_count, dir_count: total number of files and directories

        threads: number of threads used

    Returns:
        None
    """
    time_elapsed = timedelta( seconds= (time_end - time_start))
    fcount_per_sec = 0 if not file_count else file_count / (time_end - time_start)
    dcount_per_sec = 0 if dir_count < 2 else dir_count / (time_end - time_start)
    
    print("elapsed time  : %s" % (time_elapsed))
    print("files per sec : %s" % (fmt(fcount_per_sec)))
    print("dirs per sec  : %s" % (fmt(dcount_per_sec)))
    print("thread count  : %s" % (threads))

#############################################################################

def get_disk_threaded_usage(root_dir:str=".",ext:bool=False,verbose:bool=True,status:bool=False,skipdot:bool=False,stats:bool=False,bare:bool=False,norecurse:bool=False,verbose_files:bool=False,human:bool=False,max_workers:int=1) -> None:
    """Initiates the multithreading directory scans using up to max_worker number of threads
        Unless -N (norecurse), the scans recursively visit each directory in root_dir

    Args:
        root_dir: starting directory

        ext: true if cmd-line -e is invoked

        verbose: true if cmd-line -q is NOT invoked

        status: true if cmd-line -s is invoked

        skipdot: true if cmd-line -n is invoked

        stats: true if cmd-line -S is invoked

        bare: true if cmd-line -b is invoked

        norecurse: true if cmd-line -N is invoked

        verbose_files: true if cmd-line -f is invoked

        human: true if cmd-line -h is invoked

        max_workers: number of threads passed to cmd-line -T

    Returns:
        None
    """
    if norecurse:
        walker = os.walk(root_dir)
        first = next(walker)
        get_disk_usage(first,ext,verbose,status,skipdot,stats,bare,norecurse,verbose_files,1)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
            {executor.submit(get_disk_usage,walker,ext,verbose,status,skipdot,stats,bare,norecurse,verbose_files,human,max_workers): walker for walker in os.walk(root_dir)}

#############################################################################

def get_disk_usage(walker:tuple,ext:bool=False,verbose:bool=True,status:bool=False,skipdot:bool=False,stats:bool=False,bare:bool=False,norecurse:bool=False,verbose_files:bool=False,human:bool=False,max_workers:int=1) -> None:
    """Processes a single directory, compiling stats such a file count, file size, extensions, etc.
        This information is placed into: all_stats, all_extensions, all_dir_count

    Args:
        walker: a single tuple generated from os.walk()

        remaining args: see get_disk_threaded_usage()

    Returns:
        None
    """
    global all_stats, all_extensions, all_dir_count

    curr_exten_list = defaultdict(int)
    longest_ext = ""
    total = 0
    dir_total = 0
    file_count = 0
    dir_count = 0
    err_count = 0
    stats_file_sizes = []
    dot_dir = os.sep + "."

    root, dirs, files = walker

    if skipdot and dot_dir in root:
        # skip directories beginning with a '.'
        return
    dir_total = 0
    dir_count += 1
    all_dir_count += 1
    current = 0
    for name in files:
        if ext:
            tmp = os.path.splitext(name)[1][1:].lower()
            curr_exten_list[tmp] += 1
        fullname = join(root,name)
        try:
            current += getsize(fullname)
            if stats:
                stats_file_sizes.append(current)
            file_count += 1
        except:
            safe_print("Error: unable to read: %s" % fullname, isError=True)
            err_count += 1
    total += current
    dir_total += current
    
    if human:
        if verbose: safe_print("%s\t%s" % (convert_size(dir_total), root))
        elif verbose_files: safe_print("%s\t%s\t%s" % (convert_size(dir_total), convert_size(len(files)), root))
    else:
        # display directory size in kilobytes, when using 'bare' do not include commas
        if verbose: safe_print("%s\t%s" % (fmt(round(dir_total/1024.0,0),0,bare), root))
        elif verbose_files: safe_print("%s\t%s\t%s" % (fmt(round(dir_total/1024.0,0),0,bare), fmt(len(files),0), root))

    if status and not (all_dir_count % 100):
        print("Directories processed:", all_dir_count,file=sys.stderr)

    all_stats[walker[0]] = (file_count,err_count,dir_count,total,stats,stats_file_sizes)
    if ext:
        all_extensions[walker[0]] = curr_exten_list

######################################################################

def main() -> None:
    """Process command-line arguments, get directory usage, print results

    Returns:
        0 on success, 1 on error
    """
    parser = argparse.ArgumentParser(description="Display directory disk usage in kilobytes, plus totals", epilog="Directory Usage Utility, version: %s (%s)" % (pgm_version,pgm_date))
    parser.add_argument("dname", help="directory name", nargs="?", default=".")
    parser.add_argument("-b", "--bare", help="do not print summary or stats; useful for sorting when used exclusively", action="store_true")
    parser.add_argument("-e", "--ext", help="summarize file extensions", action="store_true")
    parser.add_argument("-q", "--quiet", help="don't display individual directories", action="store_true")
    parser.add_argument("-s", "--status", help="send processing status to STDERR", action="store_true")
    parser.add_argument("-n", "--nodot", help="skip directories starting with '.'", action="store_true")
    parser.add_argument("-N", "--norecurse", help="do not recurse", action="store_true")
    parser.add_argument("-f", "--files", help="also display number of files in each directory", action="store_true")
    parser.add_argument("-S", "--stats", help="display mean, median, mode and stdev file statistics", action="store_true")
    parser.add_argument("-H", "--human", help="display numbers in a more human readable format", action="store_true")
    parser.add_argument("-T", "--threads", help="number of concurrent threads, consider for SANs or NVMe, default: 1")
    args = parser.parse_args()

    verbose = False if args.quiet else True
    verbose = False if args.files else verbose
    max_workers = int(args.threads) if args.threads else 1
    if max_workers < 1 or max_workers > 64:
            max_workers = 1
    unique_ext_count = 0

    # make sure long numbers are appropriately separated with commas
    locale.setlocale(locale.LC_ALL, '')

    if isdir(args.dname):
        try:
            if args.stats:
                time_start = time.time()
            
            get_disk_threaded_usage(args.dname,args.ext,verbose,args.status,args.nodot,args.stats,args.bare,args.norecurse,args.files,args.human,max_workers)

            if args.ext:
                unique_ext_count = display_threaded_extensions()

            if not args.bare:
                fcount, dcount = display_threaded_summary(unique_ext_count)
                if args.stats:
                    time_end = time.time()
                    display_runtime_statistics(time_start,time_end,fcount,dcount,max_workers)

        except KeyboardInterrupt:
            safe_print("", isError=True)
            safe_print("", isError=True)
            safe_print("You pressed Ctrl+C", isError=True)
            safe_print("", isError=True)
            return 1
    else:
        safe_print("", isError=True)
        safe_print("Error: command-line parameter is not a directory: %s" % args.dname, isError=True)
        safe_print("", isError=True)
        return 1

    return 0

#############################################################################

if "__main__" == __name__:
    sys.exit( main() )

# end of script
