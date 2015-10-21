
/*
 * Example of 100% dynamic memory allocation.
 * Also, note the the "loop" variable has to be signed
 */

#include<stdio.h>
#include<stdlib.h>
#include<string.h>

#define BUFFSIZE 4096

int main(int argc, char *argv[]) {
	char **names;
	char *line;
	unsigned int count = 0;
	signed int loop;
	
	line = (char *) malloc(BUFFSIZE+1 * sizeof(char));

	while( ! feof(stdin) ) {
		scanf("%s\n", line);
		if( ! count ) {
			names = (char **) malloc( (count+1) * sizeof (char *));
		} else {
			names = realloc(names, (count+1) * sizeof (char *));
		}
		names[count] = (char *) malloc( (strlen(line)+1) * sizeof (char));
		strcpy(names[count], line);
		count++;

		// get rid of the age
		scanf("%s\n", line);
	}

	for(loop = count-1; loop >= 0; loop--) {
		printf("%s\n", names[loop]);
		free(names[loop]);
	}

	free(names);
	free(line);
	return 0;
}	
