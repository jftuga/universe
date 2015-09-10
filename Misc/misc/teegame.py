"""

This is a program to solve the golf-tee game that you find at the
Cracker Barrel

          a
         b b
        c c c
       d d d d
      e e e e e
"""

############################################################################

import sys
import random

############################################################################

LEGAL = {}
LEGAL[repr((0,0))] = ( (2,0), (2,2) )
LEGAL[repr((1,0))] = ( (3,0), (3,2) )
LEGAL[repr((1,1))] = ( (3,1), (3,3) )
LEGAL[repr((2,0))] = ( (0,0), (2,2), (4,0), (4,2) )
LEGAL[repr((2,1))] = ( (4,1), (4,3) )
LEGAL[repr((2,2))] = ( (0,0), (2,0), (4,2), (4,4) )
LEGAL[repr((3,0))] = ( (1,0), (3,2) )
LEGAL[repr((3,1))] = ( (1,1), (3,3) )
LEGAL[repr((3,2))] = ( (1,0), (3,0) )
LEGAL[repr((3,3))] = ( (1,1), (3,1) )
LEGAL[repr((4,0))] = ( (2,0), (4,2) )
LEGAL[repr((4,1))] = ( (2,1), (4,3) )
LEGAL[repr((4,2))] = ( (2,0), (2,2), (4,0), (4,4) )
LEGAL[repr((4,3))] = ( (2,1), (4,1) )
LEGAL[repr((4,4))] = ( (2,2), (4,2) )

############################################################################

def get_occupied():
	global OCCUPIED
	TOTAL = 0
	for row in MAP:
	  for col in row:
		 if 1 == col:
			TOTAL += 1

	global OCCUPIED
	OCCUPIED = TOTAL
	#print OCCUPIED
	return OCCUPIED

############################################################################

def find_holes():
	global MAP
	DEBUG = 0
	
	if 1 == DEBUG: print "find_holes()"

	hlist = []
	for row in range(0,len(MAP)):
		for col in range(0,len(MAP[row])):
			if 0 == MAP[row][col]:
				item = [row,col]
				if 1 == DEBUG: print "\t", row, "   ", col
				hlist.append(item)

	return hlist

		
############################################################################

def print_map():
	i = 12
	print
	print "-" * 77
	for row in MAP:
		w = len(row)
		print w-1, " " * i,
		for j in range(0,w):
			print row[j], " ",
		print 
		i -= 2
	print "-" * 77
	print

############################################################################

def look_for_moves_from(item):
	global LEGAL

	moves = []
	for item in LEGAL[ repr( tuple( item ) ) ]:
	  row = item[0]
	  col = item[1]
	  r = MAP[row]
	  c = r[col]
	  if 1 == c:
		 moves.append(item)
	return moves

############################################################################

def pick_a_move(mv):
	a = random.randint(0,len(mv)-1)
	return mv[a]

############################################################################

def pick_an_item(it):
	#print "it:", it
	a = random.randint(0,len(it)-1)
	#print "a:", a
	#print
	count = 0
	for k in it.keys():
		if count == a:
			return k
		else:
			count += 1

############################################################################
def exclude_items( item, mv ):
	global JUMP
	a = item[0]
	b = item[1]

	good = []
	#print "mv:", mv
	#print
	for m in mv:
		x = m[0]
		y = m[1]
		#print "\t  testing:", x,y, " to ",a,b

		if 2 == x - a:
			#print "\t\t 1) move up"
			if 2 == y - b:
				#print "\t\t a) move left"
				v = x - 1
				h = y - 1
			elif 2 == b - y:
				#print "\t\t b) move right"
				v = x - 1
				h = y + 1
			else:
				#print "\t\t c) move right"
				v = x - 1
				h = y 
		elif 2 == a - x:
			#print "\t\t 2) move down"
			if 2 == y - b:
				#print "\t\t a) move left"
				v = x + 1
				h = y - 1
			elif 2 == b - y:
				#print "\t\t b) move right"
				v = x + 1
				h = y + 1
			else:
				#print "\t\t c) move left"
				v = x + 1
				h = y
		elif x == a:
			#print "\t\t 3) move sideways"
			if 2 == y - b:
				#print "\t\t a) move left"
				v = x
				h = y - 1
			elif 2 == b - y:
				#print "\t\t b) move right"
				v = x
				h = y + 1
			else:
				print "\t\t c) move unknown"
				sys.exit(0)

		#print "=" * 19, v, h
		if 1 == MAP[v][h]:
			#print "=" * 19, "good"
			good.append(m)
			g = ( x, y, a, b )
			JUMP[repr(g)] = (v, h)
		#print

	return good

