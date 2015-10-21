
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <dirent.h>
#include <sys/types.h>
#include "zlib.h"

#define BUFFSIZE 65536
#define FILECOUNT 500000

extern int errno;

int
main(int argc, char *argv[]) {
	gzFile *fp;
	DIR *dp;
	char buffer[BUFFSIZE+1];
	int loop, bufflength,end;
	char *ptr, *start, *next;
	char tmp;
	int filecount;
	int dircount;
	struct dirent *ditem;
	char **list;

	list = (char **) malloc( sizeof(char *) * FILECOUNT);
	ditem = (struct dirent *) malloc( sizeof(struct dirent) );

	if ( 1 == argc )
		return fprintf(stderr,"\nGive directory name on command line.\n\n");

	if( NULL == (dp=opendir(argv[1])) )
		return fprintf(stderr,"\n%s: %s\n\n", argv[1], strerror(errno));

	dircount = 0;
	while( (ditem = readdir(dp)) ) {
		list[dircount] = (char *) malloc( sizeof(char) * (strlen(ditem->d_name)+strlen(argv[1])+1));
		if( ! strcmp(ditem->d_name, ".") ) continue;
		if( ! strcmp(ditem->d_name, "..") ) continue;
		strcpy(list[dircount], argv[1]);
		strcat(list[dircount], "/");
		strcat(list[dircount++], ditem->d_name);
	}
	closedir(dp);

	for(filecount=0; filecount < dircount; filecount++) {
		//printf("%s\n", list[filecount]);

		if( NULL == (fp=gzopen(list[filecount],"r")) )
			return fprintf(stderr,"\n%s: %s\n\n", argv[1], strerror(errno));

		/* skip article header */

		while( gzgets(fp, buffer, BUFFSIZE ) )
			if( ! strcmp(buffer,"\n") ) break;

		while( gzgets(fp, buffer, BUFFSIZE ) ) {
			loop=end=0;
			bufflength=strlen(buffer) - 1;
			buffer[bufflength] = '\0';
			next = &buffer[loop];

			while(1) {
				ptr = strstr(next,"://");
				if(!ptr) break;
		
				if(ptr) {
					/* scan backwards */
					//end=-1;
					end=0;
					for( ptr--; *ptr != ' '; ptr--) {
						tmp = tolower(*ptr);
						if( ('a' > tmp) || ('z' < tmp) ) {
							break;
						}
						if( ptr == &buffer[0] ) {
							ptr--;
							break;
						}
					}
					start = ++ptr;
					ptr++;
					/* scan forwards */
					for( ; *ptr != ' '; ptr++) {
						if( *ptr == '\n' ) {
							ptr--;
							end=-2;
							break;
						}
					}
					if( ('>' == *(ptr+end)) || (')' == *(ptr+end)) || (',' == *(ptr+end)) || ('.' == *(ptr+end)) ) {
						printf("fix --> ");
						ptr--;
					}
					tmp = *ptr;
					*ptr = '\0';
					if( strcmp(start,"http://www.deja.com/") && strcmp(start,"http://www.remarq.com") && strcmp(start,"http://www.newsfeeds.com") )
						printf("%s\n", start);
					*ptr = tmp;
				}
				next = ptr+1;
				if( next >= &buffer[bufflength] ) break;
				if( ! next ) break;
			} /* while */
		}

		gzclose(fp);
		if( !(filecount%3000) )
			fprintf(stderr, "%d...\n", dircount-filecount);
	} /* for */
	
	return 0;
}


