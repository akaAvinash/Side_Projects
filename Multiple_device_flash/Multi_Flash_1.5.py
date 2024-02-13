import subprocess
import os

def check_connected_devices():
    # Check for connected devices
    adb_devices_output = subprocess.check_output(["adb", "devices"]).decode("utf-8")
    connected_devices = [line.split('\t')[0] for line in adb_devices_output.splitlines()[1:] if line.strip()]
    return connected_devices

def separate_devices(connected_devices):
    # Separate devices into adb and fastboot modes
    adb_devices = []
    fastboot_devices = []

    for device in connected_devices:
        device_state_output = subprocess.check_output(["adb", "-s", device, "get-state"]).decode("utf-8").strip()
        if device_state_output == "device":
            adb_devices.append(device)
        elif device_state_output == "fastboot":
            fastboot_devices.append(device)

    return adb_devices, fastboot_devices

def flash_adb_devices(adb_devices):
    # Flash ADB devices
    for device in adb_devices:
        cwd = os.getcwd()
        terminal_command = f'gnome-terminal -- bash -c "cd {cwd} && {flash_file_name} --aserial {device} --fserial {device}; sleep 10; export ANDROID_SERIAL={device}; adb -s {device} wait-for-device; cd apps; adb -s {device} push *.vpkg /data/; exec bash"'
        subprocess.Popen(terminal_command, shell=True).wait()

def flash_fastboot_devices(fastboot_devices):
    # Flash fastboot devices with user input for serial numbers
    for idx, device in enumerate(fastboot_devices, start=1):
        cwd = os.getcwd()
        fastboot_serial = input(f"Enter the DSN (Device Serial Number) for Fastboot device {idx} ({device}): ")
        terminal_command = f'gnome-terminal -- bash -c "cd {cwd} && {flash_file_name} --fserial {fastboot_serial} && adb -s {fastboot_serial} push apps /data/; exec bash"'
        subprocess.Popen(terminal_command, shell=True).wait()

def main():
    connected_devices = check_connected_devices()

    if not connected_devices:
        print("No connected devices found.")
        exit()

    adb_devices, fastboot_devices = separate_devices(connected_devices)

    if not adb_devices and not fastboot_devices:
        print("No devices in either adb or fastboot mode found.")
        exit()

    print("Detected ADB devices:")
    for idx, device in enumerate(adb_devices, start=1):
        print(f"{idx}. {device}")

    print("\nDetected Fastboot devices:")
    for idx, device in enumerate(fastboot_devices, start=1):
        print(f"{idx}. {device}")

    flash_adb_devices(adb_devices)
    flash_fastboot_devices(fastboot_devices)

    print(f"Flashing {len(adb_devices)} ADB devices and {len(fastboot_devices)} fastboot devices in parallel.")

    input("Press Enter when flashing is complete...")

    # No need to push apps here, as it's done in the terminal sessions

    # Reassign DSN to ADB devices
    for device in adb_devices:
        device_state_output = subprocess.check_output(["adb", "-s", device, "get-state"]).decode("utf-8").strip()
        if device_state_output == "device":
            continue  # The device is already in ADB mode
        elif device_state_output == "offline":
            # You can reboot the device to get it back into ADB mode if needed
            subprocess.Popen(["adb", "-s", device, "reboot"]).wait()
            print(f"Rebooting {device} to get it back into ADB mode...")

    print("Finished reassigning DSN to ADB devices.")

if __name__ == "__main__":
    main()
