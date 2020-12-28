import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class MyGridLayout(GridLayout):
    # initialize infinite keywords:
    def __init__(self, **kwargs):
        # Call grid layout constructor
        super(MyGridLayout, self).__init__(**kwargs)

        # Set columns
        self.cols = 1

        #create a second grid layout
        self.top_grid = GridLayout()
        self.top_grid.cols = 2

        # Add widgets
        self.top_grid.add_widget(Label(text="Name: "))
        # Add input box
        self.name = TextInput(multiline = False)
        self.top_grid.add_widget(self.name)
        
        # Add widgets
        self.top_grid.add_widget(Label(text="Pizza: "))
        # Add input box
        self.pizza = TextInput(multiline = False)
        self.top_grid.add_widget(self.pizza)
        
        # Add widgets
        self.top_grid.add_widget(Label(text="Drink: "))
        # Add input box
        self.drink = TextInput(multiline = False)
        self.top_grid.add_widget(self.drink)
        
        # Add top_grid to app
        self.add_widget(self.top_grid)

        # Create Submit button
        self.submitButt = Button(text="Submit")
        # Bind the button
        self.submitButt.bind(on_pres=self.press)
        self.add_widget(self.submitButt)

    def press(self, instance):
        name = self.name.text
        pizza = self.pizza.text
        drink = self.drink.text

        # print('Hello {}, you like {} and you drink {}'.format(name, pizza, drink))
        self.add_widget(Label(text='Hello {}, you like {} and you drink {}'.format(name, pizza, drink)))

        # Clear the input boxes
        self.name.text = ""
        self.pizza.text = ""
        self.drink.text = ""

class MyApp(App):
    def build(self):
        return MyGridLayout()

if __name__ == '__main__':
    MyApp().run()