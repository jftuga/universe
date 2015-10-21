
/*
 * How to compute the value of PI
 *
 * compile with : gcc -Wall -pedantic -o pi pi.c -lm
 */

#include <stdio.h>
#include <math.h>

int main(void) {
	
	printf("%149.148f\n", 4.0 * atan(1.0));
	return 0;
}
