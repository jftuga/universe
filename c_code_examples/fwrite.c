
/*
 * fwrite(), shows how to write an array of floats to data files in 
 * a binary format
 *
 * Lots of values and data is hard-coded, but you get the idea.
 *
 * To run:
 * ./fwrite test.dat w    ( writes to test.dat )
 * ./fwrite test.dat r    ( reads from test.dat )
 */

#include <stdio.h>
#include <stdlib.h>

int
main(int argc, char *argv[]) {
	float data1[] = { 22.11, 33.22, 44.33, 55.44, 66.55, 77.66, 88.77, 99,88 };
	float data2[] = { 0, 0, 0, 0, 0, 0, 0, 0 };
	int length = 8;
	int loop;
	FILE *fp;
	int rc = 0;

	if( argc != 3 )
		return fprintf( stderr, "\nGive file name to write to on command line, then either r or w.\n\n");

	if( ! strcmp(argv[2], "w") ) {
		
		/* write array to file */

		if( (fp=fopen(argv[1], "w")) == NULL )
			return fprintf( stderr, "\nUnable to open file %s for writing.\n\n", argv[1]);

		rc = fwrite( data1, sizeof(float), length, fp);
		printf("return code : %d\n\n", rc);
		fclose(fp);
	} else if ( ! strcmp(argv[2], "r") ) {

		/* read array from file */

		if( (fp=fopen(argv[1], "r")) == NULL )
			return fprintf( stderr, "\nUnable to open file %s for reading.\n\n", argv[1]);

		rc = fread( data2, sizeof(float), length, fp);
		fclose(fp);

		printf("return code : %d\n\n", rc);

		printf("\n");
		for(loop=0; loop < length; loop++)
			printf("[ %d ]  %4.2f\n", loop, data2[loop]);
		printf("\n");

	} else {
		return fprintf( stderr, "\nUnknown command : %s\nUse either r or w for the command.\n", argv[2]);
	}

	return 0;
}
