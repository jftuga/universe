
#include <stdio.h>

int main() {
	int i;
	for( i = 0; i < 255; printf("[%d] %c\n", i, (char) i++) );
	return 0;
}

