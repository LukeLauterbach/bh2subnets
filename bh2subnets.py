import argparse
import json
import socket
import sys


# --------------------------------------- #
#               FUNCTIONS                 #
# --------------------------------------- #

def read_computers_file(input_file=""):
    hostnames = []
    try:
        # Open and read the JSON file
        with open(input_file, 'r') as file:
            hostnames = read_sharphound_file(file)
    except FileNotFoundError:
        print(f"File '{input_file}' not found.")

    return hostnames


def read_sharphound_file(input_file=None):
    hostnames = []
    data = json.load(input_file)
    for computer_object in data['data']:
        hostnames.append(computer_object['Properties']['name'])
    return hostnames


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


def parse_arguments():
    parser = argparse.ArgumentParser(description="Get list of subnets from BloodHound/SharpHound data")
    parser.add_argument("list_of_hostnames", type=str,
                        help="File with list of hostnames. SharpHound computers.json, BloodHound JSON export, or "
                             "txt file with hostname per line accepted.")
    parser.add_argument("-o", "--output-file", type=str,
                        help="(OPTIONAL) Output filename. If no filename is provided, output will be displayed in the"
                             "terminal only.")

    args = parser.parse_args()

    return args.list_of_hostnames, args.output_file

def main(input_file="", output_file=""):
    subnets = []
    device_names = read_computers_file(input_file=input_file)
    for hostname in device_names:
        subnet = get_first_three_octets(hostname)
        if subnet is not None:
            subnets.append(subnet)
    subnets = deduplicate_and_add_subnet(subnets)

    for subnet in subnets:
        print(subnet)

    if output_file:
        write_list_to_file(output_file_name, subnets)


# --------------------------------------- #
#               MAIN                      #
# --------------------------------------- #

if __name__ == "__main__":
    main_input_file, main_output_file = parse_arguments()
    main(input_file=main_input_file, output_file=main_output_file)
