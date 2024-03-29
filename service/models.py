"""
Models for Order

All of the models are stored in this module
"""


import logging
from enum import Enum
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db(app):
    """ Initializes the SQLAlchemy app """
    Order.init_db(app)


class OrderStatus(Enum):
    """
        This enum defines the status values an order can exist in.
    """
    PLACED = 0
    PAID = 1
    SHIPPED = 2
    DELIVERED = 3
    CANCELLED = 4

######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################


class PersistentBase:
    """Base class added persistent methods"""

    def __init__(self):
        self.id = None  # pylint: disable=invalid-name

    def create(self):
        """
        Creates an Order/Item to the database
        """
        logger.info("Creating %s", self.id)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates an Order/Item to the database
        """
        logger.info("Updating %s", self.id)
        db.session.commit()

    def delete(self):
        """Removes an Order/Item from the database"""
        logger.info("Deleting %s", self.id)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the records in the database"""
        logger.info("Processing all records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a record by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

######################################################################
#  I T E M   M O D E L
#  Item: represents a product with the quantity and its price
######################################################################


class Item(db.Model, PersistentBase):
    """
    Class that represents an item
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Item {self.product_id} id=[{self.id}] order[{self.order_id}]>"

    def __str__(self):
        return f"Item {self.product_id}: {self.quantity}, {self.price}$"

    def serialize(self):
        """Serializes an item into a dictionary"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": self.price
        }

    def deserialize(self, data):
        """
        Deserializes an item from a dictionary
        Args:
            data (dict): A dictionary containing the Item data
        """
        try:
            self.order_id = data["order_id"]
            self.product_id = data["product_id"]
            self.quantity = data["quantity"]
            self.price = data["price"]

        except KeyError as error:
            raise DataValidationError("Invalid Item: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained bad or no data " + error.args[0]
            ) from error
        return self

######################################################################
#  O R D E R   M O D E L
#  Order: a collection of order items
######################################################################


class Order(db.Model, PersistentBase):
    """
    Class that represents an Order
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    tracking_id = db.Column(db.Integer)
    created_time = db.Column(db.DateTime(), default=datetime.now)
    status = db.Column(
        db.Enum(OrderStatus), nullable=False, server_default=(OrderStatus.PLACED.name)
    )
    order_items = db.relationship('Item', backref='order', passive_deletes=True)

    def __repr__(self):
        str_return = f"<Order {self.id}: Customer_id=[{self.customer_id}], "
        str_return += f"Tracking_id=[{self.tracking_id}], Status=[{self.status}], "
        str_return += f"items_number=[{len(self.order_items)}]>"
        return str_return

    def serialize(self):
        """Serializes an order into a dictionary"""
        items = []
        for item in self.order_items:
            items.append(Item.serialize(item))

        order = {
            "id": self.id,
            "customer_id": self.customer_id,
            "tracking_id": self.tracking_id,
            "created_time": self.created_time,
            "status": self.status.name,
            "order_items": items
        }

        return order

    def deserialize(self, data):
        """
        Deserializes an order from a dictionary
        Args:
            data (dict): A dictionary containing the order data
        """
        try:
            self.customer_id = data["customer_id"]
            self.tracking_id = data["tracking_id"]
            self.status = getattr(OrderStatus, data["status"])

            self.order_items = []
            if "order_items" in data.keys():
                for item in data["order_items"]:
                    self.order_items.append(
                        Item().deserialize(item))

        except KeyError as error:
            raise DataValidationError("Invalid Order: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order: body of request contained bad or no data - " + error.args[0]
            ) from error
        return self

    @classmethod
    def find_by_customer(cls, customer_id: int):
        """Returns all Orders of the given customer ID

        :param status: the id of the customer you want to match
        :type category: int

        :return: a collection of Orders for that customer
        :rtype: list

        """
        logger.info("Processing customer query for %d ...", customer_id)
        return cls.query.filter(cls.customer_id == customer_id)

    @classmethod
    def find_by_status(cls, status: OrderStatus = OrderStatus.PLACED):
        """Returns all Orders with the given status

        :param status: values are ['PLACED', 'PAID', 'SHIPPED', 'DELIVERED','CANCELLED']
        :type available: enum

        :return: a collection of Orders that are with specific status
        :rtype: list

        """
        logger.info("Processing status query for %s ...", status)
        return cls.query.filter(cls.status == status)

    @classmethod
    def find_by_item(cls, product_id: int):
        """Returns all Orders with the given item product id

        :param product_id: the product id of the item you want to match
        :type name: int

        :return: a collection of coders with that item inside
        :rtype: list

        """
        logger.info("Processing item query for %s ...", product_id)
        return cls.query.filter(cls.order_items.any(Item.product_id == product_id))
