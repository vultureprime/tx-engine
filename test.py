start_id = 12345
end_id = 36890
step = 1000
import time
current_id = start_id
while current_id < end_id:
    s = current_id
    e = current_id + step
    if e // 10000 > s // 10000:
        e = ((e // 10000)*10000) - 1
    if e > end_id:
        e = end_id
    current_id = e + 1
    print(s,e,s//10000)
    time.sleep(1)

