
from src.fuzz.solver import *


def run(spec):
    test = generate_test_satisfying_formula(spec, end_time=5)
    print_test(test)


if __name__ == '__main__':
    spec1 = """
    #rule p1: always FUZZ_CMD_UNSIGNED_ARG_1(fuzz_cmd1_arg_1=x?) => 
    #              eventually FUZZ_CMD_MIXED_5(fuzz_cmd5_arg_5=x) 

    #rule p2: eventually FUZZ_CMD_UNSIGNED_ARG_1()

    #rule q1: always FUZZ_CMD_UNSIGNED_ARG_1(fuzz_cmd1_arg_1=x1?) => 1 <= x1 <= 3

    #rule p3: eventually FUZZ_CMD_STRING_3()
    
    #rule p4: eventually FUZZ_CMD_FLOAT_4()
    
    #rule p5_1: count (9,9) FUZZ_CMD_ENUM_2(fuzz_cmd2_arg_1="fuzz_val_2") 

    # -----------------------------------------------------------------------------
    #rule p5_2: count (2,2) (FUZZ_CMD_ENUM_2(fuzz_cmd2_arg_1=x?) => x="fuzz_val_2")
    rule k1: eventually FUZZ_CMD_ENUM_2(fuzz_cmd2_arg_1="fuzz_val_2")
    rule k2: count (2,2) FUZZ_CMD_ENUM_2(fuzz_cmd2_arg_1=x?) => x="fuzz_val_2"
    # -----------------------------------------------------------------------------

    #rule p5_3: always FUZZ_CMD_ENUM_2(fuzz_cmd2_arg_1=x?) => x="fuzz_val_2"

    #rule p6: count(5,6) FUZZ_CMD_ENUM_2()
       
    #rule p7: always 
    #           (FUZZ_CMD_UNSIGNED_ARG_1(fuzz_cmd1_arg_1=x?) => (x < 796))

    #rule p8: next next next next FUZZ_CMD_UNSIGNED_ARG_1()
    
    #rule p9: always FUZZ_CMD_UNSIGNED_ARG_1(fuzz_cmd1_arg_1=x?) => 
    #           sofar FUZZ_CMD_UNSIGNED_ARG_1(fuzz_cmd1_arg_1=x)
    
    # rule k1: eventually FUZZ_CMD_STRING_3()
    # rule k2: always FUZZ_CMD_STRING_3(fuzz_cmd3_arg_1=x?) => x = "jpl"
    # rule k3: count (2,2) FUZZ_CMD_STRING_3(fuzz_cmd3_arg_1=x?) => x = "jpl"
    
    # rule l1: eventually FUZZ_CMD_UNSIGNED_ARG_1()
    # rule l2: count (2,2) FUZZ_CMD_UNSIGNED_ARG_1(fuzz_cmd1_arg_1=x?) => x = 777
    """

    spec2 = """    
    rule q0: eventually FUZZ_CMD_ENUM_2()
    
    rule q1: always 
      FUZZ_CMD_UNSIGNED_ARG_1(
        fuzz_cmd1_arg_1=x1?,
        fuzz_cmd1_arg_2=x2?,
        fuzz_cmd1_arg_3=x3?) =>
          (1 <= x1 <= 800 and 1 <= x2 <= 200 and 1 <= x3 <= 10)
                
    rule q2: always 
      FUZZ_CMD_ENUM_2(
        fuzz_cmd2_arg_1=x1?,
        fuzz_cmd2_arg_2=x2?) => 
          (
            (x1 = "fuzz_val_1" or x1 = "fuzz_val_2" or x1 = "fuzz_val_3")
            and
            (x2 = "DISABLE" or x2 = "ENABLE")
          )        
    """

    spec = spec1

    for _ in range(100):
        run(spec)

'''
<command_dictionary>
        <header mission_name="FUZZ_MISSION" schema_version="1.0" version="10.1.0.2">
        </header>
        <enum_definitions>
          <enum_table name="fuzz_enum_def1">
            <values>
              <enum numeric="0" symbol="fuzz_val_1"/>
              <enum numeric="1" symbol="fuzz_val_2"/>
              <enum numeric="2" symbol="fuzz_val_3"/>
            </values>
          </enum_table>
          <enum_table name="enable_disable">
            <values>
              <enum numeric="0" symbol="DISABLE"/>
              <enum numeric="1" symbol="ENABLE"/>
            </values>
          </enum_table>
          </enum_definitions>
        <command_definitions>


          <fsw_command class="FSW" opcode="0x0003" stem="FUZZ_CMD_STRING_3">
              <var_string_arg max_bit_length="1024" name="fuzz_cmd3_arg_1" prefix_bit_length="8">
                <description>First argument for fuzzing command 3</description>
              </var_string_arg>

              <var_string_arg max_bit_length="1024" name="fuzz_cmd3_arg_2" prefix_bit_length="8">
                <description>First argument for fuzzing command 3</description>
              </var_string_arg>
          </fsw_command>

          <fsw_command class="FSW" opcode="0x0004" stem="FUZZ_CMD_FLOAT_4">
            <arguments>
              <float_arg bit_length="64" name="fuzz_cmd4_arg_1" units="None">
                <range_of_values>
                  <include max="1" min="-1"/>
                </range_of_values>
                <description>First argument for fuzzing command 4</description>
              </float_arg>
              <float_arg bit_length="64" name="fuzz_cmd4_arg_2" units="None">
                <range_of_values>
                  <include max="1" min="-1"/>
                </range_of_values>
                <description>Second argument for fuzzing command 4</description>
              </float_arg>
              <float_arg bit_length="64" name="fuzz_cmd4_arg_3" units="None">
                <range_of_values>
                  <include max="1" min="-1"/>
                </range_of_values>
                <description>Third argument for fuzzing command 4</description>
              </float_arg>
            </arguments>
            <description>Fuzzing command 4 with floats as arguments.</description>
          </fsw_command>
          <fsw_command class="FSW" opcode="0x0005" stem="FUZZ_CMD_MIXED_5">
            <arguments>
              <enum_arg bit_length="8" enum_name="fuzz_enum_def1" name="fuzz_cmd5_arg_1">
                <description>First argument for fuzzing command 5.</description>
              </enum_arg>
              <enum_arg bit_length="8" enum_name="enable_disable" name="fuzz_cmd5_arg_2">
                <description>Second argument for fuzzing command 5.</description>
              </enum_arg>
              <float_arg bit_length="32" name="fuzz_cmd5_arg_3" units="radian/s">
                <range_of_values>
                  <include max="2" min="-2"/>
                </range_of_values>
                <description>Third argument for fuzzing command 5.</description>
              </float_arg>
              <float_arg bit_length="32" name="fuzz_cmd5_arg_4" units="radian/s">
                <range_of_values>
                  <include max="2" min="-2"/>
                </range_of_values>
                <description>Fourth argument for fuzzing command 5.</description>
              </float_arg>
              <unsigned_arg bit_length="32" name="fuzz_cmd5_arg_5" units="ETR/ticks">
                <description>Fifth argument for fuzzing command 5.</description>
              </unsigned_arg>
            </arguments>
            <description>Fuzzing command 5 with a mixture of different types as arguments</description>
            <completion>Once the command has been sent.</completion>
          </fsw_command>
        </command_definitions>
      </command_dictionary>
'''