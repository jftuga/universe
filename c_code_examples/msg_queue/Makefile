
CFLAGS=-ggdb -Wall -pedantic

all: msgsnd msgrcv

msgsnd: msgsnd.c

msgrcv: msgrcv.c

clean:
	rm -f msgsnd msgrcv
	ipcs -q | awk '$$1 ~ /0x/ {print $$2}' | xargs ipcrm msg > /dev/null

