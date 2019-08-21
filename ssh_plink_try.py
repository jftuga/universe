#!/usr/bin/env python3

# for more detailed information see: https://github.com/jftuga/universe/blob/master/tc_try.py

import itertools, os, os.path, sys, time
import concurrent.futures, random, numpy
import subprocess, shlex

pgm = 'c:\\Putty\\PLINK.EXE'
max_workers=4
fname_pwlist = 'C:\\ssh_plink_try\\pwlist'
pwlen = 4
cmd = '"%s" -batch -ssh 192.168.1.1 -l admin -pw _ help ' % (pgm)

checkpoint_groups = max_workers
checkpoint_fname = "plink.chkpt"
eureka = False
candidates = {}
attempts = 0

######################################################################################

def get_pw_from_candidates():
    global eureka, attempts

    eureka = False

    # single-threaded check
    for pw in candidates:
        attempts += 1
        rv = run_pgm(pw,True)
        if 2 == rv:
            break

######################################################################################

# all possible passwords are broken up into chunks of max_worker length
def guess_one_group(passwd_grp):
    with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
        alpha = { executor.submit(run_pgm, "".join(curr_pass)): curr_pass for curr_pass in passwd_grp }
        for future in concurrent.futures.as_completed(alpha):
            pass

######################################################################################

def run_pgm(curr_pass:str):
    global eureka, candidates, attempts
    
    if eureka:
        return

    # start of password specific settings
    # do not include these by default
    """
    # must start with
    if curr_pass[0] != 'a':
        return
    
    if len(curr_pass) < 7:
        return

    if len(curr_pass) > 15:
        return

    # xor: you want one or the other, but not both
    if "1234567" in curr_pass and "5678" in curr_pass:
        return

    # must be in there
    if "1" not in curr_pass:
        return

    # ends with
    if curr_pass[-1] == 'z':
        return

    # contains 2 or more instances of
    if curr_pass.count("1234") >= 2:
        return

    # you know this is not in there
    if "a2" in curr_pass:
        return

    # you know this is not in there
    if "b2" in curr_pass:
        return
    
    # you know this is not in there
    if "c2" in curr_pass:
        return
    """
    # end of password specific settings

    cmd_final = cmd.replace("_",curr_pass)
    args = shlex.split(cmd_final)
    print(args)

    attempts += 1
    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        #print("out:", proc.stdout.read())
        #print("err:", proc.stderr.read())
        err = proc.stderr.read().decode("utf-8")
        print("result %s:::%s" % (curr_pass,err))
        if "Access denied" not in err:
            eureka = True
            print()
            print("="*77)
            print()
            print("found password:", curr_pass)
            print("%d password attempts were made." % (attempts))
            print()
            print("="*77)
            return 2

    return 0

######################################################################################

def main():
    global eureka, attempts, pwlen

    start_time = time.localtime()
    end_time = False
    
    with open(fname_pwlist) as fp: pw_fragment_list = fp.read().splitlines()
    print("password fragments loaded from %s: %d" % (fname_pwlist, len(pw_fragment_list)) )
    if os.path.exists( checkpoint_fname ):
        with open(checkpoint_fname) as fp: checkpoint_list = fp.read().splitlines()
        last = checkpoint_list[-1]
        old_timestamp,old_pwlen,move_to_chk_num,old_attempts = last.split("\t")
        pwlen = int(old_pwlen)
        print("checkpoint file found, continuing from last checkpoint location of %s:%s\n" % (pwlen,move_to_chk_num))
        move_to_chk_num = int(move_to_chk_num) - 1
    else:
        move_to_chk_num = 0
        print()

    for curr_pwlen in range(pwlen,0,-1):
        print("="*20, "trying password of group length: %d" % (curr_pwlen))

        items = itertools.permutations(pw_fragment_list, curr_pwlen)
        passwd_list = numpy.array_split( list(items), checkpoint_groups)

        chk = 0
        for grp in passwd_list:
            if eureka:
                break
            if move_to_chk_num:
                chk += 1
                move_to_chk_num -= 1
                continue
            chk += 1
            
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print("[%s] group length: %s checkpoint: %s" % (now,curr_pwlen,chk))
            guess_one_group(grp)
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            with open(checkpoint_fname,mode="a") as fp: fp.write("%s\t%s\t%s\t%s\n" % (now,curr_pwlen,chk,attempts))

        if eureka:
            get_pw_from_candidates()
            end_time = time.localtime()
            break
    
    if not end_time:
        end_time = time.localtime()

    print()
    print("="*77)
    print()
    print( "start time: %s" % (time.strftime("%Y-%m-%d %H:%M:%S", start_time)))
    print( "end time  : %s" % (time.strftime("%Y-%m-%d %H:%M:%S", end_time)))
    print()
    if not eureka:
        print("Unable to guess the password :-(")
        print("%s passwords were attempted.\n" % (attempts))
        return 1


######################################################################################

if __name__ == "__main__":
    sys.exit(main())
    
            