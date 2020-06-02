from zheye import zheye
z = zheye()
positions = z.Recognize('zhihu_image/a.gif')
last_position = []
if len(positions) == 2:
    # 如果第一个元素的x坐标大于第二哥元素的x坐标，则第二个元素是第一个倒立文字
    if positions[0][1] > positions[1][1]:
        # 所以列表里放文字的时候返过来放，先放第二个元素的xy，再放第一个元素的xy,后面的是x，前面的是y
        last_position.append([positions[1][1], positions[1][0]])
        last_position.append([positions[0][1], positions[0][0]])
    else:
        last_position.append([positions[0][1], positions[0][0]])
        last_position.append([positions[1][1], positions[1][0]])
else:
    last_position.append([positions[0][1], positions[0][0]])
print(last_position)
