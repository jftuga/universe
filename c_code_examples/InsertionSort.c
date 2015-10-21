
/*
 * Example demonstrating the Insertion Sort Algorithm
 */

#include<stdio.h>

void InsertionSort(int *a, int length) {
	int i,j;
	int tmp;
	
	for( i=0; i < length; i++) {
		j = i;
		tmp = a[i];

		while ((j > 0) && (a[j-1] > tmp)) {
			a[j] = a[j-1];
			j--;
		}

		a[j] = tmp;
	}

	return;
}
	
int main(int argc, char *argv[]) {
	int a[] = { 25,19,45,12 };
	int length = 4;
	int loop;

	InsertionSort(a, length);

	for(loop=0; loop < length; loop++)
		printf("%d\n", a[loop]);

	return 0;
}
