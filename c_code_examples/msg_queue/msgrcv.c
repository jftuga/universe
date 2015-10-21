
/*
 * $Id: msgrcv.c,v 1.1 2001/02/04 19:49:08 john Exp $
 * 
 * Example of System V IPC message queues.
 *
 * This program retreive a message from a message queue create from the msgsnd
 * program.  You need to know the queue id.  This is printed out from the msgsnd
 * program, or you can use ipcs -q and look for it.
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/ipc.h>
#include <sys/msg.h>

#define BUFFSIZE 512

typedef struct ipcbuf {
	long mtype;
	char mtext[256];
} ipcbuf;

int main (int argc, char *argv[]) {
	int queue_id;
	int rc;
	struct ipcbuf message;

	if (argc != 2)
		return fprintf (stderr, "\nGive msg queue id on command line.\n\n");

	queue_id = atoi (argv[1]);

	rc = msgrcv (queue_id, &message, BUFFSIZE, 1973, 0);

	printf ("rc = %d\n\n", rc);
	printf ("mtype : %ld\n", message.mtype);

	if (message.mtext)
		printf ("message : %s\n", message.mtext);
	else
		printf ("message->mtext is NULL.\n");

	if( msgctl(queue_id,IPC_RMID,NULL) < 0 )
		fprintf(stderr, "Unable to remove message queue ( %d )\n", queue_id);

	return 0;
}
