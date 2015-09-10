
data = open("a",mode="r",encoding="ascii").read()
b = data.encode("utf=16")


fp = open("b",mode="w",encoding="utf-16")
fp.write(data)
fp.close()