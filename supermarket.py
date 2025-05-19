# -*- coding: utf-8 -*-

class DataBase:
    users = {} 
    id_user = 0
    goods = {}
    id_good = 0

    def check_username(self, name):
        
        for user_id, created_user in self.users.items():
            if created_user.name == name:
                return self.users[user_id]
        return False

    def create_new_user(self, data):
        
        self.users[self.id_user] = (User(name = data['name'], age = data['age'], email = data['email']))
        self.id_user += 1

    def delete_user(self, user_id):
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

    def create_good(self, data):
        self.goods[self.id_good] = Goods(name=data['name'], quantity=data['quantity'], price=data['price'])
        self.id_good += 1
        return self.id_good - 1  # Повертаємо ID створеного товару

    def delete_good(self, good_id):
        if good_id in self.goods:
            del self.goods[good_id]
            return True
        return False

    def get_goods_list(self):
        return self.goods


class User:
    def __init__(self, name='anon', age=25, email='fake@mail.com', money=0):
        self.name = name
        self.age = age
        self.email = email
        self.money = money
        self.cart = {}  # Кошик: {good_id: quantity}

    def change_data(self, name=None, age=None, email=None):
        if name is not None:
            self.name = name
        if age is not None:
            self.age = age
        if email is not None:
            self.email = email

    def put_money_on_wallet(self, sum):
        if sum > 0:
            self.money += sum
            return True
        return False

    def spend_money(self, sum):
        if sum > 0 and sum <= self.money:
            self.money -= sum
            return True
        return False

    def add_to_cart(self, good_id, quantity=1):
        if good_id in self.cart:
            self.cart[good_id] += quantity
        else:
            self.cart[good_id] = quantity

    def remove_from_cart(self, good_id, quantity=None):
        if good_id in self.cart:
            if quantity is None or quantity >= self.cart[good_id]:
                del self.cart[good_id]
            else:
                self.cart[good_id] -= quantity
            return True
        return False

    def clear_cart(self):
        self.cart = {}

    def get_cart_total(self, db):
        total = 0
        for good_id, quantity in self.cart.items():
            if good_id in db.goods:
                total += db.goods[good_id].price * quantity
        return total


class Goods:
    def __init__(self, name='unknown', quantity=0, price=0):
        self.name = name
        self.quantity = quantity
        self.price = price

    def change_data(self, name=None, quantity=None, price=None):
        if name is not None:
            self.name = name
        if quantity is not None:
            self.quantity = quantity
        if price is not None and price >= 0:
            self.price = price

    def increase_quantity(self, amount):
        if amount > 0:
            self.quantity += amount
            return True
        return False

    def decrease_quantity(self, amount):
        if amount > 0 and self.quantity >= amount:
            self.quantity -= amount
            return True
        return False


