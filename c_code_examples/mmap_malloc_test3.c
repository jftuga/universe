
/*
 * Examples of:
 * malloc_stats(), ftruncate(), mmap(), munmap(), fork()
 * umask(), octal numbers, string reverse, fstat()
 *
 * This creates a mmap file from scratch, the file name and
 * file size are given on the command line.
 *
 * It also demonstrates how mmap'd files can be seen across
 * and manipulated by child processes.
 *
 * Compile with : gcc -Wall -pedantic mmap_malloc_test3.c -o mmap_malloc_test3 -lm
 *
 */
 
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <malloc.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <math.h>

#define DEFAULT 4

void
reverse(char *s) {
	int loop;
	int count = 0;
	char *rev;

	rev = (char *) malloc((strlen(s)+1) * sizeof(char));

	for(loop=strlen(s)-1; loop >= 0; loop--)
		rev[count++] = s[loop];

	rev[count] = '\0';

	strcpy(s,rev);
	free(rev);
}

int
Oct2Dec(char *s) {
	char *rev;
	int loop;
	int dec=0;
	int i;

	rev = (char *) malloc((strlen(s)+1) * sizeof(char));
	strcpy(rev,s);
	reverse(rev);

	for(loop=0; loop < strlen(rev); loop++) {
		i = (int) rev[loop] - '0';
		dec += i * pow(8,loop);
	}
	
	free(rev);
	return dec;
}

int main(int argc, char *argv[]) {

	char *ptr;
	int fp;
	char *v;
	int loop;
	struct stat *buf;
	int fsize;
	int child;
	mode_t um;

	if( argc != 3 ) {
		return fprintf(stderr, "\nUsage :\n%s <filename> <size in megs>\n\n",argv[0]);
	}

	fprintf(stderr, "\nbefore allocation:\n\n");
	malloc_stats();
	getchar();

	ptr = (char *) malloc(strlen(argv[1]) * sizeof(char) + 1);
	buf = (struct stat *) malloc(sizeof(struct stat));
	um = umask(0);
	if( (fp = open(argv[1], O_RDWR|O_CREAT, Oct2Dec("0600") )) < 0 ) {
		return fprintf(stderr, "\nUnable to open %s\n", argv[1]);
	}
	umask(um);

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

	/* /////////////////////////////////////////////////////////////// */

	child=fork();

	if (child < 0) {
		return fprintf(stderr, "\nUnable to fork.\n\n");
	}

	if (child == 0) { /* child process */
		for(loop=1; loop <  buf->st_size - 1; loop+=2) {
			v[loop] = 'z';
		}
	
		free(ptr);	
		munmap(v, buf->st_size);

		fprintf(stderr,"\nargv[1] length : %d\nfile size : %ld\n", strlen(argv[1]),buf->st_size);
		free(buf);

		fprintf(stderr, "\nafter free:\n\n");
		malloc_stats();
		getchar();

		return close(fp);
	} else {
		return 0;
	}
}

