from flask import Flask, request, Response
import json
import requests

from flask_sqlalchemy import SQLAlchemy

base_url = "/pizza_shop"

order_num = 0

content_type = 'application/json'
accept_type = 'application/json'

chef_ip = '10.7.160.29'
chef_base_url = 'http://' + chef_ip + ':5000/pizza_chef'

my_app = Flask(__name__)
my_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://dev:dev@' + chef_ip + '/postgres'
db = SQLAlchemy(my_app)

class Menu(db.Model):
    id     = db.Column(db.Integer, primary_key=True)
    pizza  = db.Column(db.Text)
    recipe = db.Column(db.Text)

    def __init__(self, pizza, recipe):
        self.pizza = pizza
        self.recipe = recipe

class Inventory(db.Model):
   id    = db.Column(db.Integer, primary_key=True)
   count = db.Column(db.Integer)
   item  = db.Column(db.Integer)

   def __init__(self, count, item):
       self.count = count
       self.item = item

class Orders(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   pizza = db.Column(db.String(100))
   p_status = db.Column(db.String(50))

   def __init__(self, pizza, p_status):
       self.pizza = pizza
       self.p_status = p_status

db.create_all()

# SELECT pizzas FROM menu; returns a list of tuples
# [('Pepperoni',), ("Sausage",), ("Cheese",)]
pizzas = Menu.query.with_entities(Menu.pizza).all()
pizza_menu = [entry for row in pizzas for entry in row]

@my_app.route(base_url, methods=['GET'])
def get_menu():
    response = {
        'pizzas': pizza_menu
    }
    return Response(response=json.dumps(response), status=200, mimetype='application/json')


@my_app.route(base_url, methods=['POST'])
def check_inventory():
    order = request.get_json()
    pizza = order.get('pizza')

    if pizza not in pizza_menu:
        response = {
            "Status": "Bad Order",
            "Reason": "The pizza requested is not available",
            "Pizza Requested": pizza
        }

        return Response(response=json.dumps(response), status=400, mimetype='application/json')

    # print("Hello world! ")
    headers = {
        'Content-Type': content_type,
        'Accept': accept_type
    }

    body = order

    ingredients_resp = requests.post(url=chef_base_url, headers=headers, data=json.dumps(body))
    ingredients_resp = ingredients_resp.json()
    status = ingredients_resp["Status"]

    if status == "Bad Order":
        response = {
            "Status": "Bad Order",
            "Reason": "The pizza requested is not available",
            "Pizza Requested": pizza
        }

        return Response(response=json.dumps(response), status=400, mimetype='application/json')

    if status == "No Inventory":
        response = {
            "Status": "Bad Order",
            "Reason": "The pizza requested is out of inventory",
            "Pizza Requested": pizza
        }

        return Response(response=json.dumps(response), status=400, mimetype='application/json')


    response = {
        "Status": "Complete",
        "Reason": "Your order has been completed"
    }

    return Response(response=json.dumps(response), status=200, mimetype='application/json')


@my_app.route(base_url + '/order', methods=['POST'])
def make_order():
    global order_num
    headers = {
        'Content-Type': content_type,
        'Accept': accept_type
    }

    body = request.get_json()
    body["ID"] = str(order_num)
    order_num += 1

    post_response = requests.post(url=chef_base_url + "/update", headers=headers, data=json.dumps(body))
    # post_response = requests.post(url="http://localhost:5000" + base_url, headers=headers, data=json.dumps(body))
    post_response = post_response.json()

    status = post_response["Status"]
    if status == "In Progress" or status == "Done":
        return Response(response=json.dumps(post_response), status=200, mimetype='application/json')

    # Something went wrong with the order
    return Response(response=json.dumps(post_response), status=400, mimetype='application/json')


@my_app.route(base_url + '/order', methods=['GET'])
def check_order():
    ID = request.args.get("ID")
    ID = int(ID)

    headers = {
        'Content-Type': content_type,
        'Accept': accept_type
    }

    id_check = requests.get(url=chef_base_url + "/order?ID=" + str(ID), headers=headers)
    id_check = id_check.json()

    status = id_check["Status"]

    if status == "Done":
        # Remove order
        delete_resp = requests.delete(url=chef_base_url + "/pickup?ID=" + str(ID), headers=headers)
        delete_resp = delete_resp.json()

        status = delete_resp["Status"]
        if status != "Order Picked Up":
            response = {
                "Status": "Bad Pick Up",
                "Reason": "Something is wrong with this order"
            }
            return Response(response=json.dumps(response), status=400, mimetype='application/json')

        return Response(response=json.dumps(delete_resp), status=200, mimetype='application/json')

    # Something went wrong with the order
    return Response(response=json.dumps(id_check), status=400, mimetype='application/json')


@my_app.route('/')
def health():
    response_text = '{ "status": "OK" }'
    response = Response(response_text, 200, mimetype='application/json')
    return response


if __name__ == '__main__':
    my_app.run(host='127.0.0.1')
