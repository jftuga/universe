
/*
 * $Id: cookedload.c,v 1.1 2001/02/03 12:07:19 john Exp $
 *
 * Example of reading a binary file and importing it's data directly
 * into data structures.
 *
 * rawimport.c generates the data file, and this program reads it.
 */

#include <stdio.h>
#include <stdlib.h>
#include "structures.h"

int
main(int argc, char *argv[]) {
	FILE *fp;
	int total = 0;
	int loop;
	struct stock_data **stocklist;
	short c_len, s_len;

	if( argc != 2 )
		return fprintf(stderr, "\nGive file name to load on command line.\n\n");

	if( (fp=fopen(argv[1],"r")) == NULL )
		return fprintf(stderr, "\nUnable to open file %s for reading.\n\n", argv[1]);

	fread( &total, sizeof(int), 1, fp);
	printf("elements : %d\n\n", total);

	stocklist = (stock_data **) malloc( total * sizeof(stock_data *) );
	for(loop=0; loop < total; loop++) {
		stocklist[loop] = (stock_data *) malloc( sizeof(stock_data) );
		fread( &stocklist[loop]->value, sizeof(float), 1, fp);
		fread( &c_len, sizeof(short), 1, fp);
		fread( &s_len, sizeof(short), 1, fp);
		stocklist[loop]->company = (char *) malloc( (c_len+1) * sizeof(char));
		stocklist[loop]->symbol = (char *) malloc( (s_len+1) * sizeof(char));
		fread(stocklist[loop]->company, sizeof(char), c_len, fp);
		fread(stocklist[loop]->symbol, sizeof(char), s_len, fp);
	}
	
	fclose(fp);

	for(loop=0; loop < total; loop++)
		printf("%s [ %s ] is at $%4.2f\n", stocklist[loop]->company, stocklist[loop]->symbol, stocklist[loop]->value);
		
	printf("\n");
	return 0;
}
