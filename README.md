# python-uleds

A simple library to interact with the Userspace LED subsystem in Linux.

## Setup

In order to use this library you will need to have the `uleds` module installed and loaded by running:

    # modprobe uleds

or by loading `uleds` on boot:

    # echo uleds > /etc/modules-load.d/uleds.conf

If you wish to create and read `uleds` devices as a regular user it is recommended to install the [99-uleds.rules](/99-uleds.rules) file and add yourself to the `uleds` group (create it if it doesn't exist already).

    # groupadd uleds
    # usermod -G uleds -a <username>
    # cp 99-uleds.rules /etc/udev/rules.d/
    # udevadm trigger

Note however that while you will be able to create/read `uleds` devices as a non-root user you will not be able to get and set the trigger event for the device without being root or changing the permissions of the corresponding `/sys/class/led/<device>/trigger` file.

## Example Usage

    import uleds

    # device name, max brightness
    s = uleds.uleds_user_dev(b"mydevice::myled", 255)
    l = uleds.uled(s)

    print(f"current brightness: {l.get()}")

    l.close()

