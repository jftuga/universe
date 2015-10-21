
#include <stdio.h>

int
main(int argc, char *argv[]) {
	int x,y;
	x = y = 0;

	x = (y = 3, ++y + 1);
	x = (x >= y) ? ( y = ++y, x+y) : (x -= ++y, y+1);

	printf("x = %d\n", --y);
	printf("y = %d\n", x++);

	return 0;
}
