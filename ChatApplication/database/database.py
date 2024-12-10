from pymongo import MongoClient 

DATABASE_BASE='mongodb://localhost:27017/'
print('database--',DATABASE_BASE)

client=MongoClient("mongodb://localhost:27017/")
chatApp=client['chatApp']

# chatAppDB_collection=chatApp.create_collection('users')
# chatAppDB_collection.insert_one({
#     'inputName':'Nayan Gupta',
#     'inputEmail':'nayan.gupta@hcltech.com',
#     'inputPassword':'nayan123',
#     'inputGender': 'Male'
# })

# libManageSysDB_collection=libManageSysDB.create_collection('admin_addBook')
# libManageSysDB_collection.insert_one({
#     inputTitle: 'Learning Python',
#   'inputAuthor': 'Mark Lutz',
#   'inputGenre': 'Technology',
#   'inputCopies': '10'
# })

print('client-',client.list_database_names())
db=client.chatApp