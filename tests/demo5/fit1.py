
"""
Script using the fuzz library, requiring a newer version of Python, e.g. 3.11.
It stores the generated test in the file `fuzz_testsuite.json`.
"""

from fuzz import generate_tests

spec = """
    rule entry_gate:
      always DDM_ENABLE_DWN_PB_ENTRY_GATE(
        dwn_framing_packet_buffer=b?,
        dwn_framing_pb_entry_gate_enable_disable="DISABLE") =>
           once DDM_ENABLE_DWN_PB_ENTRY_GATE(
             dwn_framing_packet_buffer=b,
             dwn_framing_pb_entry_gate_enable_disable="ENABLE")


    rule entry_gate_must:
      eventually DDM_ENABLE_DWN_PB_ENTRY_GATE(dwn_framing_pb_entry_gate_enable_disable="DISABLE")
    """

if __name__ == '__main__':
    generate_tests(spec=spec, test_suite_size=5, test_size=10)
