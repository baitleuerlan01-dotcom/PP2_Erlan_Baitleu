class Animal:
    def sound(self):
        print("Some sound")

class Dog(Animal):
    def sound(self):
        print("Woof!")

a = Animal()
d = Dog()

a.sound()   # Some sound
d.sound()   # Woof!
