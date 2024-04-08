import csv
import paramiko
import argparse
import os

def run_script_on_remote(username, password, ip_address, script_path):
    try:
        # Establish SSH connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip_address, username=username, password=password)

        # Transfer script file to remote machine
        sftp = ssh_client.open_sftp()
        sftp.put(script_path, '/tmp/script.sh')
        sftp.close()

        # Run script on remote machine
        stdin, stdout, stderr = ssh_client.exec_command('bash /tmp/script.sh')

        # Save output to file
        output_dir = os.path.join(ip_address, os.path.dirname(script_path))
        output_file_path = os.path.join(output_dir, f"Output.txt")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(output_file_path, 'w') as output_file:
            for line in stdout:
                output_file.write(line)
        
        print(f"Output saved to {output_file_path}")
        
        # Close SSH connection
        ssh_client.close()

    except paramiko.AuthenticationException:
        print(f"Failed to authenticate with {ip_address}. Check username and password.")
    except paramiko.SSHException as ssh_err:
        print(f"Unable to establish SSH connection to {ip_address}: {ssh_err}")
    except Exception as e:
        print(f"Error occurred while executing script on {ip_address}: {e}")

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

            run_script_on_remote(username, password, ip_address, script_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tool to run a script on multiple remote machines via SSH.")
    parser.add_argument("csv_file", help="Path to the CSV file containing username, password, and IP addresses.")
    parser.add_argument("script_path", help="Path to the script to be executed on remote machines.")
    args = parser.parse_args()

    main(args.csv_file, args.script_path)
