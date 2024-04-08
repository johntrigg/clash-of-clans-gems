#!/bin/bash

# Function to install and enable SSH
install_and_enable_ssh() {
    package_manager="$1"
    ssh_service_name="$2"
    install_command="$3"
    enable_command="$4"
    start_command="$5"

    echo "Installing OpenSSH server..."
    $install_command

    echo "Enabling SSH service to start at boot..."
    $enable_command

    echo "Starting SSH service..."
    $start_command

    echo "SSH service installation and activation complete."
}

# Detecting the package manager and proceeding accordingly
if command -v apt > /dev/null; then
    # Debian/Ubuntu
    install_and_enable_ssh "apt" "ssh" "apt-get update && apt-get install -y openssh-server" "systemctl enable ssh" "systemctl start ssh"
elif command -v yum > /dev/null; then
    # CentOS (Older versions)
    install_and_enable_ssh "yum" "sshd" "yum -y install openssh-server" "chkconfig sshd on" "service sshd start"
elif command -v dnf > /dev/null; then
    # Fedora
    install_and_enable_ssh "dnf" "sshd" "dnf -y install openssh-server" "systemctl enable sshd" "systemctl start sshd"
elif command -v pacman > /dev/null; then
    # Arch Linux
    install_and_enable_ssh "pacman" "sshd" "pacman -Sy --noconfirm openssh" "systemctl enable sshd" "systemctl start sshd"
else
    echo "Unsupported Linux distribution. Exiting."
    exit 1
fi

# Additional check for systemctl or service command for service management
if command -v systemctl > /dev/null; then
    echo "systemctl available. SSH service managed via systemd."
else
    if command -v service > /dev/null; then
        echo "Fallback to 'service' for managing SSH service."
        # You might need to adjust the service start/enable commands for distributions
        # that do not have systemctl but this section provides a starting point.
    else
        echo "Neither systemctl nor service command is available. Manual intervention required."
        exit 1
    fi
fi
