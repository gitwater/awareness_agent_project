from agent import Agent
from database import Database
import json

def main():
    print("Welcome to the Awareness Improvement Agent!")
    profile_data_path = 'slippityj'
    #profile_data_path = input("Please enter the path to your user data or enter your username: ")
    db = Database()
    # If the value is a path then load it with the profile parser
    # Otherwise, assume it's a username and load the profile from the database
    if '/' in profile_data_path:
        # Ask for the user's username
        username = input("Please enter your username: ")
        # Load the profile data directly from the file path/profile-data.json without using ProfileParser
        profile_file_path = profile_data_path + '/profile-data.json'
        with open(profile_file_path, 'r') as file:
            user_profile_dict = json.load(file)

        user_profile_string = json.dumps(user_profile_dict)


        user_info = {}
        # Ask for user information
        user_info['username'] = username
        user_info['birthdate'] = input("Please enter your birthdate: ")
        user_info['gender'] = input("Please enter your gender: ")
        user_info['sexual orientation'] = input("Please enter your sexual orientation: ")
        user_info['culture'] = {}
        user_info['culture']['born_in_country'] = input("Please enter the country you were born in: ")
        user_info['culture']['most_in_country'] = input("Please enter the country you've spent the most time in: ")
        user_info['culture']['born_in_city'] = input("Please enter the city you were born in: ")
        user_info['culture']['most_in_city'] = input("Please enter the city you've spent the most time in: ")
        user_info['culture']['religion'] = input("Please enter your religion: ")
        user_info['culture']['interests'] = input("Please enter your interests: ")
        user_info['culture'] = json.dumps(user_info['culture'])
        user_info['language'] = input("Please enter your native language: ")
        user_info['dimensions'] = user_profile_string
        user_info = db.save_user_info(user_info)
    else:
        username = profile_data_path
        user_info = db.get_user_info(username)

    agent = Agent(user_info=user_info, db_connection=db)

    agent.main_loop()

    # while True:
    #     user_input = input("> ")
    #     if user_input.lower() in ['exit', 'quit']:
    #         print("Goodbye!")
    #         break
    #     response = agent.receive_input(user_input)
    #     print(response)

if __name__ == "__main__":
    main()





