
from z3 import *

# Define the Datatype for the timeline values
TimelineValue = Datatype('TimelineValue')
TimelineValue.declare('FUZZ_CMD_ENUM_2', ('arg', StringSort()))
TimelineValue.declare('OTHER_CMD')
TimelineValue = TimelineValue.create()


def create_solver(min_count, max_count, end_time):
    # Create a Z3 solver instance
    solver = Solver()

    # Define the timeline as a function from int to TimelineValue
    timeline = Function('timeline', IntSort(), TimelineValue)

    # Define the counts for the formula
    counts = [
        If(Or(
            Not(TimelineValue.is_FUZZ_CMD_ENUM_2(timeline(i))),
            TimelineValue.arg(timeline(i)) == StringVal("fuzz_val_2")), 1, 0)
        for i in range(end_time)
    ]

    # Compute the total count using Sum
    total_count = Sum(counts)

    # Add constraints for the total count to the solver
    solver.add(total_count >= min_count)
    solver.add(total_count <= max_count)
    solver.add(IntVal(2) + RealVal(3.0) < IntVal(6))

    return solver, timeline, total_count


def try_solver(solver, timeline, total_count, end_time):
    print("Testing solver...")
    # Print the constraints for debugging
    print(f"Total count formula: {total_count}")
    print(f"Constraints in solver: {solver}")

    # Check the satisfiability of the constraints
    if solver.check() == sat:
        print("SATISFIABLE")
        model = solver.model()
        for i in range(end_time):
            value = model.eval(timeline(i))
            print(f"timeline({i}) = {value}")
    else:
        raise ValueError('NOT SATISFIABLE')


def main():
    # Parameters
    min_count = 3
    max_count = 3
    end_time = 10

    # Create the solver and constraints
    solver, timeline, total_count = create_solver(min_count, max_count, end_time)

    # Optionally add some example assignments for testing
    # solver.add(timeline(0) == TimelineValue.FUZZ_CMD_ENUM_2(StringVal("fuzz_val_3")))
    # solver.add(timeline(1) == TimelineValue.OTHER_CMD)
    # solver.add(timeline(2) == TimelineValue.FUZZ_CMD_ENUM_2(StringVal("fuzz_val_3")))
    solver.add(timeline(3) == TimelineValue.FUZZ_CMD_ENUM_2(StringVal("fuzz_val_2")))
    # solver.add(timeline(4) == TimelineValue.OTHER_CMD)

    try_solver(solver, timeline, total_count, end_time)


if __name__ == "__main__":
    for _ in range(100):
        main()
