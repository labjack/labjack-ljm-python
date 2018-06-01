"""
Demonstrates setting up stream-in with stream-out that continuously updates.

Streams in while streaming out arbitrary values. These arbitrary stream-out
values act on DAC0 to alternate between increasing the voltage from 0 to 2.5 and
decreasing from 5.0 to 2.5 on (approximately). Though these values are initially
generated during the call to create_out_context, the values could be
dynamically generated, read from a file, etc. To convert this example file into
a program to suit your needs, the primary things you need to do are:

    1. Edit the global setup variables in this file
    2. Define your own create_out_context function or equivalent
    3. Define your own process_stream_results function or equivalent

You may also need to configure AIN, etc.

"""
import sys

from labjack import ljm

import ljm_stream_util


# Setup

IN_NAMES = ["AIN0", "AIN1"]

"""
STREAM_OUTS = [
    {
        "target": str register name that stream-out values will be sent to,
        "buffer_num_bytes": int size in bytes for this stream-out buffer,

        "stream_out_index": int STREAM_OUT# offset. 0 would generate names like
            "STREAM_OUT0_BUFFER_STATUS", etc.

        "set_loop": int value to be written to STREAM_OUT#(0:3)_SET_LOOP
    },
    ...
]
"""
STREAM_OUTS = [
    {
        "target": "DAC0",
        "buffer_num_bytes": 512,
        "stream_out_index": 0,
        "set_loop": 2
    },
    {
        "target": "DAC1",
        "buffer_num_bytes": 512,
        "stream_out_index": 1,
        "set_loop": 3
    }
]

INITIAL_SCAN_RATE_HZ = 200
# Note: This program does not work well for large scan rates because
# the value loops will start looping before new value loops can be written.
# While testing on USB with 512 bytes in one stream-out buffer, 2000 Hz worked
# without stream-out buffer loop repeating.
# (Other machines may have different results.)
# Increasing the size of the buffer_num_bytes will increase the maximum speed.
# Using an Ethernet connection type will increase the maximum speed.

NUM_CYCLES = INITIAL_SCAN_RATE_HZ / 10
NUM_CYCLES_MIN = 10
if NUM_CYCLES < NUM_CYCLES_MIN:
    NUM_CYCLES = NUM_CYCLES_MIN


def print_register_value(handle, register_name):
    value = ljm.eReadName(handle, register_name)
    print("%s = %f" % (register_name, value))


def open_ljm_device(device_type, connection_type, identifier):
    try:
        handle = ljm.open(device_type, connection_type, identifier)
    except ljm.LJMError:
        print(
            "Error calling ljm.open(" +
            "device_type=" + str(device_type) + ", " +
            "connection_type=" + str(connection_type) + ", " +
            "identifier=" + identifier + ")"
        )
        raise

    return handle


def print_device_info(handle):
    info = ljm.getHandleInfo(handle)
    print(
        "Opened a LabJack with Device type: %i, Connection type: %i,\n"
        "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i\n" %
        (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5])
    )


def main(
    initial_scan_rate_hz=INITIAL_SCAN_RATE_HZ,
    in_names=IN_NAMES,
    stream_outs=STREAM_OUTS,
    num_cycles=NUM_CYCLES
):
    print("Beginning...")
    handle = open_ljm_device(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
    print_device_info(handle)

    print("Initializing stream out buffers...")
    out_contexts = []
    for stream_out in stream_outs:
        out_context = ljm_stream_util.create_out_context(stream_out)
        ljm_stream_util.initialize_stream_out(handle, out_context)
        out_contexts.append(out_context)

    print("")

    for out_context in out_contexts:
        print_register_value(handle, out_context["names"]["buffer_status"])

    for out_context in out_contexts:
        update_str = "Updating %(stream_out)s buffer whenever " \
            "%(buffer_status)s is greater or equal to " % out_context["names"]
        print(update_str + str(out_context["state_size"]))

    scans_per_read = int(min([context["state_size"] for context in out_contexts]))
    buffer_status_names = [out["names"]["buffer_status"] for out in out_contexts]
    try:
        scan_list = ljm_stream_util.create_scan_list(
            in_names=in_names,
            out_contexts=out_contexts
        )
        print("scan_list: " + str(scan_list))
        print("scans_per_read: " + str(scans_per_read))

        scan_rate = ljm.eStreamStart(handle, scans_per_read, len(scan_list),
                                     scan_list, initial_scan_rate_hz)
        print("\nStream started with a scan rate of %0.0f Hz." % scan_rate)
        print("\nPerforming %i buffer updates." % num_cycles)

        iteration = 0
        total_num_skipped_scans = 0
        while iteration < num_cycles:
            buffer_statuses = [0]
            infinity_preventer = 0
            while max(buffer_statuses) < out_context["state_size"]:
                buffer_statuses = ljm.eReadNames(
                    handle,
                    len(buffer_status_names),
                    buffer_status_names
                )
                infinity_preventer = infinity_preventer + 1
                if infinity_preventer > scan_rate:
                    raise ValueError(
                        "Buffer statuses don't appear to be updating:" +
                        str(buffer_status_names) + str(buffer_statuses)
                    )

            for out_context in out_contexts:
                ljm_stream_util.update_stream_out_buffer(handle, out_context)

            # ljm.eStreamRead will sleep until data has arrived
            stream_read = ljm.eStreamRead(handle)

            num_skipped_scans = ljm_stream_util.process_stream_results(
                iteration,
                stream_read,
                in_names,
                device_threshold=out_context["state_size"],
                ljm_threshold=out_context["state_size"]
            )
            total_num_skipped_scans += num_skipped_scans

            iteration = iteration + 1
    except ljm.LJMError:
        ljm_stream_util.prepare_for_exit(handle)
        raise
    except Exception:
        ljm_stream_util.prepare_for_exit(handle)
        raise

    ljm_stream_util.prepare_for_exit(handle)

    print("Total number of skipped scans: %d" % total_num_skipped_scans)


if __name__ == "__main__":
    main()
