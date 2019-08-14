import re


class Validator:
    def __init__(self):
        self.user_props = ['email', 'username', 'name', 'password']
        self.review_props = ['rating', 'body']
        self.business_props = ['name', 'description', 'location', 'category']
        self.has_numbers = re.compile('[0-9]')
        self.has_special = re.compile('[^\w\s]')

    def validate(self, obj, con):
        if con == 'user_reg':
            message = {}
            for prop in self.user_props:
                if prop not in obj:
                    message[prop+' error'] = f"Please provide {prop}"
            for prop in self.user_props:
                if prop in obj and str(obj[prop]).strip() == "":
                    message[prop+' error'] = f'Empty {prop} is not allowed'
            if 'name' in obj and len(str(obj['name'])) > 255:
                message['name error'] = 'Name cannot be more than 255 characters'
            if 'email' in obj and '@' not in str(obj['email']):
                message['email error'] = 'Email is invalid'
            if 'email' in obj and '.' not in str(obj['email']):
                message['email error'] = 'Email is invalid'
            if 'password' in obj and len(str(obj['password'])) < 6:
                message['password error'] = 'Password cannot be less than 6 characters'
            if 'password' in obj and not self.has_special.search(obj['password']):
                message['password error'] = 'Strong password must have at least one special character'
            if 'password' in obj and not self.has_numbers.search(obj['password']):
                message['password error'] = 'Strong password must have at least one number character'
            if 'password' in obj and len(str(obj['password'])) > 255:
                message['password error'] = 'Password cannot be more than 255 characters'
            if 'email' in obj and len(str(obj['email'])) > 255:
                message['email error'] = 'Email cannot be more than 255 characters'
            if 'username' in obj and len(str(obj['username'])) > 10:
                message['username error'] = 'Username cannot be more than 10 characters'
            if message:
                return message

        if con == 'business_reg':
            message = {}
            for prop in self.business_props:
                if prop not in obj:
                    message[prop+' error'] = f"Please provide {prop}"
            for prop in self.business_props:
                if prop in obj and str(obj[prop]).strip() == "":
                    message[prop+' error'] = f'Empty {prop} is not allowed'
            if "name" in obj and len(str(obj['name'])) > 255:
                message['name error'] = 'Name must be less than 255 characters'
            if 'description' in obj and len(str(obj['description'])) > 255:
                message['description error'] = 'Description must be less than 255 characters'
            if 'location' in obj and len(str(obj['location'])) > 255:
                message['location error'] = 'Location string must be less than 255 characters'
            if message:
                return message

        if con == 'review_reg':
            message = {}
            for prop in self.review_props:
                if prop not in obj:
                    message[prop+' error'] = f"Please provide {prop}"
            for prop in self.review_props:
                if prop in obj and str(obj[prop]).strip() == "":
                    message[prop + ' error'] = f'Empty {prop} is not allowed'
            if 'rating' in obj and not isinstance(int(obj['rating']), int):
                message['rating error'] = 'Rating must be a value'
            if 'body' in obj and len(str(obj['body'])) > 255:
                message['review error'] = 'Review must be less than 255 characters'
            if 'rating' in obj and int(obj['rating']) > 5:
                message['rating error'] = 'Rating must be less than 5'
            if message:
                return message
