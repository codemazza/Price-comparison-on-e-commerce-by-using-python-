from tkinter import *
from bs4 import BeautifulSoup
import requests
from difflib import get_close_matches
import webbrowser
from collections import defaultdict
import random

# Initialize Tkinter root
root = Tk()
root.geometry("320x150")

class PriceCompare:
    def __init__(self, master):
        # Variables for product comparison
        self.var = StringVar()
        self.var_flipkart = StringVar()
        self.var_amzn = StringVar()

        # GUI elements
        label = Label(master, text='Enter the product')
        label.grid(row=0, column=0, padx=(30, 10), pady=30)

        entry = Entry(master, textvariable=self.var)
        entry.grid(row=0, column=1)

        button_find = Button(master, text='Find', bd=4, command=self.find)
        button_find.grid(row=1, column=1, sticky=W, pady=8)

    def find(self):
        self.product = self.var.get()
        self.product_arr = self.product.split()
        self.n = 1
        self.key = ""

        for word in self.product_arr:
            if self.n == 1:
                self.key = str(word)
                self.n += 1
            else:
                self.key = self.key + '+' + str(word)

        # Create a new window for price comparison results
        self.window = Toplevel(root)
        self.window.title('Price Comparison Engine')

        label_title_flip = Label(self.window, text='Flipkart Title:')
        label_title_flip.grid(row=0, column=0, sticky=W)

        label_flipkart = Label(self.window, text='Flipkart price (Rs):')
        label_flipkart.grid(row=1, column=0, sticky=W)

        entry_flipkart = Entry(self.window, textvariable=self.var_flipkart)
        entry_flipkart.grid(row=1, column=1, sticky=W)

        label_title_amzn = Label(self.window, text='Amazon Title:')
        label_title_amzn.grid(row=3, column=0, sticky=W)

        label_amzn = Label(self.window, text='Amazon price (Rs):')
        label_amzn.grid(row=4, column=0, sticky=W)

        entry_amzn = Entry(self.window, textvariable=self.var_amzn)
        entry_amzn.grid(row=4, column=1, sticky=W)

        # Fetch prices from Flipkart and Amazon
        self.price_flipkart(self.key)
        self.price_amzn(self.key)

        # Set the first match from Amazon and Flipkart if available
        try:
            self.var_amzn.set(self.matches_amzn[0])
        except IndexError:
            self.var_amzn.set('Product not available')

        try:
            self.var_flipkart.set(self.matches_flip[0])
        except IndexError:
            self.var_flipkart.set('Product not available')

    def price_flipkart(self, key):
        url_flip = f'https://www.flipkart.com/search?q={key}&marketplace=FLIPKART&otracker=start&as-show=on&as=off'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }
        source_code = requests.get(url_flip, headers=headers)
        soup = BeautifulSoup(source_code.text, "html.parser")
        map_flip = defaultdict(list)
        home = 'https://www.flipkart.com'

        for block in soup.find_all('div', {'class': '_2kHMtA'}):
            title = block.find('div', {'class': '_4rR01T'}).text
            price = block.find('div', {'class': '_30jeq3 _1_WHN1'}).text[1:]
            link = home + block.find('a', {'class': '_1fQZEK'}).get('href')
            map_flip[title] = [price, link]

        user_input = self.var.get().title()
        self.matches_flip = get_close_matches(user_input, map_flip.keys(), 20, 0.1)
        self.looktable_flip = {title: map_flip[title] for title in self.matches_flip}

        try:
            self.var_flipkart.set(self.looktable_flip[self.matches_flip[0]][0] + '.00')
        except IndexError:
            self.var_flipkart.set('Product not found')

    def price_amzn(self, key):
        url_amzn = f'https://www.amazon.in/s?k={key}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/51.0.2704.64 Safari/537.36'
        }
        source_code = requests.get(url_amzn, headers=headers)
        soup = BeautifulSoup(source_code.text, "html.parser")
        map_amzn = defaultdict(list)
        home = 'https://www.amazon.in'

        for html in soup.find_all('div', {'class': 'sg-col-inner'}):
            title = html.find('span', {'class': 'a-size-medium a-color-base a-text-normal'}).text
            price = html.find('span', {'class': 'a-price-whole'}).text
            link = home + html.find('a', {'class': 'a-link-normal s-no-outline'}).get('href')
            map_amzn[title] = [price, link]

        user_input = self.var.get().title()
        self.matches_amzn = get_close_matches(user_input, map_amzn.keys(), 20, 0.01)
        self.looktable_amzn = {title: map_amzn[title] for title in self.matches_amzn}

        try:
            self.var_amzn.set(self.looktable_amzn[self.matches_amzn[0]][0] + '.00')
        except IndexError:
            self.var_amzn.set('Product not found')

# Run the app
if __name__ == "__main__":
    app = PriceCompare(root)
    root.title('Price Comparison Engine')
    root.mainloop()
    