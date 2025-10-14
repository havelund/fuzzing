from fuzz import generate_tests, TestSuite, Options
import time

"""
ROTATE(number:uint, time:uint, angle:float) 
GOTO(number:uint, time:uint, x: float,y: float)
MOVE(number:uint, time:uint, dir:uint, dist:float) where dir in {0,1} & dist > 0 
PIC(number:uint, time:uint, quality: uint,images: uint) where quality in {0,1,2} & 0 < images <= 10
STORE(number:uint, time:uint, file:uint, images: uint) where file in {0..100} & 0 < images <= 10
SEND(number:uint, time:uint, file: uint) where file in {0..100}
COLLECT(number:uint, time:uint, file: uint, sample: uint) where file in {0..100} & sample in {0..5}
SCRIPT(number:uint, time:uint, script: uint, file: uint) where script in {0..105} & file in {0..100}
"""

spec = """     
  rule time_increases: # p1
    always any(time=t1?) => wnext any(time=t2?) =>  t2 >= t1 + 10

  rule numbers_consecutive: # p2
    any(number=1) and
    always any(number=n1?) => wnext any(number=n2?) =>  n2 = n1 + 1
        
  rule rotation_range: # p3  
    always ROTATE(angle=a?) => -90 <= a <= 90
    
  rule distance_range: # p4
    always MOVE(distance=d?) => (d = 1 or d = 2 or d = 3)

  rule move_backwards: # p5
    # always [MOVE(dir=0,distance=d?)] eventually <ROTATE(angle=a?)> a = 45/d
    always [MOVE(dir=0,distance=d?)] eventually <ROTATE(angle=a?)> ((d <= 1 and a = 45) or (d > 1 and a = 20))

  rule goto_path: # p6
    always GOTO(x=x1?,y=y1?) => 
      always GOTO(x=x2?,y=y2?) => 
        (x2 > x1 and y2 > y1)

  rule image_process_forward: # p7
    always [PIC(quality=2, images=i?)]
      eventually <STORE(file=f?, images=j?)>
        (
          0 < j <= i 
          and
          eventually SEND(file=f)
        )

  rule image_process_backward: # p8
    always [STORE(file=f?,images=j?)]
        prev ( 
          not once STORE(file=f) 
          and 
          (
            not STORE() since <PIC(images=i?, quality=2)> i >= j
          )
        )
      
  rule run_script: # p9   
    always [COLLECT(file=f?, sample=s?)] 
     next (
       not COLLECT()  
       until <SCRIPT(script = k?, file=f)> k = 100 + s
     )
     
  rule required_commands: # p10
    eventually MOVE() and eventually PIC(quality=2) and eventually COLLECT()     
    """

if __name__ == '__main__':
    Options.PRINT_CONSTRAINTS = False
    tests: TestSuite = generate_tests(spec=spec, test_suite_size=3, test_size=300)