class Interface:
    user = None
    command_list_user = '''
    to log in: login
    to create account: create account
    to log out: logout
    to change account: change account
    to delete account: delete account
    to deposit money: deposit
    to view goods: view goods
    to buy goods: buy
    to add to cart: add to cart
    to remove from cart: remove from cart
    to view cart: view cart
    to checkout: checkout
    to exit: exit
    
    For admin:
    to create good: admin create good
    to delete good: admin delete good
    

    '''



    def __init__(self, database):
        self.db = database

    def _greeting(self):
        print('\nHello, user, please, sign in')
        print(self.command_list_user)

    def _login(self, name=''):
        if name == '':
            name = input('Please, enter name: ')
        result = self.db.check_username(name)
        if result:
            self.user = result
            print(f'Successfully logged in as {name}')
        else:
            print('No user found, please create account')

    def _create_account(self):
        data = {
            'name': input('Enter name: '),
            'age': int(input('Enter age: ')),
            'email': input('Enter email: ')
        }
        self.db.create_new_user(data)
        print('Account created successfully!')
        self._login(data['name'])

    def _change_account_data(self):
        print('Leave field empty to keep current value')
        name = input(f'New name [{self.user.name}]: ')
        age = input(f'New age [{self.user.age}]: ')
        email = input(f'New email [{self.user.email}]: ')

        self.user.change_data(
            name=name if name else None,
            age=int(age) if age else None,
            email=email if email else None
        )
        print('Account data updated successfully!')

    def _delete_account(self):
        confirm = input('Are you sure you want to delete your account? (yes/no): ')
        if confirm.lower() == 'yes':
            for user_id, user in self.db.users.items(): # Шукаємо ID користувача для видалення
                if user == self.user:
                    self.db.delete_user(user_id)
                    self.user = None
                    print('Account deleted successfully!')
                    return
            print('Error: account not found in database')

    def _deposit_money(self):
        try:
            amount = float(input('Enter amount to deposit: '))
            if amount > 0:
                self.user.put_money_on_wallet(amount)
                print(f'Successfully deposited {amount}. New balance: {self.user.money}')
            else:
                print('Amount must be positive')
        except ValueError:
            print('Invalid amount')




    def _view_goods(self):
        goods = self.db.get_goods_list()
        if not goods:
            print('No goods available')
            return

        print('\nAvailable goods:')
        for good_id, good in goods.items():
            print(f'ID:{good_id:3} |Name: {good.name[:15]:15} | Price:{good.price:6.2f} |Quantity:{good.quantity:8}')
            

    def _buy_goods(self):
        self._view_goods()
        try:
            good_id = int(input('Enter ID of good to buy: '))
            quantity = int(input('Enter quantity: '))
            
            if good_id not in self.db.goods:
                print('Invalid good ID')
                return
            
            good = self.db.goods[good_id]
            
            if quantity <= 0:
                print('Quantity must be positive')
                return
                
            if quantity > good.quantity:
                print('Not enough goods in stock')
                return
                
            total_price = good.price * quantity
            if total_price > self.user.money:
                print('Not enough money')
                return
                
            self.user.spend_money(total_price) # Виконуємо покупку
            good.decrease_quantity(quantity)
            print(f'Successfully bought {quantity} x {good.name} for {total_price:.2f}')
            
        except ValueError:
            print('Invalid input')

    def _add_to_cart(self):
        self._view_goods()
        try:
            good_id = int(input('Enter ID of good to add to cart: '))
            quantity = int(input('Enter quantity: '))
            
            if good_id not in self.db.goods:
                print('Invalid good ID')
                return
            
            if quantity <= 0:
                print('Quantity must be positive')
                return
                
            if quantity > self.db.goods[good_id].quantity:
                print('Not enough goods in stock')
                return
                
            self.user.add_to_cart(good_id, quantity)
            print(f'Added {quantity} x {self.db.goods[good_id].name} to cart')
            
        except ValueError:
            print('Invalid input')

    def _remove_from_cart(self):
        if not self.user.cart:
            print('Your cart is empty')
            return
            
        self._view_cart()
        try:
            good_id = int(input('Enter ID of good to remove from cart: '))
            
            if good_id not in self.user.cart:
                print('This good is not in your cart')
                return
                
            current_quantity = self.user.cart[good_id]
            quantity = input(f'Enter quantity to remove (current: {current_quantity}, press Enter to remove all): ')
            
            if quantity == '':
                self.user.remove_from_cart(good_id)
                print(f'Removed all {self.db.goods[good_id].name} from cart')
            else:
                quantity = int(quantity)
                if quantity <= 0:
                    print('Quantity must be positive')
                    return
                if quantity > current_quantity:
                    print(f'Cannot remove more than {current_quantity}')
                    return
                    
                self.user.remove_from_cart(good_id, quantity)
                print(f'Removed {quantity} x {self.db.goods[good_id].name} from cart')
                
        except ValueError:
            print('Invalid input')

    def _view_cart(self):
        if not self.user.cart:
            print('Your cart is empty')
            return
            
        print('\nYour cart:')
        
        total = 0
        for good_id, quantity in self.user.cart.items():
            if good_id in self.db.goods:
                good = self.db.goods[good_id]
                item_total = good.price * quantity
                total += item_total
                print(f'{good_id:3} | {good.name[:15]:15} | {good.price:6.2f} | {quantity:8} | {item_total:6.2f}')
            else:
                print(f'{good_id:3} | [Product not available]')
                
        print(f'\nCart total: {total:.2f}')
        print(f'Your balance: {self.user.money:.2f}')

    def _checkout(self):
        if not self.user.cart:
            print('Your cart is empty')
            return
            
        self._view_cart()
        total = self.user.get_cart_total(self.db)
        
        if total > self.user.money:
            print('Not enough money to checkout')
            return
            
        confirm = input('Proceed to checkout? (yes/no): ')
        if confirm.lower() != 'yes':
            return
            
        for good_id, quantity in self.user.cart.items():  # Перевіряємо, чи всі товари ще доступні
            if good_id not in self.db.goods or self.db.goods[good_id].quantity < quantity:
                print(f'Sorry, {self.db.goods[good_id].name if good_id in self.db.goods else "some items"} are no longer available in requested quantity')
                return
                
        for good_id, quantity in self.user.cart.items(): # Виконуємо покупку
            self.db.goods[good_id].decrease_quantity(quantity)
            
        self.user.spend_money(total)
        self.user.clear_cart()
        print(f'Successfully checked out! Total: {total:.2f}')
        print(f'Remaining balance: {self.user.money:.2f}')
        
    def _admin_create_good(self):
        if self.user is None or self.user.name != 'admin':
            print('Access denied')
            return
            
        data = {
            'name': input('Enter good name: '),
            'quantity': int(input('Enter quantity: ')),
            'price': float(input('Enter price: '))
        }
        good_id = self.db.create_good(data)
        print(f'Good created successfully with ID {good_id}')

    def _admin_delete_good(self):
        if self.user is None or self.user.name != 'admin':
            print('Access denied')
            return
            
        self._view_goods()
        try:
            good_id = int(input('Enter ID of good to delete: '))
            if self.db.delete_good(good_id):
                print('Good deleted successfully')
            else:
                print('Invalid good ID')
        except ValueError:
            print('Invalid input')

    def await_orders(self):
        work = True
        self._greeting()

        while work:
            command = input('\nEnter command: ').strip().lower()

            if command == 'exit':
                work = False    
            
            else:  
                if command == 'login':
                    self._login()    
                elif command == 'create account':
                    self._create_account()
                elif command == 'view goods':
                    self._view_goods()
                elif command == 'logout':
                    self.user = None
                    self._greeting()
                elif command == 'change account':
                    self._change_account_data()
                elif command == 'delete account':
                    self._delete_account()
                elif command == 'deposit':
                    self._deposit_money()
                elif command == 'view goods':
                    self._view_goods()
                elif command == 'buy':
                    self._buy_goods()
                elif command == 'add to cart':
                    self._add_to_cart()
                elif command == 'remove from cart':
                    self._remove_from_cart()
                elif command == 'view cart':
                    self._view_cart()
                elif command == 'checkout':
                    self._checkout()
                elif command == 'admin create good' and self.user.name == 'admin':
                    self._admin_create_good()
                elif command == 'admin delete good' and self.user.name == 'admin':
                    self._admin_delete_good()
                else:
                    print('Unknown command')
                    self._greeting()


db = DataBase()
interface = Interface(db)

# Додамо якогось користувача, якщо це перший запуск
if not db.users:
    db.create_new_user({'name': 'some user', 'age': 39, 'email': 'some_user@gmail.com'})
    some_user= db.users[0]
    some_user.put_money_on_wallet(10000)  

# Додамо декілька товарів для прикладу, якщо магазин порожній
if not db.goods:
    db.create_good({'name': 'Laptop', 'quantity': 10, 'price': 9909.99})
    db.create_good({'name': 'Smartphone', 'quantity': 20, 'price': 4499.49})
    db.create_good({'name': 'Headphones', 'quantity': 50, 'price': 709.59})

interface.await_orders()