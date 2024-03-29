######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Order Steps

Steps file for Orders.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""

import requests
from behave import given
from compare import expect


@given('the following orders')
def step_impl(context):
    """ Delete all Orders and load new ones """
    # List all of the pets and delete them one by one
    context.order_ids = list()
    rest_endpoint = f"{context.BASE_URL}/api/orders"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for order in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{order['id']}")
        expect(context.resp.status_code).to_equal(204)

    # load the database with new orders
    for row in context.table:
        payload = {
            "customer_id": int(row['customer_id']),
            "tracking_id": int(row['tracking_id']),
            "created_time": row['created_time'],
            "status": row['status'],
            "order_items": list()
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        context.order_ids.append(context.resp.json()["id"])
        expect(context.resp.status_code).to_equal(201)
