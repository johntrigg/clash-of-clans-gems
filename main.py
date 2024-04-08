import csv
import paramiko
import argparse
import os
from paramiko import ssh_exception

def run_script_on_remote(username, password, ip_address, id_rsa_path, script_path):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Trying to SSH into host {ip_address} as user {username} using password authentication.")
        ssh_client.connect(ip_address, username=username, password=password)
        print(f"Password authentication successful. Transferring and executing script {os.path.basename(script_path)}.")
        transfer_and_execute_script(ssh_client, script_path, ip_address)
    except paramiko.AuthenticationException:
        print(f"Password authentication failed for {ip_address}. Trying SSH key authentication with key {id_rsa_path}.")
        try:
            ssh_client.connect(ip_address, username=username, key_filename=id_rsa_path)
            print(f"SSH key authentication successful. Transferring and executing script {os.path.basename(script_path)}.")
            transfer_and_execute_script(ssh_client, script_path, ip_address)
        except Exception as e:
            print(f"Error occurred while executing script on {ip_address} with SSH key authentication: {e}")
    except ssh_exception.NoValidConnectionsError as e:
        print(f"Unable to connect to {ip_address}: {e}")
    except paramiko.SSHException as ssh_err:
        print(f"SSH exception for {ip_address}: {ssh_err}")
    except Exception as e:
        print(f"General error occurred for {ip_address}: {e}")
    finally:
        # Ensure the connection is closed in case of failure
        ssh_client.close()

def transfer_and_execute_script(ssh_client, script_path, ip_address):
    # Transfer script file to remote machine
    sftp = ssh_client.open_sftp()
    sftp.put(script_path, '/tmp/script.sh')
    sftp.close()
    print(f"Script {os.path.basename(script_path)} transferred to {ip_address}. Executing...")

    # Execute the script on the remote machine
    stdin, stdout, stderr = ssh_client.exec_command('bash /tmp/script.sh')

    # Output handling
    print(f"Execution output for {ip_address}:")
    for line in stdout:
        print(line.strip())

def main(csv_file, script_path):
    # Check if the script file exists
    if not os.path.exists(script_path):
        print(f"Script file {script_path} does not exist.")
        return

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            username = row['username']
            password = row['password']
            ip_address = row['ip_address']
            id_rsa_path = row['id_rsa']

            # Adjust id_rsa_path to be an absolute path if necessary
            if not os.path.isabs(id_rsa_path):
                id_rsa_path = os.path.join(os.getcwd(), id_rsa_path)

            print(f"\nProcessing host {ip_address}...")
            # Run the script on the remote machine
            run_script_on_remote(username, password, ip_address, id_rsa_path, script_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tool to run a script on multiple remote machines via SSH.")
    parser.add_argument("csv_file", help="Path to the CSV file containing username, password, id_rsa path, and IP addresses.")
    parser.add_argument("script_path", help="Path to the script to be executed on remote machines.")
    args = parser.parse_args()

    main(args.csv_file, args.script_path)
