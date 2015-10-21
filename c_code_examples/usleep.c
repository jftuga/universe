
/*
 * Example of a very small sleep
 * 1 million microseconds = 1 second
 *
 * Running this program with an argument of 5200000 will make
 * it sleep for 5.2 seconds.
 */

#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h>

int main(int argc, char *argv[]) {
	if (argc!=2) return printf("\n\tusage:  usleep microseconds\n\n");
	usleep(atol(argv[1]));

	return 0;
}

