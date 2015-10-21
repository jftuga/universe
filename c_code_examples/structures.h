
/*
 * $Id: structures.h,v 1.1 2001/02/03 12:07:19 john Exp $
 *
 * Data structures for cookedload & rawimport
 */

#ifndef _STRUCTURES_H_
#define _STRUCTURES_H_

typedef struct stock_data {
	char *company;
	char *symbol;
	float value;
	float change;
} stock_data;

#define BUFFSIZE 4096

#endif

