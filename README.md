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
