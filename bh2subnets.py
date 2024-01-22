import json
import socket
import sys

# --------------------------------------- #
#               VARIABLES                 #
# --------------------------------------- #

input_file_name = "computers.json"
output_file_name = "subnets.txt"

device_names = []
subnets = []


# --------------------------------------- #
#               FUNCTIONS                 #
# --------------------------------------- #

def read_computers_file():
    try:
        # Open and read the JSON file
        with open(input_file_name, 'r') as file:
            # Load JSON data
            data = json.load(file)

            for computer_object in data["computers"]:
                device_names.append(computer_object['Properties']['name'])
    except FileNotFoundError:
        print(f"File '{input_file_name}' not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file '{input_file_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return device_names


def get_first_three_octets(l_hostname):
    try:
        # Perform NSLOOKUP
        ip_address = socket.gethostbyname(l_hostname)

        # Extract the first three octets
        first_three_octets = '.'.join(ip_address.split('.')[:3])

        return first_three_octets

    except socket.gaierror as e:
        pass


def deduplicate_and_add_subnet(input_list):
    # Deduplicate the list
    deduplicated_list = list(set(input_list))

    # Add ".0/24" to each entry
    result_list = [entry + ".0/24" for entry in deduplicated_list]

    return result_list


def write_list_to_file(file_path, input_list):
    if not file_path:
        return
    try:
        # Open the file in write mode
        with open(file_path, 'w') as file:
            # Write each element of the list to a new line
            for item in input_list:
                file.write(str(item) + '\n')

        print(f"List written to file: {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


# --------------------------------------- #
#               MAIN                      #
# --------------------------------------- #

# Accept Parameters
if len(sys.argv) == 3:
    # Get input and output file names from command-line arguments
    input_file_name = sys.argv[1]
    output_file_name = sys.argv[2]
elif len(sys.argv) == 2:
    input_file_name = sys.argv[1]
    output_file_name = None
else:
    print("Usage: python3 bh2subnet.py {input_file_name} {output_file_name}")
    print("If no output filename is provided, output will just go to console output")

device_names = read_computers_file()
for hostname in device_names:
    subnet = get_first_three_octets(hostname)
    if subnet is not None:
        subnets.append(subnet)
subnets = deduplicate_and_add_subnet(subnets)

for subnet in subnets:
    print(subnet)

write_list_to_file(output_file_name, subnets)
