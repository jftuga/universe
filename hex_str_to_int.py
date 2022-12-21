"""
hex_str_to_int.py
-John Taylor
2022-12-21

convert a hexidecimal of any length in string format to its native integer value
this done by using left shift and OR
"""

# orginal hex input (without leading 0x)
uuid = "abcdefffff"

def main():
    total = 0
    count = len(uuid) // 2
    print(f"{count=}")
    shift = 8 * (len(uuid)-2)//2
    print(f"{shift=}")
    print()
    for i in range(0,len(uuid),2):
        print(f"{i=}")
        print(uuid[i:i+2])
        h = int(f"0x{uuid[i:i+2]}",16)
        print(f"    {h=}")
        print(f"{shift=}")
        val = h << shift
        print(f"  {val=}")
        total |= val
        print(f"{total=}")
        shift -= 8
        print("-"*20)

    # now compare 'total' to the originl input of 'uuid'
    orig = int(f"0x{uuid}",16)
    print(f" {orig=}")
    print(f" {type(uuid)=}")
    print(f"{type(total)=}")

if __name__ == "__main__":
    main()
