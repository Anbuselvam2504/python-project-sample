def my_func():
    print("Heloo, Sir Welcome ")
my_func()
def my_func2():
    print()
def my_func3():
    print("This is my function 3")

def my_func4():
    pass

def my_func5():
    return "This is my function 5"


my_func2()
my_func3()
my_func4()     
print(my_func5())

def limit(name):
    print("Hello, " + name +":Today, you crossed your limit")

limit("Anbu")

def renew(working_hours=8 ,name ="Anbu",age=25):
    return "Hello, " + name +":Today, you worked for " + str(working_hours) + " hours and \nYou can try after " + str(24 - working_hours) + " hours and your age is " + str(age) +"\nPlease take rest and drink water"

print(renew(age=30,name="Hari",working_hours=9))
print(renew(name="Anbu",working_hours=9,age=25))
print(renew(9, "Anbu", 29))
print(renew(12,name="Tarun",age=22))
print()
name="Anbu"
def my_func6(name):
    for letter in name:
        print (letter)

my_func6(name)

print()

def my_func7(a,b,/,*,c,d):
    return a+b+c+d
print(my_func7(1,2,d=3,c=4))

print()

def my_child(*kids):
    print("My youngest kid is: " + kids[0])
    print()
    for kid in kids:
        print(kid)

my_child("Anbu","Hari","Tarun","Arun")


# Lamda function 
x = lambda a : a + 10
print(x(5))

print((lambda a,b : a*b)(2,3))
def my_lambda(n):
    return lambda a : a * n
my_doubler = my_lambda(2)
print(my_doubler(11))

#lambda function with map()
numbers= [1,2,3,4,5]
doubled_numbers = list(map(lambda x : x*2, numbers))
print(doubled_numbers)

#lambda function with filter()
numbers = range(10)
odd_num=list(filter(lambda x: x% 2 != 0, numbers ))
print(odd_num)
print()
#lambda function with sorted()
stud=[("Anbu", 25), ("Hari", 30), ("Tarun", 22)] 
sorted_stud = sorted(stud, key=lambda x: x[1])
print(sorted_stud)

print()

#python Recursion
def count_down(n):
   if n<=-1:
       print("Done!")
   else:
       print(n)
       if n==20: print("you are almost finished")
       count_down(n-2)

count_down(10)
print()
def fact(n):
    if n==0 or n==1:
        return 1
    else:
        return n * fact(n-1)
    
print(fact(5))
print()
def fibonacci(n):
    if n<=1:
        return n
    else:
        return fibonacci(n-1) + fibonacci (n-2)
    
print(fibonacci(10))
print(fibonacci(4))
print(fibonacci(3))

# recursion with list
def sum_list(numbers):
    if len(numbers)== 0:
        return 0
    else:
        return numbers[0] + sum_list(numbers[1:])
my_list=[1,3,5,7,9]
print(sum_list(my_list))

import sys
x=sys.getrecursionlimit() # we also set recursion limit using sys.setrecursionlimit()
print(x)


# python Generator
def my_generator():
    yield 1
    yield 2
    yield 3
for value in my_generator():
    print(value)

print()

def count_upto(n):
    count =1
    while count<=n:
        yield count
        count +=1
for num in count_upto(5):
    print(num)

# use  next() to get the next value from the generator manually

def gen_manual():
    yield "Anbu"
    yield"Hari"
    yield"Tarun"
gen=gen_manual()
print(next(gen))
print(next(gen))
print(next(gen))
#print(next(gen)) # this will raise StopIteration error because there are no more values to yield

print()

# use send() to send a value to the generator
def gen_send():
    while True:
        value = yield
        print("Received:", value)
gen=gen_send()
next(gen) # start the generator
gen.send("Hello")
gen.send("World")
gen.send("Python")

print()
# close the generator using close()
def gen_close():
    try:
        while True:
            yield "Anbu"
            yield "Hari"
            yield "Tarun"
    except GeneratorExit:
        print("Generator closed")
gen=gen_close()
print(next(gen))   
print(next(gen))
print(next(gen))
gen.close() # this will raise GeneratorExit exception and print "Generator closed"
