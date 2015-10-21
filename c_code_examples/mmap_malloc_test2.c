
/*
 * Examples of:
 * malloc_stats(), ftruncate(), mmap(), munmap()
 *
 * This creates a mmap file from scratch, the file name and
 * file size are given on the command line.
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/mman.h>
#include <malloc.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#define DEFAULT 4

int main(int argc, char *argv[]) {

	char *ptr;
	int fp;
	char *v;
	int loop;
	struct stat *buf;
	int fsize;

	if( argc != 3 ) {
		return fprintf(stderr, "\nUsage :\n%s <filename> <size in megs>\n\n",argv[0]);
	}

	fprintf(stderr, "\nbefore allocation:\n\n");
	malloc_stats();
	getchar();

	ptr = (char *) malloc(strlen(argv[1]) * sizeof(char) + 1);
	buf = (struct stat *) malloc(sizeof(struct stat));
	if( (fp = open(argv[1], O_RDWR|O_CREAT)) < 0 ) {
		return fprintf(stderr, "\nUnable to open %s\n", argv[1]);
	}

	fsize = atol(argv[2]) * 1024 * 1024;
	if(! fsize ) fsize = DEFAULT * 1024 * 1024;
	
	if( ftruncate(fp, fsize ) < 0 ) {
		return fprintf(stderr, "\nUnable to ftruncate %s\n", argv[1]);
	}
	
	if( fstat(fp, buf ) < 0 ) {
		return fprintf(stderr, "\nUnable to fstat %s\n", argv[1]);
	}

	v = mmap(0, buf->st_size, PROT_READ|PROT_WRITE, MAP_SHARED, fp, 0 );

	if( (int) v < 0 ) {
		return fprintf(stderr, "\nmmap() failed.\n");
	}
	
	fprintf(stderr, "\n\nafter allocation:\n\n");
	malloc_stats();
	getchar();

	for(loop=0;loop < buf->st_size - 1; loop+=2) {
		v[loop] = 'X';
	}

	free(ptr);	
	munmap(v, buf->st_size);

	fprintf(stderr,"\nargv[1] length : %d\nfile size : %ld\n", strlen(argv[1]),buf->st_size);
	free(buf);

	fprintf(stderr, "\nafter free:\n\n");
	malloc_stats();
	getchar();

	return close(fp);
}

