r"""
show_waiters_paginators.py
-John Taylor
2022-11-25

Output waiters and paginators for the given AWS service
"""

import boto3
import sys


def header(service: str):
    print()
    title = f"{service} waiters"
    print(title)
    print("=" * len(title))


def waiters(service: str, client):
    header(service)
    if not len(client.waiter_names):
        print("(None)")
    else:
        for name in client.waiter_names:
            print(name)


def paginators(service: str, client):
    header(service)
    all_api = [a for a in dir(client) if a[0] != "_" and a != "can_paginate"]
    has_paginator = False
    for api in all_api:
        try:
            if client.can_paginate(api):
                print(api)
                has_paginator = True
        except Exception:
            continue
    if not has_paginator:
        print("(None)")


def usage():
    print()
    print(f"Usage: {sys.argv[0]} [boto3 service name]")
    print(f"Example: {sys.argv[0]} s3")
    print(f"To see all available service names: {sys.argv[0]} -?")
    print()


def main():
    if len(sys.argv) != 2:
        usage()
        sys.exit(1)
    service = sys.argv[1]
    try:
        client = boto3.client(service)
    except Exception as e:
        print(f"{e}")
        sys.exit(1)
    waiters(service, client)
    paginators(service, client)
    print()


if __name__ == "__main__":
    main()
