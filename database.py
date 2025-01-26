from dotenv import load_dotenv
import os
from pymongo import MongoClient
from users.utils import user, usertype
from vechiles.utils import vechile, vechiletype, availability_status
from rentals.utils import rental, rental_request
from branches.utils import branch
import bcrypt


load_dotenv()



mongo_client = MongoClient(os.getenv("MONGO_URI"))

sysdb = mongo_client[os.getenv("DATABASE_NAME")]
users = sysdb[os.getenv("USER_COLLECTION")]
vechiles = sysdb[os.getenv("VECHILE_COLLECTION")]
rentals = sysdb[os.getenv("RENTAL_COLLECTION")]
rental_requests = sysdb[os.getenv("RENTAL_REQUEST_COLLECTION")]
branches = sysdb[os.getenv("BRANCH_COLLECTION")]




for user in users.find({}):
    print(user)

print("\n")

for branch in branches.find({}):
    print(branch)
    
print("\n")

for vechile in vechiles.find({}):
    print(vechile)
    
print("\n")

for rental in rentals.find({}):
    print(rental)
    
print("\n")

for rental_request in rental_requests.find({}):
    print(rental_request)

'''cust1 = user.create_user('sara', '1234', usertype.CUSTOMER)
emp1 = user.create_user('mike', '1234', usertype.EMPLOYEE)
branch1 = branch.create_branch('1234', '1234', '1234')
vec1 = vechile.create_vechile('1234', '1234', vechiletype.CAR, availability_status.AVAILABLE, '1234', 100.0)
rent1 = rental.create_rental('vec1734286304', 'cust1734285610', '01/01/2020', '10/01/2020')
req1 = rental_request.create_rental_request('vec1734286304', 'cust1734285610', '01/01/2020', '10/01/2020')
employee emp1734285610'''