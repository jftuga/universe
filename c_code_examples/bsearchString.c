
/*
 * Example of how to use the bsearch(3) function
 * Only shows how to search for a string in an array of strings
 */

#include <stdio.h>
#include <stdlib.h>


int SearchString(const void *key, const void *current) {
	printf("%s : %s\n", *((char **) key), *((char **) current) );
	return strcmp( *((char **) key) , *((char **) current) );
}

int
main(int argc, char *argv[]) {
	char *start[] = { "alpha", "beta", "delta", "epsilon", "gamma", "omega", "theta", "zeta" , NULL };
	char **data;
	int length,loop;
	char **ptr;

	if(argc != 2 ) {
		return printf("\nGive number to search for on command line.\n");
	}

	// find the length of start[]
	length=0;
	while( start[length] ) {
		//printf("[%d] %s\n", length, start[length] );
		length++;
	}

	data = (char **) malloc( length * sizeof(char *));
	for(loop=0; loop < length; loop++) {
		data[loop] = (char *) malloc( (strlen(start[loop])+1) * sizeof(char) );
		strcpy(data[loop], start[loop]);
	}

	ptr = bsearch(&argv[1], data, length, sizeof(char *), SearchString);

	printf("\n");

	if(! ptr )
		printf("Not found.\n");
	else
		printf("found : %s\n", *ptr);

	for(loop=0; loop < length; loop++)
		free(data[loop]);

	free(data);
	
	return 0;
}