############################################################################

def search_for_moves():
	h = find_holes()
	move_list = {}
	print "holes occupied :", OCCUPIED
	for item in h:
		print
		print "looking for moves from hole : ",item[0],item[1]
		mv = look_for_moves_from(item)
		print "\t move from     : ",
		if len(mv) > 0:
			for m in mv:
				print m,
			print
		else:
			print "(NONE)"
			continue

 		good = exclude_items( item, mv )
		print "\t allowed moves : ", tuple(good)
		if 0 == len(good):
			continue

		#t = repr(tuple(item))
		t = tuple(item)
		move_list[t] = pick_a_move(good)
		print "\t move choosen  : ", move_list[t]

	#print "ml: ", move_list
	if 0 == len(move_list):
		print 
		print "No moves left"
		print
		return -1
	final_move = pick_an_item(move_list)
	#sys.exit(1)
	#t = repr(tuple(final_move))
	t = tuple(final_move)
	#print "f:", final_move
	#print "m:", move_list
	print
	print "executing move from", move_list[t], "to", t
	make_a_move( move_list[t], tuple(final_move) )


############################################################################

def make_a_move( src, dst ):
	global MAP, MOVE_HIST, JUMP

	s_row = src[0]
	s_col = src[1]
	d_row = dst[0]
	d_col = dst[1]

	if 0 != MAP[d_row][d_col]:
		print "make_a_move(): trying to move TO an occupied position!"
		print
		sys.exit(1)
	if 1 != MAP[s_row][s_col]:
		print "make_a_move(): trying to move FROM an unoccupied position"
		print
		sys.exit(1)

	MAP[d_row][d_col] = 1
	MAP[s_row][s_col] = 0

	item = ( src, dst )
	MOVE_HIST.append(item)
	g = (s_row, s_col, d_row, d_col)
	j= JUMP[repr(g)]
	j_row = j[0]
	j_col = j[1]
	if 1 != MAP[j_row][j_col]:
		print "make_a_move(): the jump position was unoccupied"
		print
		sys.exit(1)
	MAP[j_row][j_col] = 0

############################################################################

def go():
	global OCCUPIED, MOVE_HIST

	get_occupied()
	while OCCUPIED > 1:
		print_map()
		rc = search_for_moves()
		if -1 == rc: break
		get_occupied()

	get_occupied()
	if OCCUPIED < 3:
		solution = 1
		print "+" * 77
		print
		print "Move order:"
		print "-----------"
		for m in MOVE_HIST:
			print "%2d) %s" % (solution,m)
			solution += 1
		print

	return OCCUPIED

############################################################################

def main():
	global MAP, OCCUPIED, MOVE_HIST, JUMP
	random.seed()


	total = 1
	rc = 15
	while rc > 1:
		print "[" + "=" * 77 + "]"
		print "new game:", total
		print "[" + "=" * 77 + "]"
		OCCUPIED=0
		MOVE_HIST = []
		JUMP = {}
		MAP = [ [ 1 ], [ 1, 1 ], [ 1, 1, 1 ], [ 1, 1, 1, 1 ], [ 1, 1, 0, 1, 1 ] ]
		
		rc = go()
		total += 1
		sys.stderr.write("game: %d, outcome: %d\n" % (total, OCCUPIED))

	print_map()

############################################################################

main()



