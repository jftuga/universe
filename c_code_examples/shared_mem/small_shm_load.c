
/*
 * Example of System V shared memory
 * shmget(), shmat(), shmdt()
 *
 * Use small_shm_get to view shared memory segment.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/shm.h>

#define BUFFER_SIZE 256 * 1048576

int
main(int argc, char *argv[]) {
	FILE *fp;
	FILE *msgfp;
	int shmid;
	size_t size;
	char *shm;
	char *message;

	if( argc != 3 )
		return fprintf(stderr, "\nUsage : \n%s <filename> <message>\n\n", argv[0]);

	if( (fp=fopen( argv[1], "w")) == NULL )
		return fprintf(stderr, "\nUnable to open file %s for writing.\n\n", argv[1]);

	if( (msgfp=fopen( argv[2], "r")) == NULL )
		return fprintf(stderr, "\nUnable to open file %s for reading.\n\n", argv[2]);



	message = (void *) malloc( BUFFER_SIZE * sizeof(char));
	size = fread( message, 1, BUFFER_SIZE, msgfp);
	printf("size: %d\n", size);
	fclose( msgfp );

	if( (shmid=shmget(IPC_PRIVATE, size, IPC_CREAT|SHM_R|SHM_W|SHM_RND|0777)) < 0 )
		perror("shmget");
	
	if( (shm=shmat(shmid, 0, SHM_R|SHM_W|SHM_RND)) == (void *) -1 )
		perror("shmat");
	
	printf("shmid = %d\n", shmid);
	fprintf(fp,"%d\n", shmid);
	fclose(fp);

	/* strncpy(shm, message, ( (strlen(message)+1) * sizeof(char) ) ); */
	memcpy( shm, message, size);
	free(message);

	if( shmdt( shm ) == -1 ) 
		perror("shmdt");
	
	return 0;
}
