
/*
 * Binary Search Algorithm
 * Items in list must be presorted.
 *
 * Give name to search for on command line.
 * Returns -1 when item is not found.
 */

#include <stdio.h>

int BinarySearch(char *list[], char *keyname, int length) {
	int low, high, test, found;
	low = 0;
	high = length - 1;

	found = -1;

	while ((found==-1) && (low <= high)){ //search loop
		test = (low + high) / 2;

		if( ! strcmp(list[test], keyname ) )
			return test;

		if( strcmp(list[test], keyname ) < 0 )
			low = test + 1;
		else
			high = test - 1;
	}

	return found;
}

int main(int argc, char *argv[] ) {
	char *list[] = { "Amit" , "Bob" , "Brian" , "Chris" , "Clate" , "Daniel" , "John" };
	int length = 7;
	int loop;

	if( argc != 2 ) return fprintf(stderr, "\nGive name to search for on command line.\n\n");

	for(loop=0; loop < length; loop++)
		printf("[%d] %s\n", loop, list[loop]);

	printf("\n");
	printf("Answer : %d\n\n", BinarySearch( list, argv[1], length));

	return 0;
}
		
