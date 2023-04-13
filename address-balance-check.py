
import os
import psutil
import subprocess
import json
import csv
import sys

wallets_folder ="./wallets"

def is_electrum_running():
    for proc in psutil.process_iter(['name']):
        if 'electrum' in proc.info['name'].lower() and proc.info['name'].endswith('.exe'):
            return True
    return False



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





# check if this is main so it can be imported into a module
if __name__ == "__main__":
    print("This is the main module.")

    electrum_path = find_electrum_path()

    # if electrum is not running then
    if not is_electrum_running():
        # spawn electrum as a subprocess and don't wait, pass the parameter "daemon" and get the pid        
        # spawn Electrum as a subprocess and pass the "daemon" parameter
        electrum_process = subprocess.Popen([electrum_path, "daemon"])

        # get the process ID of Electrum
        electrum_pid = electrum_process.pid
   
    wallet_files = [os.path.join(wallets_folder, f) for f in os.listdir(wallets_folder) if os.path.isfile(os.path.join(wallets_folder, f))]
    
    data_list = []
    for wallet_file in wallet_files:
        
        # open the wallet using Electrum CLI

        proc = subprocess.Popen([electrum_path, "-w", wallet_file, "load_wallet"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = proc.communicate()
        if proc.returncode != 0:
            print(f"Error opening wallet {wallet_file}: {error}")
            break

        # open the wallet using Electrum CLI
        
        proc = subprocess.Popen([electrum_path, "-w", wallet_file, "listaddresses"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = proc.communicate()
        if proc.returncode != 0:
            print(f"Error listing addresses in wallet {wallet_file}: {error}")
            break

        # parse the output and get the list of addresses
        addresses = json.loads(output.decode())
        
        # for each address, get the balance and transaction count
        for address in addresses:
            # get the balance
            proc = subprocess.Popen([electrum_path, "-w", wallet_file, "getaddressbalance", address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = proc.communicate()
            if proc.returncode != 0:
                print(f"Error getting balance for address {address}: {error}")
                break

            # parse the output and get the balance and transaction count
            balance_data = json.loads(output.decode())
            balance = balance_data["confirmed"]

            # get the history
            proc = subprocess.Popen([electrum_path, "-w", wallet_file, "getaddresshistory", address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = proc.communicate()
            if proc.returncode != 0:
                print(f"Error getting history for address {address}: {error}")
                break

            # parse the output and get the balance and transaction count
            history_data = json.loads(output.decode())

            tx_count = len(history_data)

            # add the data to the list
            wallet_filename = wallet_file.split('\\')[-1] 
            data_list.append([wallet_filename, address, balance, tx_count])
            print(f'{wallet_filename},{address},{balance},{tx_count}')

# else:
#     print("This module has been imported.")
