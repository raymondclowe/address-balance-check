import csv
import os
import subprocess
import json


def find_electrum_path():
    print("start: find_electrum_path")
    """
    Finds the Electrum executable based on common locations it might be located in.
    Returns the path to the executable if found, otherwise returns None.
    """
    if os.name == 'nt': # Windows
        paths_to_check = ['C:/Program Files (x86)/Electrum', 'C:/Program Files/Electrum']
        for path in paths_to_check:
            for file_name in os.listdir(path):
                if 'electrum' in file_name.lower() and 'debug' not in file_name.lower() and file_name.endswith('.exe'):
                    return os.path.join(path, file_name)
    else: # Unix-like
        paths_to_check = ['/usr/bin', '/usr/local/bin', '/opt', os.path.expanduser('~/bin')]
        for path in paths_to_check:
            for file_name in os.listdir(path):
                if 'electrum' in file_name.lower() and 'debug' not in file_name.lower() and os.access(os.path.join(path, file_name), os.X_OK):
                    return os.path.join(path, file_name)
    return None
    print("end: find_electrum_path")




def start_daemon(electrum_path):
    print("start: start_daemon")
    # start Electrum daemon as a subprocess
    daemon_proc = subprocess.Popen([electrum_path, "daemon"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # wait for the daemon to start
    output, error = daemon_proc.communicate()
    if daemon_proc.returncode != 0:
        print(f"Error starting daemon: {error}")
        exit()
    print("end: start_daemon")



def stop_daemon(electrum_path):
    print("start: stop_daemon")
    # stop the Electrum daemon
    proc = subprocess.Popen([electrum_path, "stop"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = proc.communicate()
    if proc.returncode != 0:
        print(f"Error stopping daemon: {error}")
    print("end: stop_daemon")



def get_wallet_files(wallets_folder):
    print("start: get_wallet_files")
    # find all the wallet files in the folder
    wallet_files = [os.path.join(wallets_folder, f) for f in os.listdir(wallets_folder) if f.endswith(".dat")]
    return wallet_files
    print("end: get_wallet_files")


def get_wallet_data(wallet_file, electrum_path):
    print("start: get_wallet_data")
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
        data_list
