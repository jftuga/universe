
/*
 * Example of how to use the bsearch(3) function
 * Only shows how to search for an int in an array of int's
 */

#include<stdio.h>
#include <stdlib.h>


int
SearchInt(const void *key, const void *current) {
	printf("%d : %d\n", *((int *) key), *((int *) current) );
	return *((int *) key) - *((int *) current);
}

int
main(int argc, char *argv[]) {
	int data[] = { 12 , 15 , 23 , 29 , 31 , 37 , 40 , 43 };
	int length = 8;
	int *ptr;
	int key;

	if(argc != 2 ) {
		return printf("\nGive number to search for on command line.\n");
	}

	key = atoi(argv[1]);

	ptr = bsearch(&key, data, length, sizeof(int), SearchInt);

	printf("\n");

	if(! ptr )
		return printf("Not found.\n");
	printf("%d\n", *ptr);
	
	return 0;
}

