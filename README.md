# self-driving
Self-driving Contest Source

#### 19.7.11 연븐성수's 낙서

<아이디어 및 생각해야 할 것들> 
- 현재 정상적으로 달리고 있는지 판단 
To_middle < self.half_road_limit 

- 복구할때 고려 상황들 
  - sensing_info.moving_angle : 도로방향에서 얼마나 정렬이 되어 있는지 
  - sensing_info.to_middle : 중간으로 부터 얼마나 떨어져있는지 
  - 전체 도로폭

- 스피드가 빠를수록 꺾는 각도는 커져야 한다. 
  - Moving_angle -90 ~ + 90
  - Steering=  +1 ~  -1 
  - Speed가 가중치 

- 이미 피할 수 있는 상황인지 판단

- 양 옆 박는 상황에 대한 판단 

#### 19.7.16 연븐's 낙서 
> 자율주행 소스에서 참고할만한 것들 정리

1. 샘플 <s, a, r, s'>을 리플레이 메모리에 저장
<pre><code>def append_sample(self, state, action, reward, next_state, done):
	self.memory.append((state, action, reward, next_state, done))
</code></pre>

2. 차량 상태 class
<pre><code>class CarState:
    def __init__(self, name):
        self.__name = name

    collided = False
    collision_distance = 0
    speed = 0
    to_middle = 0
    moving_angle = 0

    moving_forward = True
    lap_progress = 0
    track_forward_angles = []
    track_forward_obstacles = []
</code></pre>

3. 센싱 데이터 계산
<pre><code>sensing_info = self.calc_sensing_data(car_next_state, 	car_current_state, backed_car_state, self.way_points,
        check_point_index, progress)
</code></pre>
