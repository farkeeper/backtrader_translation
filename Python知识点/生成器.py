# 生成器其实是一个函数
# 这个函数体必须包含yield关键字,这个函数返回一个生成器对象generator
# 类似这样：
def myGenerator0():
    yield
# 官方解释是：边循环边计算，所以函数体内还得有循环
def myGenerator1():
    i = 0
    while i < 5:
        yield
        i += 1
# yield 相当于return，不同的是 先return再噎住。
# 函数执行到 yield 时，会先把yield当成return，之后，函数处于噎住、折断、暂停状态，等待被唤醒以继续执行后面的代码
# 一般用__next__()唤醒
# __next__()和next()不同的是 前者是生成器对象的实例方法，后者是python的内置方法，他们功能一样，只能对可迭代对象使用
# 当再次__next__()时，生成器这个函数会从yield完毕之后的那时那刻开始继续执行，直到再次执行yield时函数return，噎住。
def myGenerator2():
    i = 0
    while i < 5:
        yield i
        i += 1

def test():
    i = 0
    while i < 5:
        temp = yield i
        # yield = 先return 再 噎住，等待__next__()唤醒
        # 把i当做返回值返回，函数在此折断暂停执行，等待下一次__next__()时从这里开始执行
        print(temp)
        i += 1


if __name__ == "__main__":
    # 生成器是一个对象，需要一个变量名来接收并绑定
    f = myGenerator2()
    print(next(f))
    print(next(f))
    print(next(f))
    print("\n")

    # 函数也是对象，不绑定不行
    # 无法打印temp
    test()
    test()
    print(test())   # <generator object test at 0x00000173D77D8040>
    print(type(test()))     # <class 'generator'>
    print(test)  # <function test at 0x00000173D7A411C0>

    b = test()
    print(b)        # <generator object test at 0x000002A632078040>
    print(b)
    print(b)


    # 生成器需要一个变量名来接收并绑定
    a = test()

    # 第一次调用__next__()时，函数执行导yield时，先把yield当成return，故函数返回0，然后函数被暂停，等待唤醒
    # temp = yield i 语句是先右后左执行，执行完yield i时，函数已经return了，此时temp还未被赋值，所以temp为空
    print("第一次调用", a.__next__(), "\n")

    # 第二次调用__next__()时从yield i 执行完毕时开始执行，因为执行到赋值运算式的右边yield i时函数就return了，所以temp永远无法被赋值。
    # 继续执行后面的代码，因为i=0，再执行i=i+1 即 i=1，此时并未返回，所以while循环继续执行，直到执行到 yield i时，返回i即1
    print("第2次调用", a.__next__(), "\n")

    # 第三次调用__next__()时，i值已为1，又执行i+=1， 即i=2，再执行完毕yield i，返回值为i即2,
    print("第3次调用", a.__next__(), "\n")

    # 第四次调用__next__()时从yield i 执行完毕时开始执行，temp还是无法被赋实值。
    # 继续执行后面的代码，i=2，再执行i=i+1 即 i=3，此时并未返回，所以while循环继续执行，再执行到yield i，此时被return，故生成器返回值为3
    print("第4次调用", a.__next__(), "\n")

    # 第五次调用__next__()时，i值已为3，又执行完毕i+=1，即i=4，此时并未返回，所以while循环继续执行，再执行到yield i， 返回4,
    print("第5次调用", a.__next__(), "\n")
