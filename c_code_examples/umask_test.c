
/*
 * Creates 512 files with all possible umasks
 * Shows how to print a decimal in octal format
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

int main(int argc, char *argv[]) {
	int fp,loop;
	char fname[128];

	umask(0);

	for(loop=0; loop < 512; loop++) {
		sprintf(fname,"%#o", loop);
		printf("%s\n", fname);
		if( (fp = open(fname, O_RDWR|O_CREAT, loop )) < 0 )
			return fprintf(stderr, "\nUnable to open %s\n", fname);
		close(fp);
	}

	printf("\n");
	return 0;
}
