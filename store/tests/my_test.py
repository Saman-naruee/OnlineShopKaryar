from django.test import TestCase  
from ..models import Promotion, Collection, Product, Customer, Order, OrderItem, Address, Cart, CartItem  

class PromotionModelTest(TestCase):  
    def test_string_representation(self):  
        promotion = Promotion(discount=10.0)  
        self.assertEqual(str(promotion), '10.0')  

class CollectionModelTest(TestCase):  
    def test_string_representation(self):  
        collection = Collection(title='Summer Collection')  
        self.assertEqual(str(collection), 'Summer Collection')  

class ProductModelTest(TestCase):  
    def setUp(self):  
        self.collection = Collection.objects.create(title='Summer Collection')  
        self.product = Product.objects.create(  
            title='T-Shirt',  
            slug='t-shirt',  
            unit_price=19.99,  
            inventory=100,  
            collection=self.collection  
        )  

    def test_string_representation(self):  
        self.assertEqual(str(self.product), 'T-Shirt')  

    def test_product_creation(self):  
        self.assertEqual(self.product.title, 'T-Shirt')  
        self.assertEqual(self.product.unit_price, 19.99)  
        self.assertEqual(self.product.inventory, 100)  
        self.assertEqual(self.product.collection, self.collection)  

class CustomerModelTest(TestCase):  
    def test_string_representation(self):  
        customer = Customer(first_name='John', last_name='Doe', email='john@example.com', phone='1234567890')  
        self.assertEqual(str(customer), 'Mr.Doe')  

class OrderModelTest(TestCase):  
    def setUp(self):  
        self.customer = Customer.objects.create(  
            first_name='John',  
            last_name='Doe',  
            email='john@example.com',  
            phone='1234567890'  
        )  
        self.order = Order.objects.create(customer=self.customer)  

    def test_string_representation(self):  
        self.assertEqual(str(self.order), f'{self.order.pk}.Order of {self.customer}')  

class OrderItemModelTest(TestCase):  
    def setUp(self):  
        self.customer = Customer.objects.create(  
            first_name='John',  
            last_name='Doe',  
            email='john@example.com',  
            phone='1234567890'  
        )  
        self.order = Order.objects.create(customer=self.customer)  
        self.collection = Collection.objects.create(title='Summer Collection')  
        self.product = Product.objects.create(  
            title='T-Shirt',  
            slug='t-shirt',  
            unit_price=19.99,  
            inventory=100,  
            collection=self.collection  
        )  
        self.order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=2, unit_price=19.99)  

    def test_order_item_creation(self):  
        self.assertEqual(self.order_item.order, self.order)  
        self.assertEqual(self.order_item.product, self.product)  
        self.assertEqual(self.order_item.quantity, 2)  

class AddressModelTest(TestCase):  
    def setUp(self):  
        self.customer = Customer.objects.create(  
            first_name='John',  
            last_name='Doe',  
            email='john@example.com',  
            phone='1234567890'  
        )  
        self.address = Address.objects.create(street='123 Main St', city='Anytown', customer=self.customer)  

    def test_string_representation(self):  
        self.assertEqual(str(self.address), f'{self.customer}: Anytown')  

class CartModelTest(TestCase):  
    def test_string_representation(self):  
        cart = Cart.objects.create()  
        self.assertEqual(str(cart), str(cart.created_at))  

class CartItemModelTest(TestCase):  
    def setUp(self):  
        self.cart = Cart.objects.create()  
        self.collection = Collection.objects.create(title='Summer Collection')  
        self.product = Product.objects.create(  
            title='T-Shirt',  
            slug='t-shirt',  
            unit_price=19.99,  
            inventory=100,  
            collection=self.collection  
        )  
        self.cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)  

    def test_cart_item_creation(self):  
        self.assertEqual(self.cart_item.cart, self.cart)  
        self.assertEqual(self.cart_item.product, self.product)  
        self.assertEqual(self.cart_item.quantity, 2)