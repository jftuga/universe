
/*
 * Example of writing a binary file, which can later be read directly into
 * data structures 
 *
 * cookedload.c will read the data file
 *
 * Also, an example of sscanf() and fwrite()
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include "structures.h"

void
showlist(stock_data **sd, int total) {
	int loop;

	for(loop=0; loop < total; loop++ )
		printf("%s [ %s ] is at $%4.2f\n", sd[loop]->company, sd[loop]->symbol, sd[loop]->value);
}

int
writelist(stock_data **sd, int total, char *fname) {
	int loop;
	int rec_size = 0;
	short int c_len, s_len;
	FILE *fp;
	char buffer[BUFFSIZE+1];

	if( (fp = fopen(fname, "w")) == NULL )
		return fprintf(stderr, "Unable to open file %s for writing.\n", fname);

	fwrite( &total, sizeof(int), 1, fp);

	for(loop=0; loop < total; loop++ ) {
		c_len = strlen(sd[loop]->company);
		s_len = strlen(sd[loop]->symbol);

		rec_size = c_len + s_len;
		snprintf(buffer, ((rec_size+1) * sizeof(char)), "%s%s", sd[loop]->company, sd[loop]->symbol);

		fwrite( &sd[loop]->value, sizeof(float), 1 , fp);
		fwrite( &c_len, sizeof(short), 1, fp);
		fwrite( &s_len, sizeof(short), 1, fp);
		fwrite( &buffer, (rec_size * sizeof(char)), 1, fp);
	}

	fclose(fp);

	return 0;
}

int
main(int argc, char *argv[]) {
	FILE *fp;
	char buffer[BUFFSIZE+1];
	char *company, *symbol;
	float value;
	struct stock_data **stocklist = NULL;
	int count = 0;

	company = (char *) malloc( (BUFFSIZE+1) * sizeof(char) );
	symbol  = (char *) malloc( (BUFFSIZE+1) * sizeof(char) );

	if( argc != 2 )
		return fprintf(stderr,"\nGive raw data file name on command line.\n\n");

	if( (fp = fopen(argv[1], "r")) == NULL )
		 return fprintf(stderr,"\nUnable to open file %s for reading.\n\n", argv[1]);

	while( fgets(buffer, BUFFSIZE, fp) ) {
		sscanf(buffer,"%[^|] | %[^|] | %f", symbol, company, &value);
		if( ! count )
			stocklist = (stock_data **) malloc( (count+1) * sizeof(stock_data *) );
		else
			stocklist = realloc( stocklist, (count+1) * sizeof(stock_data *) );

		stocklist[count] = (stock_data *) malloc( sizeof(stock_data) );
		stocklist[count]->company = (char *) malloc( (strlen(company)+1) * sizeof(char));
		stocklist[count]->symbol = (char *) malloc( (strlen(symbol)+1) * sizeof(char));
		strcpy(stocklist[count]->company, company);
		strcpy(stocklist[count]->symbol, symbol);
		stocklist[count]->value = value;
		count++;
	}

	// showlist( stocklist, count);
	writelist( stocklist, count, "test.dat" );

	fclose(fp);

	return 0;
}
