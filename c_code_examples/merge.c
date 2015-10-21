
/* msort.c - merge sort */
/* illustrates several important ideas, most notably merging
   and double buffering. */

#include <stdio.h>
#include <stdlib.h>

void merge(double[], int, double[], int, double[]);
void mergesort( double[], int);

void merge(double a[], int lengtha, double b[], int lengthb, double c[])
/* Arrays a and b are assumed to be sorted. They are merged into a
   single sorted array c, which had better be long enough... */
{
   /* Start at beginning of all 3 arrays*/
   int indexa = 0; int indexb = 0; int indexc = 0;
   /* Take smaller element until one of the two arrays is used up. */
   while( indexa < lengtha && indexb < lengthb)
   {
      c[indexc++] = (a[indexa] < b[indexb]) ? a[indexa++] : b[indexb++];
   }
   /* When we get here, either a[] or b[] has leftover elements (but
      not both of them). Just copy the leftover elements from whichever
      array. */
   while( indexa < lengtha)
      c[indexc++] = a[indexa++];
   while( indexb < lengthb)
      c[indexc++] = b[indexb++];
   /* Report for tutorial purposes. */
   printf("\nReport from merge routine :");
   for(indexc = 0; indexc < lengtha + lengthb; indexc++)
      printf("%10g%s", c[indexc], (indexc % 6) == 5 ? "\n" : " ");
   printf("\n");
}

void mergesort(double a[], int size)
/* The array to be sorted resides in the  array a[], which has length
   size. In this implementation, size must be less than 200. We can
   of course get rid of this restriction using pointers amd malloc. */
{
   double work[2][200];
   int fromrow, torow, mergesize, locator, i, kcopy;
   if(size > 200)
   {
      printf("Critical error: array size restricted to 200 max.\n");
      exit(0);
   }
   /* Copy array a into #0 row of work array. */
   for(i = 0; i < size; i++)
      work[0][i] = a[i];
   /* The overall process is : merge pairs of 1-element blocks, then
      2-element blocks, then 4-element blocks, ... until the mergesize
      is >= the size of the whole array. We use a double buffering
      technique to save copying. */
   fromrow = 0;
   torow = 1;
   mergesize = 1;
   /* Merge blocks of size 1, then size 2, then size 4,... */
   while(mergesize < size)
   {
      /* Do one pair of blocks at a time, so that the block locator
         changes by two blocks at a time. */
      for(locator = 0; locator < size; locator += mergesize*2)
      {
         /* The normal case is that we have two full blocks to merge. */
         if(locator + 2*mergesize - 1 < size)
            merge(&(work[fromrow][locator]), mergesize,
                  &(work[fromrow][locator+mergesize]), mergesize,
                  &(work[torow][locator]) );
         /* Next case - we are at the end of the array, and we have one
            full block and one partial block. */
         else if(locator + mergesize < size)
            merge(&(work[fromrow][locator]), mergesize,
                  &(work[fromrow][locator+mergesize]),
                  size - (locator + mergesize),
                  &(work[torow][locator]));
         /* Last case - there is only one block left, and it may
            not be full size. Just copy it. */
         else
            for(kcopy = locator; kcopy < size; kcopy++)
               work[torow][kcopy] = work[fromrow][kcopy];
      }
      /* Show progress in this tutorial program. */
      printf("\nMergesize = %d :\n", mergesize);
      for(i = 0; i < size; i++)
         printf("%10g%s",work[torow][i], (i % 6) == 5 ? "\n" : " ");
      printf("\n");
      /* Set up for next round - switch rows. */
      fromrow = 1 - fromrow;
      torow = 1 - torow;
      /* Double the size of the blocks that will be merged. */
      mergesize *= 2;
   }
   /* When sorted, copy the result back to a[]. */
   for(kcopy = 0; kcopy < size; kcopy++)
      a[kcopy] = work[fromrow][kcopy];
}

/* Test program. */
int main()
{
   double a[200];
   int size=0, i;
   while(scanf("%lf",&a[size]) == 1)
      size++;
   printf("Number read in = %d\n", size);
   for(i = 0; i < size; i++)
      printf("%10g%s", a[i], (i % 6) == 5 ? "\n" : " ");
   printf("\n");
   mergesort(a,size);
   printf("Sorted array:\n");
   for(i = 0; i < size; i++)
      printf("%10g%s", a[i], (i % 6) == 5 ? "\n" : " ");

   printf("\n");

   return 0;
}
