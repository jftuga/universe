
/*
 * $Id: msgsnd.c,v 1.1 2001/02/04 19:49:08 john Exp $
 *
 * Example of System V IPC message queues.
 *
 * This programs creates a queue and sends the message given on the command line.
 * The msgrcv program will use the queue id to retreive the message.
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/ipc.h>
#include <sys/msg.h>

typedef struct ipcbuf {
	long mtype;
	char mtext[256];
} ipcbuf;

int main(int argc, char *argv[]) {
	int queue_id;
	struct ipcbuf message;
	int rc;

	if( argc != 2 )
		return fprintf(stderr,"\nGive message on command line.\n\n");

	if ((queue_id = msgget(IPC_PRIVATE, IPC_EXCL | 0660)) < 0) {
		perror("msgget");
		return 1;
	}
	
	printf("queue id : %d\n", queue_id);
	sleep(5);

	strcpy( message.mtext, argv[1] );
	message.mtype = 1973;

	rc = 0;
	rc = msgsnd( queue_id, &message, strlen(message.mtext)+1, 0 );

	return 0;
}
