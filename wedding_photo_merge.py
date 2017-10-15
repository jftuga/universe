#!/usr/bin/env python3

# wedding_photo_merge.py
# -John Taylor
# Oct-15-2017

# Merge photo files from 3 separate folders into one 'combined' folder

# merging order:
# 1) Bride
# 2) Groom
# 3) Bride
# 4) Groom
# 5) Together
# 6) Goto #1

# In dest_dir, files will be copied & :enamed to:
# image001.jpg, image002.png, image003.jpg, etc.

import os, os.path, shutil

bride_dir = r"C:\Dropbox\Bride"
groom_dir = r"C:\Dropbox\Groom"
together_dir = r"C:\Dropbox\Together"
dest_dir = r"C:\Dropbox\Dest"
new_img = 1

########################################################################################

def process_image(src_dir:str, fname:str):
    """ src_dir will either be: bride_dir, groom_dir, or together_dir
        fname is the photo file name in srd_dir
    """
    global new_img

    dbg = False

    if dbg: print(src_dir, new_img, fname)
    base, ext = os.path.splitext(fname)
    ext = ext.lower()
    if ".jpeg" == ext:
        ext = ".jpg"
    if ext != ".jpg" and ext != ".png" and ext != ".tif":
        print("skipping:", fname)
        return

    src_fname = "%s%s%s" % (src_dir, os.sep, fname)
    new_base = "image%03d" % (new_img)
    new_fname = "%s%s" % (new_base,ext)
    dest_fname = "%s%s%s" % (dest_dir,os.sep,new_fname)
    print("copy: '%s' => '%s'" % (src_fname, dest_fname))
    shutil.copyfile(src_fname,dest_fname)    
    new_img += 1

########################################################################################

def main():
    global new_img

    dbg = False 
    bride_pix = os.listdir(bride_dir)
    groom_pix = os.listdir(groom_dir)
    together_pix = os.listdir(together_dir)

    b = g = t = 0
    b_max = len(bride_pix)
    g_max = len(groom_pix)
    t_max = len(together_pix)
    bride_not_fin = groom_not_fin = together_not_fin = True

    while bride_not_fin or groom_not_fin or together_not_fin:
        if bride_not_fin and b < b_max:
            process_image(bride_dir, bride_pix[b])
            b += 1
        else:
            bride_not_fin = False
            if dbg: print("="*77, " bride done @ ", new_img)
            
        if groom_not_fin and g < g_max:
            process_image(groom_dir, groom_pix[g])
            g += 1
        else:
            groom_not_fin = False
            if dbg: print("="*77, " groom done @ ", new_img)

        if bride_not_fin and b < b_max:
            process_image(bride_dir, bride_pix[b])
            b += 1
        else:
            bride_not_fin = False
            if dbg: print("="*77, " bride done @ ", new_img)
            
        if groom_not_fin and g < g_max:
            process_image(groom_dir, groom_pix[g])
            g += 1
        else:
            groom_not_fin = False
            if dbg: print("="*77, " groom done @ ", new_img)

        if together_not_fin and t < t_max:
            process_image(together_dir, together_pix[t])
            t += 1
        else:
            together_not_fin = False
            if dbg: print("="*77, " together done @ ", new_img)

    if dbg: 
        print()
        print( bride_not_fin, groom_not_fin, together_not_fin)

########################################################################################

if "__main__" == __name__:
    main()
    
