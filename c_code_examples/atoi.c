
#include <stdio.h>

int
local_atoi(char *s) {
	int loop;
	int total = 0;
	int current;
	int mul = 1;

	for(loop = strlen(s) - 1; loop > 0; loop--) {
		current = (int) s[loop] - '0';
		total += current * mul;
		mul *= 10;
	}

	if( '-' == s[loop] )
		total *= -1;
	else {
		current = (int) s[loop] - '0';
		total += current * mul;
	}

	return total;
}

int
main(int argc, char *argv[]) {

	if( 2 != argc )
		return fprintf(stderr, "Give number on command line.\n");

	printf("atoi : %d\n", local_atoi( argv[1] ) );

	return 0;
}
