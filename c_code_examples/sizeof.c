
/*
 * Shows the byte size of each primative data type.
 * Machine dependent
 */

#include<stdio.h>

int main()
{
	char a[1024];
	
	printf("\n");

	printf("a[1024]   : %d\n", sizeof(a)         );
	printf("'orange'  : %d\n", sizeof("orange")  );
	printf("\n");

	printf("void      : %d\n", sizeof(void)      );
	printf("char      : %d\n", sizeof(char)      );
	printf("short     : %d\n", sizeof(short)     );
	printf("int       : %d\n", sizeof(int)       );
	printf("long      : %d\n", sizeof(long)      );
	printf("long long : %d\n", sizeof(long long) );
	printf("float     : %d\n", sizeof(float)     );
	printf("double    : %d\n", sizeof(double)    );

	printf("\n");

	return 0;
}
