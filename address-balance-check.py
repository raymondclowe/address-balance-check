import csv
import os
import subprocess
import json


def start_daemon(electrum_path):
    # start Electrum daemon as a subprocess
    daemon_proc = subprocess.Popen([electrum_path, "daemon"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # wait for the daemon to start
    output, error = daemon_proc.communicate()
    if daemon_proc.returncode != 0:
        print(f"Error starting daemon: {error}")
        exit()


def stop_daemon(electrum_path):
    # stop the Electrum daemon
    subprocess.Popen([electrum_path, "stop"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def get_wallet_files(wallets_folder):
    # find all the wallet files in the folder
    wallet_files = [os.path.join(wallets_folder, f) for f in os.listdir(wallets_folder) if f.endswith(".dat")]
    return wallet_files


def get_wallet_data(wallet_file, electrum_path):
    data_list = []
    # open the wallet using Electrum CLI
    proc = subprocess.Popen([electrum_path, "-w", wallet_file, "listaddresses"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = proc.communicate()
    if proc.returncode != 0:
        print(f"Error opening wallet {wallet_file}: {error}")
        return []
    
    # parse the output and get the list of addresses
    addresses = json.loads(output.decode())
    
    # for each address, get the balance and transaction count
    for address in addresses:
        # get the balance
        proc = subprocess.Popen([electrum_path, "-w", wallet_file, "getaddressbalance", address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = proc.communicate()
        if proc.returncode != 0:
            print(f"Error getting balance for address {address}: {error}")
            return []

        # parse the output and get the balance and transaction count
        balance_data = json.loads(output.decode())
        balance = balance_data["confirmed"]
        tx_count = balance_data["history"]

        # add the data to the list
        data_list.append({
            "wallet_name": os.path.basename(wallet_file),
            "address": address,
            "balance": balance,
            "tx_count": tx_count
        })

    return data_list


def write_to_csv(data_list):
    # output the data to a CSV file
    with open("wallet_data.csv", mode="w", newline="") as csv_file:
        fieldnames = ["wallet_name", "address", "balance", "tx_count"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        writer.writeheader()
        for data in data_list:
            writer.writerow(data)


# set the path to the Electrum executable
electrum_path = "C:/path/to/electrum.exe"

# start the daemon
start_daemon(electrum_path)

# specify the path to the folder containing the wallets
wallets_folder = "C:/path/to/wallets/folder"

# get the list of wallet files
wallet_files = get_wallet_files(wallets_folder)

# create a list to store the collected data
data_list = []

# for each wallet, get the list of addresses and their balances
for wallet_file in wallet_files:
    wallet_data = get_wallet_data(wallet_file, electrum_path)
    if wallet_data:
        data_list.extend(wallet_data)

# write the data to a CSV file
write_to_csv(data_list)

# stop the daemon
stop_daemon(electrum_path)
