
/*
 * demonstrates complex qsort()
 * does not exhibit hard-code limitations from nameage1.c
 * completely dynamic
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "nameage.h"

#define BUFFSIZE 4096

typedef struct person_type {
	char *name;
	unsigned int age;
} person_type;

int compareName (const void* a, const void* b) {
  return strcmp( (*(person_type**)a)->name, (*(person_type**)b)->name );
}

int compareAge (const void* a, const void* b) {
  return (*(person_type**)a)->age - (*(person_type**)b)->age;
}

int main(int argc, char *argv[]) {

	FILE *fp;
	char *line;
	char *ptr;
	struct person_type **person;
	unsigned int count=0;
	int loop;

	line = (char *) malloc( BUFFSIZE * sizeof(char) + 2);

	if( argc != 2 ) {
		return fprintf(stderr, "\nDid not have just one cmd-line argument.\n\n");
	}

	if( (fp=fopen(argv[1], "r")) == NULL ) {
		return fprintf(stderr, "\nUnable to open file: %s\n\n", argv[1]);
	}

	while( fgets(line, BUFFSIZE, fp) != NULL ) {
		ptr = strtok(line, " ");
		if( ! count ) {
			person = (person_type **) malloc( (count+1) * sizeof (person_type *));
		} else {
			person = realloc(person, (count+1) * sizeof (person_type *));
		}

		person[count] = (struct person_type *) malloc(sizeof(person_type));
		person[count]->name = (char *) malloc( ( strlen(ptr) + 1 ) * sizeof(char));
		strcpy(person[count]->name, ptr);
		ptr = strtok(NULL, "\n");
		person[count]->age = atoi(ptr);
		count++;
	}

	printf("\n\n");
	printf("Orginal list:\n\n");

	for(loop=0; loop < count; loop++) {
		printf("[%d] _%s_:%d\n", loop, person[loop]->name, person[loop]->age);
	}

	printf("\n\n");
	printf("Sorted by name:\n\n");

	qsort( person, count, sizeof(person_type *), compareName );

	for(loop=0; loop < count; loop++) {
		printf("_%s_:%d\n", person[loop]->name, person[loop]->age);
	}

	printf("\n\n");
	printf("Sorted by age:\n\n");

	qsort( person, count, sizeof(person_type *), compareAge );

	for(loop=0; loop < count; loop++) {
		printf("_%s_:%d\n", person[loop]->name, person[loop]->age);
	}

	printf("\n\n");
	printf("person_type      :  %d\n", sizeof(person_type));
	printf("person_type *    :  %d\n", sizeof(person_type *));
	printf("person_type **   :  %d\n", sizeof(person_type **));
	printf("\n\n");

	for( loop=0; loop < count; loop++) {
		printf("loop: %d %s\n", loop, person[loop]->name);
		free(person[loop]->name);
		free(person[loop]);
	}
	free(person);
	free(line);
	return fclose(fp);
}
	

