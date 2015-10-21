
#include <stdio.h>
#include <stdlib.h>

int
local_strlen(char *s) {
	int loop=0;

	while( s[loop] != '\0' ) loop++;

	return loop;
}
	

char *
local_strrev(char *s) {
	int loop, r;
	char *rev;

	rev = (char *) malloc( local_strlen(s) * sizeof(char) );
	if( ! rev ) {
		fprintf(stderr, "Unable to malloc() enough memory.\n\n");
		exit(1);
	}

	for(loop = strlen(s) - 1, r = 0; loop >= 0; loop--)
		rev[r++] = s[loop];

	rev[r] = '\0';

	for(loop = 0; loop < strlen(rev); loop++)
		s[loop] = rev[loop];

	free(rev);

	return s;
}

int
main(int argc, char *argv[]) {
	
	if( 2 != argc )
		return fprintf(stderr, "\nGive one command line argument.\n\n");

	printf("length  : %d\n", local_strlen(argv[1]) );
	printf("reverse : %s\n", local_strrev(argv[1]) );

	return 0;
}

