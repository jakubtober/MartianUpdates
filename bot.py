import messages
from data_scraper import *
import json
import random


class Bot():

    def __init__(self, load_photos='no'):
        print(time_now() + 'starting bot...')
        self.my_data = RoverDataScraper()
        print(time_now() + 'collecting data...')
        self.my_data.scrap_missing_sols_data()
        if load_photos == 'yes':
            self.my_data.get_photos(self.my_data.last_day_data['sol'], 'navcam')
        self.my_data.get_time()

        self.sample_messages = {}

        if self.my_data.time:
            time_message = messages.Message(my_data=self.my_data)
            time_message.create_tweet_message_time()
            self.sample_messages['time'] = time_message
        if self.my_data.time and self.my_data.location_str:
            location_and_time_message = messages.Message(my_data=self.my_data)
            location_and_time_message.create_tweet_message_location_and_time()
            self.sample_messages['location_and_time'] = location_and_time_message
        if self.my_data.last_day_data:
            weather_message = messages.Message(my_data=self.my_data)
            weather_message.create_tweet_message_weather()
            self.sample_messages['weather'] = weather_message

    def print_sample_messages_in_cmd(self):
        print(time_now() + 'sample messages:' + '\n')
        print(self.sample_messages['time'])
        print(self.sample_messages['location_and_time'])
        print(self.sample_messages['weather'])

    def choose_message(self):
        sols_in_history = []
        posts_history_with_indexes = {}
        is_post_selected = False

        posts_history_file = open('posts_history.json')
        history_data = json.load(posts_history_file)

        for key in history_data.keys():
            sols_in_history.append(int(key))

        last_days_history = (
            [history_data[str(sols_in_history)] for sols_in_history in
             sorted(sols_in_history, reverse=True)]
        )

        print(time_now() + 'last message posted on sol: ' + str(max(sols_in_history)))
        print(time_now() + 'last post type: ' + history_data[str(max(sols_in_history))])

        available_message_types_for_new_post = [key for key in self.sample_messages.keys()]
        random.shuffle(available_message_types_for_new_post)
        print(time_now() + 'types of posts availabe for new post: ' +
              str(available_message_types_for_new_post))

        # check 3 days history of posts, use new topic if not used during this time
        for message_type in available_message_types_for_new_post:
            if message_type not in last_days_history[:3]:
                self.message_to_post = self.sample_messages[message_type]
                print(time_now() + 'type for new message: ' + str(message_type))
                is_post_selected = True
                break

        # if all post types has been used for last 3 days, use the oldest used topic
        if is_post_selected == False:
            print(time_now() + "looking for the oldest topic...")
            for message_type in available_message_types_for_new_post:
                for index in range(len(last_days_history)):
                    if last_days_history[index] == message_type:
                        posts_history_with_indexes[index] = message_type
                        break
            posts_history_index_max = max(list(posts_history_with_indexes.keys()))
            self.message_to_post = (
                self.sample_messages[posts_history_with_indexes[posts_history_index_max]]
            )

        print(time_now() + 'new message to post: ' + str(self.message_to_post))

        # check if post for last availabe sol hasn't been published yet, if not publish on twitter
        if self.my_data.present_sol_number not in sols_in_history:
            if self.sample_messages:
                self.message_to_post.post_on_twitter()
                print(time_now() + 'message posted on twitter.')
            else:
                print(time_now() + 'sorry, there are not messages to post now.')
        else:
            print(time_now() + "there are already posts for this sol on twitter, can't publish it.")
