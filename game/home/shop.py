import game.user as UserManager


shopList = {
     "item1" : {
         'name': 'item1',
         'price': 100000,
         'description': 'This is the first item in the shop'
     },
     "item2" : {
         'name': 'item2',
         'price': 200000,
         'description': 'This is the second item in the shop'
     }
}


class Shop:
    def __init__(self):
        self.user = UserManager.User()