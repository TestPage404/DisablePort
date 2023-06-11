import netmiko, os
from datetime import datetime
from pprint import pprint
import psycopg2

day = datetime.today().strftime('%A')
# day = 'Monday'
# day = 'Tuesday'
# day = 'Wednesday'
# day = 'Thursday'
# day = 'Friday'
# day = 'Saturday'
host = '127.0.0.1'
db_user = 'pgadmin'
db_pass = 'qwerty'
db_name = 'switches'

def append_to_sql(switch):
    host = {
    'device_type':'cisco_ios',
    'host':switch,
    'username':os.environ.get('CCIE_user'),
    'password':os.environ.get('CCIE_password'),
    'secret':os.environ.get('CCIE_password')
    }

    ssh = netmiko.Netmiko(**host)
    coma = ssh.send_command('show int', use_textfsm=True)
    ll = []
    for i in coma:
        interface, packets = i['interface'], i['input_packets']
        if '/' in interface:
            first_column_bd = ':'.join([switch.rstrip(), interface])
            second_column_bd = packets
            ll.append((first_column_bd,second_column_bd))
    return ll

def ConnectToDevice(switch):
    host = {
    'device_type':'cisco_ios',
    'host':switch,
    'username':os.environ.get('CCIE_user'),
    'password':os.environ.get('CCIE_password'),
    'secret':os.environ.get('CCIE_password')
    }

    ssh = netmiko.Netmiko(**host)

def db_insert(values):
    connection = psycopg2.connect(host=host, user=db_user, password=db_pass, database=db_name)
    connection.autocommit = True
    with connection.cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS switches(
            "switch:port" text PRIMARY KEY,
            Monday text,
            Tuesday text,
            Wednesday text,
            Thursday text,
            Friday text,
            Saturday text,
            Sunday text
        )""")
        cur.executemany("""INSERT INTO switches("switch:port",{}) VALUES(%s, %s)""".format(day), values)


def db_update(port, packets):
    connection = psycopg2.connect(host=host, user=db_user, password=db_pass, database=db_name)
    connection.autocommit = True
    with connection.cursor() as cur:
        query = 'UPDATE switches SET {} = %s WHERE "switch:port" = %s'.format(day)
        data = (packets, port)
        cur.execute(query, data)


def shutdown_port(switch):
    connection = psycopg2.connect(host='127.0.0.1', user=db_user, password=db_pass, database=db_name)
    connection.autocommit = True
    print(f"[+] Отключаю порты на коммутаторе {switch.rstrip()}...")
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM switches")
        request_data = cur.fetchall()
        host = {
            'device_type': 'cisco_ios',
            'host': switch,
            'username': os.environ.get('CCIE_user'),
            'password': os.environ.get('CCIE_password'),
            'secret': os.environ.get('CCIE_password')
        }

        ssh = netmiko.Netmiko(**host)
        ssh.enable()

        for swandport,mon,tue,wed,thur,fri,sut,sun in request_data:
            port = swandport.split(":")[1]
            commands = ['int '+port, 'shut', 'exit']
            if mon==tue==wed==thur==fri==sut==sun:
                coma = ssh.send_config_set(commands)
                print(f"Порт {port} отключен")



if __name__ == '__main__':
    file = 'd:\\switches.txt'
    with open(file) as f:
        for switch in f:
            print(f"[+] Заполняю SQL для коммутатора {switch.rstrip()}...")
            try:
                values = append_to_sql(switch)
                db_insert(values)
            except:
                values = append_to_sql(switch)
                for port, packets in values:
                    db_update(port, packets)
            shutdown_port(switch)

