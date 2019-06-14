from flask import request, Response, Flask
import json
from flask_sqlalchemy import SQLAlchemy

my_app = Flask(__name__)

db = SQLAlchemy(my_app)
chef_ip = '10.7.160.29'
my_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://dev:dev@' + chef_ip + '/postgres'

base_url = "/pizza_chef"


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    item = db.Column(db.Integer)


def __init__(self, count, item):
    self.count = count
    self.item = item

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pizza = db.Column(db.String(100))
    recipe = db.Column(db.String(50))


def __init__(self, pizza, recipe):
    self.pizza = pizza
    self.recipe = recipe

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    p_status = db.Column(db.String(50))


def __init__(self, p_status):
    self.p_status = p_status

db.create_all()

# Creates list of pizza menu items from db
pizzas = Menu.query.with_entities(Menu.pizza).all()
pizza_menu = [entry for row in pizzas for entry in row]

# POST: Check inventory of pizza ingredients to see if pizza can be made
@my_app.route(base_url, methods=['POST'])
def make_pizza():
    order = request.get_json()
    pizza = order.get('pizza')

    if pizza in pizza_menu:
        recipe = Menu.query.filter_by(pizza=pizza).with_entities(Menu.recipe).all()

        # Check each pizza ingredient to make sure enough in inventory
        for i in recipe[0][0]['recipe']:
            inventory_list = Inventory.query.with_entities(Inventory.item, Inventory.count).all()
            inventory = {row[0]: row[1] for row in inventory_list}

            if inventory[i] < 1:
                response = {
                    "Status": "No Inventory",
                    "Reason": "Not enough " + i + " inventory to make pizza"
                }
                return Response(response=json.dumps(response), status=400, mimetype='application/json')

        # If enough, decrement inventory used and respond that order has been accepted
        for i in recipe[0][0]['recipe']:
            # Decrease each inventory item by 1
            inventory_item = Inventory.query.filter_by(item=i).first()
            inventory_item.count -= 1
            db.session.commit()

        response = {
            "Status": "Pizza Accepted",
            "Reason": "Ordered " + pizza
        }
        return Response(response=json.dumps(response), status=200, mimetype='application/json')

    # If pizza ordered is not on menu, return error response
    else:
        response = {
                "Status": "Bad Order",
                "Reason": "The pizza " + pizza + " is not known"
            }
        return Response(response=json.dumps(response), status=400, mimetype='application/json')


# POST: Initialize status of order ID, then update to done
@my_app.route(base_url + "/update", methods=['POST'])
def update_status():
    order_num = request.get_json()
    num_id = order_num.get('ID')

    # Set the IDs status
    new_order = Orders(id = num_id, p_status = "In Progress")
    db.session.add(new_order)
    db.session.commit()
    # order_ids[num_id] = "In Progress"


    # Update status
    order_item = Orders.query.filter_by(id = num_id).first()
    order_item.p_status = "Done"
    db.session.commit()
    # order_ids[num_id] = "Done"

    response = {
        "Status": "Pizza order is done",
        "ID": num_id
    }
    return Response(response=json.dumps(response), status=200, mimetype='application/json')


# GET: Retrieves current status of order by ID
@my_app.route(base_url + "/order", methods=['GET'])
def get_status():
    order_num = request.args.get('ID')
    order_num = int(order_num)

    ids = Orders.query.with_entities(Orders.id).all()
    order_ids = [entry for row in ids for entry in row]

    if order_num in order_ids:
        response = {
            "Status": Orders.query.filter_by(id=order_num).with_entities(Orders.p_status).first()[0]
        }
        return Response(response=json.dumps(response), status=200, mimetype='application/json')

    response = {
       "Status": "Order does not exist"
    }
    return Response(response=json.dumps(response), status=400, mimetype='application/json')


# DELETE: Order is picked up and deleted from db
@my_app.route(base_url + "/pickup", methods=['DELETE'])
def pickup():
    order_num = request.args.get('ID')
    order_num = int(order_num)

    ids = Orders.query.with_entities(Orders.id).all()
    order_ids = [entry for row in ids for entry in row]

    # If order status is "Done", delete for pick up
    if  order_num in order_ids and Orders.query.filter_by(id=order_num).with_entities(Orders.p_status).first()[0] == "Done":
        db.session.delete(Orders.query.filter_by(id = order_num).first())
        db.session.commit()

        response = {
            "Status": "Order Picked Up"
        }
        return Response(response=json.dumps(response), status=200, mimetype='application/json')

    response = {
        "Status": "Bad Pick Up"
    }

    return Response(response=json.dumps(response), status=400, mimetype='application/json')


if __name__ == "__main__":
    my_app.run(host='0.0.0.0')

