#!/bin/sh -e

sudo chmod +x /home/pi/oasis-grow/scripts/setup_env.sh
source /home/pi/oasis-grow/scripts/setup_env.sh
sudo chmod +x /home/pi/oasis-grow/scripts/setup_config.sh
source /home/pi/oasis-grow/scripts/setup_config.sh
sudo chmod +x /home/pi/oasis-grow/scripts/setup_network.sh
source /home/pi/oasis-grow/scripts/setup_network.sh

while getopts ":b" opt; do
    case $opt in
        b)
            echo "Adding controller bootloader..."
            sudo chmod +x /home/pi/oasis-grow/scripts/setup_bootloader.sh
            source /home/pi/oasis-grow/scripts/setup_bootloader.sh
            
            echo "Optimizing boot time..."
            sudo chmod +x /home/pi/oasis-grow/scripts/optimize_boot.sh
            source /home/pi/oasis-grow/scripts/optimize_boot.sh -no_bt        
            
            ;;
        \?)
            echo "Invalid option: -$OPTARG"
            ;;
    esac
done

echo "Returning to WiFi mode..."
sudo cp /etc/dhcpcd_WiFi.conf /etc/dhcpcd.conf
sudo cp /etc/dnsmasq_WiFi.conf /etc/dnsmasq.conf
sudo systemctl disable hostapd
sudo systemctl reboot
