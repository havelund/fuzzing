from fuzz import generate_tests, TestSuite, Options
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
    # always [MOVE(dir=direction.backwards,distance=d?)] eventually <ROTATE(angle=a?)> a = 45/d
    always [MOVE(dir=direction.backwards,distance=d?)] eventually <ROTATE(angle=a?)> ((d <= 1 and a = 45) or (d > 1 and a = 20))

  rule goto_path: # p6
    always GOTO(x=x1?,y=y1?) => 
      always GOTO(x=x2?,y=y2?) => 
        (x2 > x1 and y2 > y1)

  rule image_process_forward: # p7
    always [PIC(quality=image_quality.high, images=i?)]
      eventually <STORE(file=f?, images=j?)>
        (
          # f |- /\d\d\d\.img/ and
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
            not STORE() since <PIC(images=i?, quality=image_quality.high)> i >= j
          )
        )
      
  rule run_script: # p9   
    always [COLLECT(file=f?, sample=s?)] 
     next (
       not COLLECT()  
       until <SCRIPT(script = k?, file=f)>k = "run_" + s + ".py"
     )
     
  rule required_commands: # p10
    eventually MOVE() and eventually PIC(quality=image_quality.high) and eventually COLLECT()     
    """

spec = """     
  rule time_increases: # p1
    always [any(time=t1?)] wnext [any(time=t2?)] t2 >= t1 + 10

  rule numbers_consecutive: # p2
    any(number=1) and
    always [any(number=n1?)] wnext [any(number=n2?)] n2 = n1 + 1

  rule rotation_range: # p3  
    always [ROTATE(angle=a?)] -90 <= a <= 90

  rule distance_range: # p4
    always [MOVE(distance=d?)] (d = 1 or d = 2 or d = 3)

  rule move_backwards: # p5
    # always [MOVE(dir=direction.backwards,distance=d?)] eventually <ROTATE(angle=a?)> a = 45/d
    always [MOVE(dir=direction.backwards,distance=d?)] eventually <ROTATE(angle=a?)> ((d <= 1 and a = 45) or (d > 1 and a = 20))

  rule goto_path: # p6
    always [GOTO(x=x1?,y=y1?)] 
      always [GOTO(x=x2?,y=y2?)] 
        (x2 > x1 and y2 > y1)

  rule image_process_forward: # p7
    always [PIC(quality=image_quality.high, images=i?)]
      eventually <STORE(file=f?, images=j?)>
        (
          # f |- /\d\d\d\.img/ and
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
            not STORE() since <PIC(images=i?, quality=image_quality.high)> i >= j
          )
        )

  rule run_script: # p9   
    always [COLLECT(file=f?, sample=s?)] 
     next (
       not COLLECT()  
       until <SCRIPT(script = k?, file=f)>k = "run_" + s + ".py"
     )

  rule required_commands: # p10
    eventually MOVE() and eventually PIC(quality=image_quality.high) and eventually COLLECT()     
    """

if __name__ == '__main__':
    Options.PRINT_CONSTRAINTS = True
    tests: TestSuite = generate_tests(spec=spec, test_suite_size=1, test_size=10)

