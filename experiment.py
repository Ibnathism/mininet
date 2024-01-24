#!/usr/bin/env python

from sys import argv
import time
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.log import setLogLevel
import os

number_of_users = 10
number_of_files_per_user = 10
set_id = 2

class SingleSwitchTopo( Topo ):
    "Single switch connected to n hosts."
    def build( self, n=2):
        switch = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        for h in range(n):
            # Each host gets 50%/n of system CPU
            host = self.addHost('h%s' % (h), cpu=.5 / (n+1))
            self.addLink(host, switch, bw=100*8, delay='0ms', loss=0, use_htb=True)
        
        # self.addLink(switch, switch2, bw=60*8)
        # self.addLink(switch, switch2, bw=60*8, delay='5ms', loss=0.000001)
        self.addLink(switch, switch2, bw=60*8, delay='5ms', loss=0.00001)
        server = self.addHost('server', cpu=.5 / (n+1))
        self.addLink(server, switch2, bw=100*8, delay='0ms', loss=0, use_htb=True)

def get_file_size(file_path):
    """Get the size of a file in bytes."""
    try:
        return os.path.getsize(file_path)
    except OSError as e:
        print(f"Error accessing file {file_path}: {e}")
        return None

def get_all_file_sizes():
    base_path = 'saved_models/set' + str(set_id) + '/users/'

    user_file_sizes = {}

    for user in range(0, number_of_users):
        user_key = f'user{user}'
        user_file_sizes[user_key] = {}

        for file_num in range(0, number_of_files_per_user):
            if set_id == 1:
                file_path = f'{base_path}user{user}/u{user}_r{file_num}.pth'
            elif set_id == 2:
                file_path = f'{base_path}user{user}/u{user}_r{file_num}_compressed.pth'
            file_size = get_file_size(file_path)

            if file_size is not None:
                user_file_sizes[user_key][f'file{file_num}'] = file_size

    # print(user_file_sizes)
    return user_file_sizes

def check_completion_of_sending(file_id):
    all_file_sizes = get_all_file_sizes()
    # print(all_file_sizes['user0'][f'file{file_id}'])
    for user_id in range(0, number_of_users):
        user_file_size = all_file_sizes[f'user{user_id}'][f'file{file_id}']

        if set_id == 1:
            server_path = 'saved_models/set' + str(set_id) + '/server/user' + str(user_id) + '/u' + str(user_id) + '_r' + str(file_id) + '.pth'
        elif set_id == 2:
            server_path = 'saved_models/set' + str(set_id) + '/server/user' + str(user_id) + '/u' + str(user_id) + '_r' + str(file_id) + '_compressed.pth'
        size_of_file_in_server = get_file_size(server_path)

        if size_of_file_in_server != user_file_size:
            return False
    return True

def get_training_times():
    values_dict = {}
    with open('Results/training_times.txt', 'r') as file:
        for line in file:
            # Assuming each line is in the format "key:value"
            key, value = line.strip().split(':')
            values_dict[key] = value
    return values_dict   

def perfTest():
    "Create network and run simple performance test"
    topo = SingleSwitchTopo( n=10)
    net = Mininet( topo=topo, host=CPULimitedHost, link=TCLink, autoStaticArp=True )
    net.start()
    net.pingAll()

    server = net.get('server')
    server_IP = server.IP()
    port_counter = 0
    
    training_times = get_training_times()
    times = []
    for j in range (0, number_of_files_per_user): 
        for i in range(0, number_of_users):
            host = net.get('h' + str(i))
            port = 12345 + port_counter  
            
            if set_id == 1:
                server_cmd = 'nc -l -p ' + str(port) + ' > saved_models/set' + str(set_id) + '/server/user' + str(i) + '/u' + str(i) + '_r' + str(j) + '.pth &'
            elif set_id == 2:
                server_cmd = 'nc -l -p ' + str(port) + ' > saved_models/set' + str(set_id) + '/server/user' + str(i) + '/u' + str(i) + '_r' + str(j) + '_compressed.pth &'
            
            server.cmdPrint(server_cmd)

            if set_id == 1:
                transfer_cmd = 'nc ' + server_IP + ' ' + str(port) + ' < saved_models/set' + str(set_id) + '/users/user' + str(i) + '/u' + str(i) + '_r' + str(j) + '.pth &'
            elif set_id == 2:
                transfer_cmd = 'nc ' + server_IP + ' ' + str(port) + ' < saved_models/set' + str(set_id) + '/users/user' + str(i) + '/u' + str(i) + '_r' + str(j) + '_compressed.pth &'
            
            host.cmdPrint(transfer_cmd)

            port_counter = port_counter + 1
        
        transfer_time = 0
        while not check_completion_of_sending(file_id=j):
            # if transfer_time > 3:
            #     break
            transfer_time = transfer_time + 1
            time.sleep(1)
        
        # print(training_times[f'{j}'])
        total_time = round(float(training_times[f'{j}']), 6) + transfer_time
        print(f'Total time for sending file {j}: {total_time}')
        
        times.append(round(total_time, 6))

    # with open('Results/weight_files_w_o_delay_loss.txt', 'w') as file:
    #     for value in times:
    #         file.write(f"{value}\n")

    # with open('Results/weight_files_w_delay_and_smaller_loss.txt', 'w') as file:
    #     for value in times:
    #         file.write(f"{value}\n")
    
    with open('Results/weight_files_w_delay_and_larger_loss.txt', 'w') as file:
        for value in times:
            file.write(f"{value}\n")
    
    # with open('Results/model_files_w_delay_and_larger_loss.txt', 'w') as file:
    #     for value in times:
    #         file.write(f"{value}\n")

    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    perfTest()