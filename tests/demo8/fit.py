from fuzz import verify_test

spec = """
    rule at_least_one_turn_and_send_and_two_moves:
      eventually TURN() and eventually SEND() and count 2 MOVE() 

    rule move_stop:
      always MOVE(number=n?) => eventually STOP(number=n)

    rule stop_move:
      always STOP(number=n?) => prev !STOP(number=n) since MOVE(number=n)

    rule limit_turn_degree:
      always TURN(angle=a?) => -10 <= a <= 10

    rule send_preceded_by_pic:
      always SEND(message=m?,images=i?) => 
          once PIC(images=j?, message=m, quality=image_quality.high) &> j >= i

    rule time_increases:
      always any(time=t1?) => wnext any(time=t2?) =>  t1 + 10 < t2      
    """

test = [
    {'name': 'MOVE', 'time': 2, 'number': 79, 'distance': 20, 'speed': 7.328534570408251, 'message': 'trWBEHUPgR'},
    {'name': 'PIC', 'time': 27, 'number': 74, 'images': 10, 'quality': 'high', 'message': '222.img'},
    {'name': 'STOP', 'time': 38, 'number': 79, 'message': 'ZQWsNa28Op'},
    {'name': 'SEND', 'time': 49, 'number': 10, 'images': 7, 'message': '222.img'},
    {'name': 'MOVE', 'time': 60, 'number': 76, 'distance': 97, 'speed': 3.4806259783535682, 'message': 'w87ZA4ClyI'},
    {'name': 'STOP', 'time': 71, 'number': 76, 'message': '5Er2pB8U29'},
    {'name': 'PIC', 'time': 124, 'number': 7, 'images': 3, 'quality': 'low', 'message': 'dZqjDycEYt'},
    {'name': 'LOG', 'time': 584, 'number': 36, 'message': 'fnOwHLV1Gw'},
    {'name': 'LOG', 'time': 595, 'number': 96, 'message': '81IH6O7Xwi'},
    {'name': 'TURN', 'time': 606, 'number': 92, 'angle': -2.0, 'message': 'HBXeRphg3h'}
]

if __name__ == '__main__':
    result = verify_test(test, spec)
    print(result)
