import telnetlib
import json
import hashlib
import binascii

def address_to_script_hash(address):
    # convert address to bytes, stripping any prefix
    address_bytes = binascii.unhexlify(address.encode())[1:]
    # hash the address bytes using SHA256
    hash_bytes = hashlib.sha256(address_bytes).digest()
    # hash the result again using RIPEMD160
    ripe_hash_bytes = hashlib.new('ripemd160', hash_bytes).digest()
    # convert the result to a reversed hex string
    script_hash = binascii.hexlify(ripe_hash_bytes[::-1]).decode()
    return script_hash


# Define the server address and port
host = "192.168.0.105"
port = 50001

# Define the request data as a string
request_data = {
    "id": "1",
    "method": "server.features",
    "params": ["bc1qhrhcny3tfagmd7eyugumuuduzssz92xugyn8s24w3k0xh5n7xkdq9ap7m2"]
}
request_data_str = json.dumps(request_data)

# Connect to the server
tn = telnetlib.Telnet(host, port)

# Send the request data
tn.write(request_data_str.encode('ascii') + b"\n")

# Read the response data
response_data_str = tn.read_until(b"\n")

# Print the response data
print(response_data_str.decode('ascii'))

# Close the connection
tn.close()

