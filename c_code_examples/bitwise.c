
/*
 * $Id: bitwise.c,v 1.1 2001/02/13 21:14:29 john Exp $
 *
 * Example of bitwise operators
 *
 * $Log: bitwise.c,v $
 * Revision 1.1  2001/02/13 21:14:29  john
 *
 *
 * Example of bitwise operators.
 *
 *
 */

#include<stdio.h>
#include<stdlib.h>

int
main(int argc, char *argv[]) {
	int loop = 0;
	unsigned char i;
	int BITS_PER_BYTE = 0;


	i = 0;
	i = ~i;

	while ( 1 ) {
		i = i << 1;
		
		if( ! i ) break;
		loop++;
	}

	BITS_PER_BYTE = ++loop;
	printf("\n\nbits ber byte = %d\n\n", BITS_PER_BYTE);

	i = 0;
	i = ~i;

	for(loop=0; loop < BITS_PER_BYTE; loop++) {
		printf("%d\n", i+1 );
		i = i >> 1;
	}
		

	return 0;
}
