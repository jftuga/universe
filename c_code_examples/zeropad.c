
/*
 * $Id: zeropad.c,v 1.1 2001/02/03 11:31:52 john Exp $
 *
 * Demostrates how to "pad" an integer with 0's
 */

#include <stdio.h>

int main() {
	int i = 5;

	printf("1234567890\n");
	printf("%02d\n", i);
	printf("%05d\n", i);

	return 0;
}

