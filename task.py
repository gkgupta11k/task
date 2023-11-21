import json
from collections import defaultdict
from datetime import datetime, timedelta

# Function to read JSON data from a file
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to write JSON data to a file
def write_json_file(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Function to get the most recent completion of each training for each person
def get_most_recent_completions(data):
    recent_completions = {}
    for person in data:
        person_completions = {}
        for completion in person["completions"]:
            training = completion["name"]
            timestamp = datetime.strptime(completion["timestamp"], "%m/%d/%Y")
            if training not in person_completions or timestamp > person_completions[training][0]:
                person_completions[training] = (timestamp, completion.get("expires"))
        recent_completions[person["name"]] = person_completions
    return recent_completions

# Function to count the number of people who completed each training
def count_training_completions(recent_completions):
    training_counts = defaultdict(set)
    for person, completions in recent_completions.items():
        for training in completions:
            training_counts[training].add(person)
    return {training: len(people) for training, people in training_counts.items()}

# Function to find completions in a specified fiscal year for given trainings
def find_completions_in_fiscal_year(recent_completions, trainings, fiscal_year_start, fiscal_year_end):
    completions_in_fy = defaultdict(list)
    for person, completions in recent_completions.items():
        for training, (timestamp, _) in completions.items():
            if training in trainings and fiscal_year_start <= timestamp <= fiscal_year_end:
                completions_in_fy[training].append(person)
    return completions_in_fy

# Function to find people with expired or soon-to-expire trainings
def find_expired_soon_expiring_trainings(recent_completions, check_date):
    result = defaultdict(dict)
    for person, completions in recent_completions.items():
        for training, (timestamp, expires) in completions.items():
            if expires:
                expiration_date = datetime.strptime(expires, "%m/%d/%Y")
                if expiration_date < check_date + timedelta(days=30):
                    status = "expired" if expiration_date < check_date else "expires soon"
                    result[person][training] = status
    return result

# Reading the JSON data from the file
data = read_json_file("trainings.txt")

# Processing the data to get the most recent completions
most_recent_data = get_most_recent_completions(data)

# Part 1: Training completion counts
training_counts = count_training_completions(most_recent_data)
print("Training Completion Counts:\n", json.dumps(training_counts, indent=4))
write_json_file(training_counts, "training_counts_output.json")

# Part 2: Completions in Fiscal Year 2024 for specified trainings
specified_trainings = ["Electrical Safety for Labs", "X-Ray Safety", "Laboratory Safety Training"]
fiscal_year_start = datetime(2023, 7, 1)
fiscal_year_end = datetime(2024, 6, 30)
fy_completions = find_completions_in_fiscal_year(most_recent_data, specified_trainings, fiscal_year_start, fiscal_year_end)
print("\nFiscal Year Completions:\n", json.dumps(fy_completions, indent=4))
write_json_file(fy_completions, "fiscal_year_completions_output.json")

# Part 3: Expired or soon-to-expire trainings as of Oct 1st, 2023
check_date = datetime(2023, 10, 1)
expired_soon_expiring = find_expired_soon_expiring_trainings(most_recent_data, check_date)
print("\nExpired or Soon-to-Expire Trainings:\n", json.dumps(expired_soon_expiring, indent=4))
write_json_file(expired_soon_expiring, "expired_soon_expiring_output.json")
