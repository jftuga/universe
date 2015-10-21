
/*
 * Displays all possible [decimal] octal pairs for umasks
 * String Reverse
 * Octal to Deicmal conversion of command line argument
 *
 * Compile with : gcc -Wall -pedantic octal.c -o octal -lm
 *
 */

#include<stdio.h>
#include<stdlib.h>
#include<math.h>

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

int
main(int argc, char *argv[]) {
	int loop;
	int dec;

	for(loop=0; loop < 512; loop++) {
		printf("[%d] %#o\n", loop, loop);
	}

	printf("\n\n");

	if( argc == 2 ) {
		dec = Oct2Dec(argv[1]);
		printf("%s octal = %d decimal\n\n", argv[1], dec);
	} else {
		printf("\nYou can give an octal number to be converted to decimal on the command line.\n\n");
	}

	return 0;
}
