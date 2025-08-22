import time

class Timer:
    timer_count = 0
    
    def __init__(self, seconds):
        self.seconds = seconds
        Timer.timer_count += 1
    
    def run(self):
        for i in range(self.seconds):
            time.sleep(1)
        print("타이머 종료!")

timer5 = Timer(5)
timer3 = Timer(3)

timer5.run()
timer3.run()

print(Timer.timer_count)