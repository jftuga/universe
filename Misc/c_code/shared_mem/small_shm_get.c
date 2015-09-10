
/*
 * Example of System V shared memory
 * shmget(), shmat(), shmdt()
 *
 * Use small_shm_load to load the shared memory segment (do this first)
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/ipc.h>
#include <sys/shm.h>

#define BUFFSIZE 1024

int
main(int argc, char *argv[]) {
	FILE *fp;
	int shmid;
	char *shm;
	char buffer[BUFFSIZE+1];
	struct shmid_ds shm_info;

	if( argc != 3 )
		return fprintf(stderr, "\nGive shared memory id *filename* then output-file as command-line arguments.\n\n");

	if( (fp=fopen(argv[1], "r")) == NULL )
		return fprintf(stderr, "Unable to open file %s for reading.\n\n", argv[1]);

	while( fgets(buffer, BUFFSIZE, fp) ) ;
	fclose(fp);

	shmid = atoi(buffer);
	/* printf("shmid : %d\n", shmid); */

	if ( ( shm=shmat(shmid, 0, SHM_R|SHM_RND)) == (void *)-1)
		perror("shmat");

	/* ******************************************************* */

	shmctl( shmid,IPC_STAT,&shm_info);
	if( (fp=fopen(argv[2], "w")) == NULL )
		return fprintf(stderr, "Unable to open file %s for writing.\n\n", argv[2]);
	fwrite(shm,1,shm_info.shm_segsz,fp);
	fclose(fp);

	/* if( shmctl(shmid,IPC_RMID,NULL) < 0 )
		perror("shmctl");

	return unlink( argv[1] ); */

	return 0;
}
