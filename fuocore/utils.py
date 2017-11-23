def elfhash(string):
    hash = 0
    x = 0
    for c in string:
        hash = (hash << 4) + c
        x = hash & 0xF0000000
        if x:
            hash ^= (x >> 24)
            hash &= ~x
    return (hash & 0x7FFFFFFF)


if __name__ == '__main__':
    import base64

    key = base64.b64encode('你好啊'.encode('utf-8'))
    print(key)
    print(key, elfhash(key))
