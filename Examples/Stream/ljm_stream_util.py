
from labjack import ljm


def convert_name_to_int_type(name):
    return ljm.nameToAddress(name)[1]


def convert_name_to_out_buffer_type_str(target_name):
    OUT_BUFFER_TYPE_STRINGS = {
        ljm.constants.UINT16: "U16",
        ljm.constants.UINT32: "U32",
        # Note that there is no STREAM_OUT#(0:3)_BUFFER_I32
        ljm.constants.FLOAT32: "F32"
    }
    int_type = convert_name_to_int_type(target_name)
    return OUT_BUFFER_TYPE_STRINGS[int_type]


def convert_name_to_address(name):
    return ljm.nameToAddress(name)[0]


def convert_names_to_addresses(names, length_limit=None):
    """Convert a list of names to a list of addresses using LJM.

    @para names: Names to be converted to addresses.
    @type names: iterable over str
    @para length_limit: Limit the number of names to read from the name array
        also limit the size of the returned addresses.
    @type length_limit: int
    @return: The given names converted to addresses.
    @rtype: iterable over str
    """
    length = len(names)
    if length_limit:
        length = length_limit

    addresses_and_types = ljm.namesToAddresses(length, names)

    # ljm.namesToAddresses returns a tuple of a list of addresses and a list of
    # types. The list of addresses is indexed at 0 of that tuple.
    return addresses_and_types[0]


def create_scan_list(in_names=[], out_contexts=[]):
    """Creates a list of integer addresses from lists of in and out names."""
    in_addresses = []
    out_addresses = []

    if len(out_contexts) > 4:
        raise ValueError("The T7 only has 4 stream-out buffers")

    for out_context in out_contexts:
        stream_out_name = out_context["names"]["stream_out"]
        stream_out_address = convert_name_to_address(stream_out_name)
        out_addresses.append(stream_out_address)

    if in_names:
        in_addresses = convert_names_to_addresses(in_names)

    return in_addresses + out_addresses


def generate_state(start, diff, state_size, state_name):
    """Generates a dict that contains a state_name and a list of values."""
    values = []
    increment = float(1) / state_size
    for iteration in range(int(state_size)):
        # Get a value between start + diff
        sample = start + diff * increment * iteration
        values.append(sample)

    return {
        "state_name": state_name,
        "values": values
    }


def create_out_context(stream_out):
    """Create an object wich describes some stream-out buffer states.

    Create dict which will look something like this:
    out_context = {
        "current_index": int tracking which is the current state,
        "states": [
            {
                "state_name": str describing this state,
                "values": iterable over float values
            },
            ...
        ],
        "state_size": int describing how big each state's "values" list is,
        "target_type_str": str used to generate this dict's "names" list,
        "target": str name of the register to update during stream-out,
        "buffer_num_bytes": int number of bytes of this stream-out buffer,
        "stream_out_index": int number of this stream-out,
        "set_loop": int number to be written to to STREAM_OUT#(0:3)_SET_LOOP,
        "names": dict of STREAM_OUT# register names. For example, if
            "stream_out_index" is 0 and "target_type_str" is "F32", this would be
        {
            "stream_out": "STREAM_OUT0",
            "target": "STREAM_OUT0_TARGET",
            "buffer_size": "STREAM_OUT0_BUFFER_SIZE",
            "loop_size": "STREAM_OUT0_LOOP_SIZE",
            "set_loop": "STREAM_OUT0_SET_LOOP",
            "buffer_status": "STREAM_OUT0_BUFFER_STATUS",
            "enable": "STREAM_OUT0_ENABLE",
            "buffer": "STREAM_OUT0_BUFFER_F32"
        }
    }
    """
    BYTES_PER_VALUE = 2
    out_buffer_num_values = stream_out["buffer_num_bytes"] / BYTES_PER_VALUE

    # The size of all the states in out_context. This must be half of the
    # out buffer or less. (Otherwise, values in a given loop would be getting
    # overwritten during a call to update_stream_out_buffer.)
    state_size = out_buffer_num_values / 2

    target_type = convert_name_to_out_buffer_type_str(stream_out["target"])
    out_context = {
        "current_index": 0,
        "states": [],
        "state_size": state_size,
        "target_type_str": target_type
    }
    out_context.update(stream_out)

    out_context["names"] = create_stream_out_names(out_context)

    out_context["states"].append(
        generate_state(
            0.0,
            2.5,
            state_size,
            "increase from 0.0 to 2.5"
        )
    )
    out_context["states"].append(
        generate_state(
            5.0,
            -2.5,
            state_size,
            "decrease from 5.0 to 2.5"
        )
    )

    return out_context


