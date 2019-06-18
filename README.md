# Pizza-Shop
Practice mircroservice API

Pizza-Chef and Pizza-Shop interact with each other to allow a client to order a pizza, check the status of a pizza, and pick up a pizza. The chef API can check the menu data base and inventory database to determine if the pizza ordered can be made. 

Technologies used:
	• Python (PyCharm)
  • Flask
  • Docker
  • TablePlus
  • SQL
  • SQLAlchemy


		○ SHOP makes POST to /pizza_chef
			§ CHEF checks if pizza is in menu
				□ If yes, checks inventory
					® If enough --> respond w/ "pizza accepted"
					® If no, respond with "not enough inventory"
				□ If no, responds "bad order"
				
		○ SHOP makes POST to /update with order ID
			§ CHEF creates new order with given ID and status of "In Progress"
				□ Add to Orders database
			§ CHEF updates order in database based on ID to "Done"
			§ CHEF responds "pizza is done"
		
		○ SHOP makes GET to /order with ID as argument
			§ If order exists in database, respond with status
			§ If order does not exist, respond that it doesn’t

		○ SHOP makes DELETE to /pickup with ID as argument
			§ If the status of that order in the database is "Done"
				□ Delete row from database and respond "Order picked up"
			§ If order specified is not ready, respond "Bad pick up"
