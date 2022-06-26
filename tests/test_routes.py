"""
Order API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

  While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_service.py:TestOrderService
"""

import os
import logging
import random
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
from service.models import db, Order, init_db
from tests.factories import OrderFactory, ItemFactory
from service.utils import status  # HTTP Status Codes

BASE_URL = "/orders"

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  T E S T   C A S E S
######################################################################
class Test(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""
        pass

    def setUp(self):
        """Runs before each test"""
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()
        self.app = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################
    
    def _create_orders(self, count):
        """Factory method to create orders in bulk"""
        orders = []
        for _ in range(count):
            order = OrderFactory() 
            resp = self.app.post(BASE_URL, json=order.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Order",
            )
            new_order = resp.get_json()
            order.id = new_order["id"]
            orders.append(order)
        return orders

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b'Order REST API Service', resp.data)
    
    def test_get_order_list(self):
        """ Get a list of orders """
        self._create_orders(3)
        resp = self.app.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 3)
    
    def test_get_order_list_empty_list(self):
        """ Get a list of Orders when no orders present in database """
        resp = self.app.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_get_order_by_customer(self):
        """It should Get an Order by customer_id"""
        orders = self._create_orders(3)
        resp = self.app.get(BASE_URL, query_string=f"customer_id={orders[1].customer_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["customer_id"], orders[1].customer_id)

    def test_create_order(self):
        """It should Create a new Order"""
        order = OrderFactory()
        resp = self.app.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_order = resp.get_json()
        self.assertEqual(new_order["customer_id"], order.customer_id, "Customer Id does not match")
        self.assertEqual(new_order["tracking_id"], order.tracking_id, "Tracking Id does not match")
        self.assertEqual(new_order["status"], order.status.name, "Status does not match")
        self.assertEqual(len(new_order["order_items"]), len(order.order_items), "Items does not match")
        # Check that the location header was correct by getting it
        resp = self.app.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_order = resp.get_json()
        self.assertEqual(new_order["customer_id"], order.customer_id, "Customer Id does not match")
        self.assertEqual(new_order["tracking_id"], order.tracking_id, "Tracking Id does not match")
        self.assertEqual(new_order["status"], order.status.name, "Status does not match")
        self.assertEqual(new_order["order_items"], order.order_items, "Items does not match")

    def test_create_orders_wrong_content_type(self):
        """ Create an order with wrong content type """
        order = OrderFactory()
        resp = self.app.post('/orders',
                             json=order.serialize(),
                             content_type='application/xml')

        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_orders_customer_id_missing(self):
        """ Create an order missing customer_id """
        order = OrderFactory()
        order.customer_id = None
        resp = self.app.post('/orders',
                             json=order.serialize(),
                             content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_orders_customer_id_wrong_type(self):
        """ Create an order with invalid customer_id """
        order = OrderFactory()
        order.customer_id = "string"
        resp = self.app.post('/orders',
                             json=order.serialize(),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