def create_stream_out_names(out_context):
    return {
        "stream_out":
            "STREAM_OUT%(stream_out_index)d" % out_context,

        "target":
            "STREAM_OUT%(stream_out_index)d_TARGET" % out_context,

        "buffer_size":
            "STREAM_OUT%(stream_out_index)d_BUFFER_SIZE" % out_context,

        "loop_size":
            "STREAM_OUT%(stream_out_index)d_LOOP_SIZE" % out_context,

        "set_loop":
            "STREAM_OUT%(stream_out_index)d_SET_LOOP" % out_context,

        "buffer_status":
            "STREAM_OUT%(stream_out_index)d_BUFFER_STATUS" % out_context,

        "enable":
            "STREAM_OUT%(stream_out_index)d_ENABLE" % out_context,

        "buffer":
            "STREAM_OUT%(stream_out_index)d_BUFFER_%(target_type_str)s" % out_context
    }


def update_stream_out_buffer(handle, out_context):
    # Write values to the stream-out buffer. Note that once a set of values have
    # been written to the stream out buffer (STREAM_OUT0_BUFFER_F32, for
    # example) and STREAM_OUT#_SET_LOOP has been set, that set of values will
    # continue to be output in order and will not be interrupted until their
    # "loop" is complete. Only once that set of values have been output in their
    # entirety will the next set of values that have been set using
    # STREAM_OUT#_SET_LOOP start being used.

    out_names = out_context["names"]

    ljm.eWriteName(handle, out_names["loop_size"], out_context["state_size"])

    state_index = out_context["current_index"]
    error_address = -1
    current_state = out_context["states"][state_index]
    values = current_state["values"]

    info = ljm.getHandleInfo(handle)
    max_bytes = info[5]
    SINGLE_ARRAY_SEND_MAX_BYTES = 520
    if max_bytes > SINGLE_ARRAY_SEND_MAX_BYTES:
        max_bytes = SINGLE_ARRAY_SEND_MAX_BYTES

    NUM_HEADER_BYTES = 12
    NUM_BYTES_PER_F32 = 4
    max_samples = int((max_bytes - NUM_HEADER_BYTES) / NUM_BYTES_PER_F32)

    start = 0
    while start < len(values):
        num_samples = len(values) - start
        if num_samples > max_samples:
            num_samples = max_samples
        end = start + num_samples
        write_values = values[start:end]

        ljm.eWriteNameArray(handle, out_names["buffer"], num_samples, write_values)

        start = start + num_samples

    ljm.eWriteName(handle, out_names["set_loop"], out_context["set_loop"])

    print("  Wrote " +
          out_context["names"]["stream_out"] +
          " state: " +
          current_state["state_name"]
          )

    # Increment the state and wrap it back to zero
    out_context["current_index"] = (state_index + 1) % len(out_context["states"])


def initialize_stream_out(handle, out_context):
    # Allocate memory on the T7 for the stream-out buffer
    out_address = convert_name_to_address(out_context["target"])
    names = out_context["names"]
    ljm.eWriteName(handle, names["target"], out_address)
    ljm.eWriteName(handle, names["buffer_size"], out_context["buffer_num_bytes"])
    ljm.eWriteName(handle, names["enable"], 1)

    update_stream_out_buffer(handle, out_context)


def process_stream_results(
    iteration,
    stream_read,
    in_names,
    device_threshold=0,
    ljm_threshold=0
):
    """Print ljm.eStreamRead results and count the number of skipped samples."""
    data = stream_read[0]
    device_num_backlog_scans = stream_read[1]
    ljm_num_backlog_scans = stream_read[2]
    num_addresses = len(in_names)
    num_scans = len(data) / num_addresses

    # Count the skipped samples which are indicated by -9999 values. Missed
    # samples occur after a device's stream buffer overflows and are
    # reported after auto-recover mode ends.
    num_skipped_samples = data.count(-9999.0)

    print("\neStreamRead %i" % iteration)
    result_strs = []
    for index in range(len(in_names)):
        result_strs.append("%s = %0.5f" % (in_names[index], data[index]))

    if result_strs:
        print("  1st scan out of %i: %s" % (num_scans, ", ".join(result_strs)))

    # This is a test to ensure that 2 in channels are synchronized
    # def print_if_not_equiv_floats(index, a, b, delta=0.01):
    #     diff = abs(a - b)
    #     if diff > delta:
    #         print("index: %d, a: %0.5f, b: %0.5f, diff: %0.5f, delta: %0.5f" % \
    #             (index, a, b, diff, delta)
    #         )

    # for index in range(0, len(data), 2):
    #     print_if_not_equiv_floats(index, data[index], data[index + 1])

    if num_skipped_samples:
        print(
            "  **** Samples skipped = %i (of %i) ****" %
            (num_skipped_samples, len(data))
        )

    status_strs = []
    if device_num_backlog_scans > device_threshold:
        status_strs.append("Device scan backlog = %i" % device_num_backlog_scans)
    if ljm_num_backlog_scans > ljm_threshold:
        status_strs.append("LJM scan backlog = %i" % ljm_num_backlog_scans)

    if status_strs:
        status_str = "  " + ",".join(status_strs)
        print(status_str)

    return num_skipped_samples


def prepare_for_exit(handle, stop_stream=True):
    if stop_stream:
        print("\nStopping Stream")
        try:
            ljm.eStreamStop(handle)
        except ljm.LJMError as exception:
            if exception.errorString != "STREAM_NOT_RUNNING":
                raise

    ljm.close(handle)
