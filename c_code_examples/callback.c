
/*
 * $Id: callback.c,v 1.1 2001/02/03 12:46:08 john Exp $
 *
 * Cool example of "callbacks" by Brian Hammond.
 */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef void(*MY_COOL_FUNCTION_TYPE)(int);

#define MAX_EVENT       3
#define EVENT_1         0
#define EVENT_2         1
#define EVENT_3         2

MY_COOL_FUNCTION_TYPE callbacks[MAX_EVENT]={NULL};

int addFunction(int type, MY_COOL_FUNCTION_TYPE func);

void limp1(int n) { printf("1 got type %d\n",n); }
void limp2(int n) { printf("2 got type %d\n",n); }
void limp3(int n) { printf("3 got type %d\n",n); }

int main () {
	int i;
	int type;

	addFunction(EVENT_1,limp1);
	addFunction(EVENT_2,limp2);
	addFunction(EVENT_3,limp3);
	
	srand( time(NULL) );

	for (i=0;i<10;i++) {
		printf("[%d]  ", i);
		type=rand()%MAX_EVENT;
	        if (callbacks[type]) callbacks[type](type+1);
	}

	return 0;
}

int addFunction(int type, MY_COOL_FUNCTION_TYPE func) {

	if( (type < 0) || (type > MAX_EVENT) )
		return 0;

	if( ! callbacks[type] )
		callbacks[type]=func;

	return 1;
}
