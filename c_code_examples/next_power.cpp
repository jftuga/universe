
/* 
 * $Id: next_power.cpp,v 1.1 2001/06/08 05:22:41 john Exp $
 *
 * Solves this problem for x :
 *
 * ( 2 ^ x ) = argv[1]
 *
 * ouptut takes the floor of the answer and then adds 1
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int
main(int argc, char *argv[]) {
	
	if( argc != 2 )
		return fprintf(stderr,"\nGive number on commmand line.\n\n");

	unsigned int i = atoi( argv[1] );

	if( i <= 0 )
		return fprintf(stderr,"\nNumber must be greater than zero.\n\n");

	double log_two = log(2);
	double log_i = log( (double) i );

	double quotient = log_i / log_two;
	unsigned int answer = (unsigned int) quotient + 1;

	printf("%d\n", answer);

	return 0;
}
