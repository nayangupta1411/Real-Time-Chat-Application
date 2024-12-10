from database.database import db


class chatApp:
    def __init__():
        return 
    
    def add_new_user(user):
        print('db-->',db)
        print('models user',user)
        if db.users.find_one({'inputEmail':user.get('inputEmail')}):
            print('yes',db.users.find({'inputEmail':user.get('inputEmail')}))
            return True
        new_user=db.users.insert_one({
            'inputName':user.get('inputName'),
            'inputEmail':user.get('inputEmail'),
            'inputPassword': user.get('inputPassword'),
            'inputGender':user.get('inputGender')

        })
        return False
    
    def login_user(user):
        if db.users.find_one({'inputEmail':user.get('inputEmail'),'inputPassword': user.get('inputPassword')}):
            data=db.users.find({'inputEmail':user.get('inputEmail'),'inputPassword': user.get('inputPassword')})
            user_data=[{**user,"_id":str(user['_id'])} for user in data]
            print('yes',user_data)
            return user_data
            
        return False
    
    def activeUsers():
        users=db.users.find()
        active_user=[{**user,"_id":str(user['_id'])} for user in users]
        return active_user
    
    def personal_message(sender_email,receiver_email,room):
        messages=list( db.personal_message.find({ 'room': room}).sort('timestamp', 1) )

        for msg in messages:
            msg['_id'] = str(msg['_id'])  
        return messages
    
    def group_message(sender_email,room):
        messages=list( db.group_message.find({ 'room': room }).sort('timestamp', 1) )

        for msg in messages:
            msg['_id'] = str(msg['_id'])  
        return messages
    
    def create_group(access_email,access_email_name,result):
        create_group=db.create_group_accessKey.insert_one({
            'inputGroupName': result.get('inputGroupName'),
            'inputAccessKey': result.get('inputAccessKey'),
            'groupOwnerEmail': access_email,
            'groupOwnerName':access_email_name

        })
        groups=chatApp.all_groups(access_email)
        return groups
    
    def all_groups(access_email):
        owner_groups_data=db.create_group_accessKey.find({'groupOwnerEmail': access_email})
        owner_groups=[{**data,"_id":str(data['_id'])} for data in owner_groups_data]
        join_groups_data=db.join_group_accessKey.find({'groupJoinerEmail': access_email})
        join_groups=[{**data,"_id":str(data['_id'])} for data in join_groups_data]
        set_join_groups_according_owner_groups=[]
        for i in join_groups:
            group_owner_data=db.create_group_accessKey.find({'inputAccessKey':i.get('groupAccessKey')})
            owner_group=[{**data,"_id":str(data['_id'])} for data in group_owner_data]
           
            set_join_groups_according_owner_groups.append({
                'inputGroupName':i.get('joinGroupName'),
                'inputAccessKey': i.get('groupAccessKey'),
                'groupOwnerEmail': owner_group[0].get('groupOwnerEmail'),
                'groupOwnerName': owner_group[0].get('groupOwnerName')
            })

        all_groups=owner_groups+set_join_groups_according_owner_groups
        return all_groups
    
    def join_group(access_email,access_email_name,result):
        search_group=db.create_group_accessKey.find({'inputAccessKey': result.get('inputAccessKey')})
        group_data=[{**data,"_id":str(data['_id'])} for data in search_group]
        from_joined_group=db.join_group_accessKey.find({'groupAccessKey': result.get('inputAccessKey'),
                                                        'groupJoinerEmail':access_email})
        joined_group_data=[{**data,"_id":str(data['_id'])} for data in from_joined_group]
        print('data-->',joined_group_data)
        if len(joined_group_data)>0:
            return 'Joined'
        print('group_data-->',group_data)
        if len(group_data)>0:
            join_group=db.join_group_accessKey.insert_one({
            'joinGroupName': group_data[0].get('inputGroupName'),
            'groupAccessKey': group_data[0].get('inputAccessKey'),
            'groupJoinerEmail': access_email,
            'groupJoinerName':access_email_name
            })
            groups=chatApp.all_groups(access_email)
            return groups
        return False
    
    def group_members(room):
        owner_groups_data=db.create_group_accessKey.find({'inputAccessKey':room})
        owner_groups=[(data['groupOwnerName']) for data in owner_groups_data]
        join_groups_data=db.join_group_accessKey.find({'groupAccessKey': room})
        join_groups=[(data['groupJoinerName']) for data in join_groups_data]
        
        all_groups=owner_groups+join_groups
        print('all_groups',all_groups)
      
        return all_groups



        

    