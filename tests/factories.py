"""
Test Factory to make fake objects for testing
"""

import factory
import random
from factory.fuzzy import FuzzyChoice
from service.models import Order, Item, OrderStatus


class OrderFactory(factory.Factory):
    """Creates fake Orders"""

    class Meta:
        model = Order

    id = factory.Sequence(lambda n: n)
    customer_id = random.randint(0, 10000000)
    tracking_id = random.randint(0, 10000000)
    status = FuzzyChoice(OrderStatus)

    @factory.post_generation
    def order_items(self, create, extracted, **kwargs):
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.order_items = extracted


class ItemFactory(factory.Factory):
    """Creates fake Items"""
    class Meta:
        model = Item

    id = factory.Sequence(lambda n: n)
    order_id = None
    product_id = random.randint(0, 100000)
    quantity = random.randint(0, 100000)
    price = random.uniform(0, 100000)
    order = factory.SubFactory(OrderFactory)
