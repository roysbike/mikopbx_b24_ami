import requests
import asterisk.manager
import os
import re

# Variables for AMI and Asterisk
ASTERISK_IP = os.environ['ASTERISK_IP']
AMI_USERNAME = os.environ['AMI_USERNAME']
AMI_PASSWORD = os.environ['AMI_PASSWORD']
QUEUE_NAME = os.environ.get('QUEUE_NAME', "")
EXPECTED_NUMBERS = os.environ.get('EXPECTED_NUMBERS', "").split(",")

# Variables for Bitrix24
B24_HOOK = os.environ['B24_HOOK']
B24_DEPARTMENT_ID = int(os.environ['B24_DEPARTMENT_ID'])

def get_open_day_users_from_bitrix24():
    """Fetch open day users from Bitrix24."""
    users_endpoint = f"{B24_HOOK}/user.get.json?FILTER[UF_DEPARTMENT]={B24_DEPARTMENT_ID}&SELECT[]=UF_PHONE_INNER"
    response = requests.get(users_endpoint)
    users = response.json().get('result', [])

    users_with_open_day = []

    for user in users:
        user_id = user["ID"]
        timeman_endpoint = f"{B24_HOOK}/timeman.status?USER_ID={user_id}"
        response = requests.get(timeman_endpoint)
        timeman_status = response.json().get('result', {}).get('STATUS', "")

        if timeman_status == "OPENED":
            users_with_open_day.append(user)

    inner_phone_numbers = [user.get('UF_PHONE_INNER', '') for user in users_with_open_day if user.get('UF_PHONE_INNER')]

    print(f"Fetched employee numbers from Bitrix24: {', '.join(inner_phone_numbers)}")

    return inner_phone_numbers

def is_dynamic_number(manager, number):
    response = manager.send_action({'Action': 'QueueStatus', 'Queue': QUEUE_NAME})
    full_response = ''.join(response.data)
    
    dynamic_pattern = rf'{QUEUE_NAME}.*?Local/{number}@.*?dynamic'
    return bool(re.search(dynamic_pattern, full_response))

def get_queue_status(manager):
    """Get status of all queues."""
    response = manager.send_action({'Action': 'QueueStatus'})
    full_response = ''.join(response.data)

    queue_names = re.findall(r'Queue: (\S+)', full_response)
    unique_queue_names = list(set(queue_names))

    for name in unique_queue_names:
        number_pattern = re.compile(rf'{name}.*?Local/(\d+)@', re.DOTALL)
        queue_numbers = re.findall(number_pattern, full_response)
        
        print(f"Queue {name}: {', '.join(queue_numbers)}")
    
    return unique_queue_names

def get_current_queue_numbers(manager):
    """Get numbers currently in the specified queue."""
    response = manager.send_action({'Action': 'QueueStatus'})
    full_response = ''.join(response.data)
    
    number_pattern = re.compile(rf'{QUEUE_NAME}.*?Local/(\d+)@', re.DOTALL)
    actual_numbers = re.findall(number_pattern, full_response)
    
    return actual_numbers

def add_expected_numbers_to_queue(manager, current_numbers):
    """Add expected numbers to queue if not already present."""
    for number in EXPECTED_NUMBERS:
        if number not in current_numbers:
            print(f"Adding number {number} to queue {QUEUE_NAME}...")
            manager.send_action({
                'Action': 'QueueAdd',
                'Queue': QUEUE_NAME,
                'Interface': f'Local/{number}@internal/n',
                'Penalty': 0
            })

def remove_unexpected_numbers_from_queue(manager, current_numbers):
    """Remove unexpected numbers from queue."""
    for number in current_numbers:
        if number not in EXPECTED_NUMBERS and is_dynamic_number(manager, number):
            print(f"Removing number {number} from queue {QUEUE_NAME}...")
            manager.send_action({
                'Action': 'QueueRemove',
                'Queue': QUEUE_NAME,
                'Interface': f'Local/{number}@internal/n'
            })

def main():
    global EXPECTED_NUMBERS
    
    inner_phone_numbers = get_open_day_users_from_bitrix24()
    
    if inner_phone_numbers:
        EXPECTED_NUMBERS = inner_phone_numbers
    
    manager = asterisk.manager.Manager()
    manager.connect(ASTERISK_IP)
    manager.login(AMI_USERNAME, AMI_PASSWORD)

    all_queues = get_queue_status(manager)

    if not QUEUE_NAME:
        print("Error: QUEUE_NAME not specified!")
        return

    current_numbers = get_current_queue_numbers(manager)
    print(f"Current numbers in queue {QUEUE_NAME}: {', '.join(current_numbers)}")

    if set(current_numbers) == set(EXPECTED_NUMBERS):
        print("Queue numbers match expected numbers. No changes required.")
        return

    add_expected_numbers_to_queue(manager, current_numbers)
    remove_unexpected_numbers_from_queue(manager, current_numbers)

    manager.logoff()

if __name__ == "__main__":
    main()
