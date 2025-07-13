from fuzz import generate_tests, TestSuite
import time

"""
ROTATE(number:uint, time:uint, angle:float) 
GOTO(number:uint, time:uint, x: float,y: float)
MOVE(number:uint, time:uint, dir:direction, dist:float) where dist > 0 
PIC(number:uint, time:uint, quality: image_quality,images: uint) where 0 < images <= 10
STORE(number:uint, time:uint, file:string, images: uint) where 0 < images <= 10
SEND(number:uint, time:uint, file: string)
COLLECT(number:uint, time:uint, file: string, sample: string)
SCRIPT(number:uint, time:uint, script: string, file: string)
"""

spec = """     
  rule time_increases:
    always any(time=t1?) => wnext any(time=t2?) =>  t2 >= t1 + 10

  rule numbers_consecutive:
    any(number=1) and
    always any(number=n1?) => wnext any(number=n2?) =>  n2 = n1 + 1
        
  rule rotation_range:   
    always ROTATE(angle=a?) => -90 <= a <= 90
    
  rule distance_range:
    always MOVE(distance=d?) => (d = 1 or d = 2 or d = 3)

  rule move_backwards:
    always [MOVE(dir=direction.backwards,distance=d?)] eventually <ROTATE(angle=a?)> a = 45/d

  rule goto_path:
    always GOTO(x=x1?,y=y1?) => 
      always GOTO(x=x2?,y=y2?) => 
        (x2 > x1 and y2 > y1)

  rule required_commands:
    eventually MOVE() and eventually PIC(quality=image_quality.high) and eventually COLLECT()
    # eventually MOVE() and eventually COLLECT(sample="soil") and count 1 PIC(quality=image_quality.high) 

  rule image_process_forward:
    always [PIC(quality=image_quality.high, images=i?)]
      eventually <STORE(file=f?, images=j?)>
        (
          f |- /\d\d\d\.img/ and
          0 < j <= i 
          and
          eventually SEND(file=f)
        )

    # f |- /\d\d\d\.img/ and

  rule image_process_backward:
    always [STORE(file=f?,images=j?)]
        prev ( 
          not once STORE(file=f) 
          and 
          (
            not STORE() since <PIC(images=i?, quality=image_quality.high)> i >= j
          )
        )
      
  rule run_script:    
    always [COLLECT(file=f?, sample=s?)] 
     next (
       not COLLECT()  
       until <SCRIPT(script = k?, file=f)> k = "run_" + s + ".py"
     )
    """

# Missing: or, sofar, ->, next n

if __name__ == '__main__':
    start_time = time.time()
    tests: TestSuite = generate_tests(spec=spec, test_suite_size=100, test_size=10)
    end_time = time.time()
    for test in tests:
        print(f'RESET SUT')
        for cmd in test:
            print(cmd)
    print(f'Execution time = {end_time - start_time} seconds.')

