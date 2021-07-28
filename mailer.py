print("hello world")

f = open("/tmp/ex288.txt", "w")
f.write("Woops! I have deleted the content!")
f.close()
