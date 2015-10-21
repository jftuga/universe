
#include <stdio.h>
#include <stdlib.h>

char *
local_itoa(unsigned int num) {
	int mul=1;
	int digits=0;
	int loop;
	char *s;
	int current;
	
	// compute # of digits

	while( mul <= num ) {
		digits++;
		mul *= 10;
	}

	s = (char *) malloc( (digits * sizeof(char)) + 1 );

	mul /= 10;

	for(loop=0; loop < digits; loop++) {
		s[loop] = (char) (num / mul) + '0';
		current = num / mul;
		num -= (current * mul);
		mul /= 10;
	}

	s[loop] = '\0';

	return s;
}

int
main(int argc, char *argv[]) {

	unsigned int i;

	if( 2 != argc )
		return fprintf(stderr, "Give number on command line.\n\n");

	i = atoi( argv[1] );

	printf("itoa: %s\n", local_itoa(i) );

	return 0;
}

