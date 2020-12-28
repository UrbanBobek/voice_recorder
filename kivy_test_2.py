import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_file('my.kv')

class MyGridLayout(Widget):
    name = ObjectProperty(None)
    pizza = ObjectProperty(None)
    drink = ObjectProperty(None)

    def press(self):
        name = self.name.text
        pizza = self.pizza.text
        drink = self.drink.text

        print('Hello {}, you like {} and you drink {}'.format(name, pizza, drink))
        # self.add_widget(Label(text='Hello {}, you like {} and you drink {}'.format(name, pizza, drink)))

        # Clear the input boxes
        self.name.text = ""
        self.pizza.text = ""
        self.drink.text = ""

class MyApp(App):
    def build(self):
        return MyGridLayout()

if __name__ == '__main__':
    MyApp().run()