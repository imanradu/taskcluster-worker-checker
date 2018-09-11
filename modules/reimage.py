import paramiko
import os
import socket

data = {"username": "danut",
        "hostname": "192.168.118.200",
        "port": "65222",
        "password": "123"}

mdc2_range = list(range(21, 237))
mdc1_range = list(range(237, 473))

mdc1_command = "ls"
mdc2_command = "w"
reboot_command = "sudo reboot now"

mdc1_fqdn = "root@{}.test.releng.mdc1.mozilla.com"
mdc1_fqdn_no_root = "{}.test.releng.mdc1.mozilla.com"
mdc2_fqdn = "root@{}.test.releng.mdc2.mozilla.com"

rejh1 = "rejh1.srv.releng.mdc1.mozilla.com"
rejh2 = "rejh1.srv.releng.mdc2.mozilla.com"

host_keys = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))


def question_loop():
    with open("hosts.txt") as hosts:
            for host in hosts:
                if host:
                    helptxt = "Answer with 'y'/'n' for reimage, 'r' for reboot or 'e' to exit application\n"
                    reply = input("Reimage {}".format(host) + helptxt)

                    if reply[:1] == "y":
                        if int(host[-3:]) <= int(mdc2_range[-1]):
                            try:
                                ssh = paramiko.SSHClient()
                                ssh.load_system_host_keys()
                                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                ssh.connect(mdc1_fqdn.format(host.split("\n")[0]), key_filename="~/.ssh/id_rsa_mozilla.pem")
                                stdin, stdout, stderr = ssh.exec_command(mdc1_command)
                                print(stdout.read().decode())
                                ssh.close()
                            finally:
                                pass

                        else:
                            try:
                                ssh = paramiko.SSHClient()
                                ssh.load_system_host_keys()
                                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                ssh.connect(mdc2_fqdn.format(host.split("\n")[0]))
                                stdin, stdout, stderr = ssh.exec_command(mdc2_command)
                                print(stdout.read().decode())
                                ssh.close()
                            finally:
                                pass
                    elif reply[:1] == "n":
                        print("Skipping ".format(host))

                    elif reply[:1] == "r":
                        if int(host[-3:]) <= int(mdc2_range[-1]):
                            try:

                                hostkeytype = host_keys[mdc1_fqdn_no_root.format(host.split("\n")[0])].keys()[0]
                                hostkey = host_keys[mdc1_fqdn_no_root.format(host.split("\n")[0])][hostkeytype]
                                ssh = paramiko.SSHClient()
                                ssh.load_system_host_keys()
                                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                ssh.load_system_host_keys()
                                ssh.connect(hostkey, gss_host=socket.getfqdn(rejh1), gss_auth=True, gss_kex=True)
                                stdin, stdout, stderr = ssh.exec_command("{} '{}'".format(mdc1_fqdn.format(host.split("\n")[0]) ,reboot_command))
                                print(stdout.read().decode())
                                ssh.close()
                            finally:
                                pass

                        else:
                            try:
                                ssh = paramiko.SSHClient()
                                ssh.load_system_host_keys()
                                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                ssh.connect(mdc2_fqdn.format(host.split("\n")[0]))
                                stdin, stdout, stderr = ssh.exec_command(reboot_command)
                                print(stdout.read().decode())
                                ssh.close()
                            finally:
                                pass

                    elif reply[:1] == "e":
                        print("Exiting application.")
                        exit(0)
                else:
                    print("No more ")

if __name__ == "__main__":
    question_loop()
