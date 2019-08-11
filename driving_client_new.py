from drive_controller import DrivingController
from datetime import datetime, timedelta
import logging
import math

logging.basicConfig(filename='{}.log'.format(datetime.now().strftime('%Y-%m-%d-%H-%M')), level=logging.DEBUG)


class DrivingClient(DrivingController):
    def __init__(self):
        # =========================================================== #
        #  Area for member variables =============================== #
        # =========================================================== #
        # Editing area starts from here
        #
        self.is_debug = False
        self.collision_flag = False
        self.collision_time = 0
        self.moving_backward = False
        self.moving_backward_time = 0
        #
        #         # Editing area ends
        #         # ==========================================================#
        super().__init__()
        self.speed_list = []
        # 도로 범위 할당
        track_range = int((self.half_road_limit - 1.25) * 2 / 3)
        self.track_range = track_range if track_range % 2 != 0 else track_range - 1
        # 이전 도로 번호 할당
        self.previous_track_number = int(self.track_range / 2) + 1

    def control_driving(self, car_controls, sensing_info):
        # =========================================================== #
        # Area for writing code about driving rule ================= #
        # =========================================================== #
        # Editing area starts from here
        #

        logging.debug("=========================================================")
        logging.debug("to middle: {}".format(sensing_info.to_middle))

        logging.debug("collided: {}".format(sensing_info.collided))
        logging.debug("car speed: {} km/h".format(sensing_info.speed))

        logging.debug("is moving forward: {}".format(sensing_info.moving_forward))
        logging.debug("moving angle: {}".format(sensing_info.moving_angle))
        logging.debug("lap_progress: {}".format(sensing_info.lap_progress))

        logging.debug("track_forward_angles: {}".format(sensing_info.track_forward_angles))
        logging.debug("track_forward_obstacles: {}".format(sensing_info.track_forward_obstacles))
        logging.debug("opponent_cars_info: {}".format(sensing_info.opponent_cars_info))
        logging.debug("=========================================================")

        ###########################################################################

        self.speed_list.append(sensing_info.speed)
        self.speed_list = self.speed_list[1:] if len(self.speed_list) > 10 else self.speed_list

        # 충돌 상황인지 판단
        if not self.collision_flag:
            if sensing_info.collided \
                    and len(list(speed for speed in self.speed_list[-10:] if abs(speed) < 1)) > 9:
                self.collision_flag = True
                self.collision_time = datetime.now()

        # 충돌했을 경우 - 1초간 후진 / 방향 체크
        if self.collision_flag:
            if self.collision_time + timedelta(milliseconds = 2000) > datetime.now():
                car_controls.throttle = -0.5
            else:
                # 1초 후 탈출 / 방향 체크 (정상 후진 중인지 판단)
                if sensing_info.moving_forward:
                    self.moving_backward = True
                    self.moving_backward_time = datetime.now()
                self.collision_flag = False

        # 역주행 상황 판단
        if not self.collision_flag and not self.moving_backward:
            if not sensing_info.moving_forward and sensing_info.speed > 0:
                self.moving_backward = True
                self.moving_backward_time = datetime.now()

        # 역주행 하고 있을 경우
        if not self.collision_flag and self.moving_backward:
            if self.moving_backward_time + timedelta(milliseconds = 1000) > datetime.now():
                # 역주행 벗어나기
                car_controls.steering = 1 if car_controls.steering > 0 else -1
                car_controls.throttle = 0.3
            else:
                car_controls.steering = 1 if car_controls.steering < 0 else -1
                car_controls.throttle = 0.3
                if sensing_info.speed > 0:
                    self.moving_backward = False
                else:
                    self.moving_backward_time = datetime.now()

        # 탈출 / 일반적 상황
        if not self.collision_flag and not self.moving_backward:
            # 핸들 값 할당
            car_controls.steering = calculate_steering(self, sensing_info)
            # 속도 조절
            car_controls.throttle = 1 if sensing_info.speed < get_limit_speed(sensing_info) else 0

        logging.debug("steering:{}, throttle:{}, brake:{}".format(car_controls.steering, car_controls.throttle,
                                                                  car_controls.brake))

        #
        # Editing area ends
        # ==========================================================#
        return car_controls

    # ============================
    # If you have NOT changed the <settings.json> file
    # ===> player_name = ""
    #
    # If you changed the <settings.json> file
    # ===> player_name = "My car name" (specified in the json file)  ex) Car1
    # ============================
    def set_player_name(self):
        player_name = ""
        return player_name


def calculate_steering(self, sensing_info):
    # 도로 번호에 맞는 중앙값 선택
    track_number = select_track_number(self, sensing_info)
    to_middle = (track_number - (int(self.track_range / 2) + 1)) * self.track_range * 0.8
    # 현재 중앙값에 맞는 핸들값 할당
    middle = -(sensing_info.to_middle + to_middle) / (self.track_range * self.track_range)
    # 현재 도로 각도에 맞는 핸들값 할당
    angle = -(sensing_info.moving_angle - sensing_info.track_forward_angles[0]) / 45
    return middle + angle


def select_track_number(self, sensing_info):
    # 이전 도로 번호 할당
    track_number = self.previous_track_number
    # 중앙 도로 번호 할당
    middle_number = int(self.track_range / 2) + 1
    # 장애물이 있는 도로 번호 확인
    if len(sensing_info.track_forward_obstacles) > 0:
        disable_track_number_list = get_disable_track_number_list(self, sensing_info, middle_number)
        if len(disable_track_number_list) > 0:
            if self.previous_track_number in disable_track_number_list:
                mark = 1 if sensing_info.track_forward_angles[0] < 0 else -1
                for index in range(1, middle_number):
                    mark_plus = self.previous_track_number + (mark * index)
                    mark_minus = self.previous_track_number - (mark * index)
                    if mark_plus not in disable_track_number_list and 0 < mark_plus <= self.track_range:
                        track_number = self.previous_track_number + (mark * index)
                        break
                    elif mark_minus not in disable_track_number_list and 0 < mark_minus <= self.track_range:
                        track_number = self.previous_track_number - (mark * index)
                        break
        print("disable_track_number_list : {}".format(disable_track_number_list))
    else:
        if sensing_info.track_forward_angles[0] < -10 and track_number + 1 < self.track_range:
            track_number += 1
        elif sensing_info.track_forward_angles[0] > 10 and track_number - 1 > 1:
            track_number -= 1
        elif abs(sensing_info.track_forward_angles[0]) < 10:
            if sensing_info.track_forward_angles[0] < 0 and track_number - 1 > 1:
                track_number -= 1
            elif sensing_info.track_forward_angles[0] > 0 and track_number + 1 < self.track_range:
                track_number += 1
    print("previous_track_number : {}".format(self.previous_track_number))
    print("track_number : {}".format(track_number))
    # 현재 도로 번호 저장
    self.previous_track_number = track_number
    return track_number


def get_disable_track_number_list(self, sensing_info, middle_number):
    disable_track_number_list = []
    # 장애물 + 상대편 차량을 obstacle로 간주
    obstacle = sensing_info.track_forward_obstacles + sensing_info.opponent_cars_info
    obstacle = sorted(obstacle, key=lambda obs: obs['dist'])
    for obstacle in obstacle:
        if obstacle['dist'] < max(sensing_info.speed * 5 / 18 * 1.5, 30):
            for index in range(middle_number):
                if abs(obstacle['to_middle']) - 1.5 < 1.5 + (3 * index):
                    if obstacle['to_middle'] > 0:
                        if (middle_number - index) not in disable_track_number_list:
                            disable_track_number_list.append(middle_number - index)
                        break
                    else:
                        if (middle_number + index) not in disable_track_number_list:
                            disable_track_number_list.append(middle_number + index)
                        break
            for index in range(middle_number):
                if abs(obstacle['to_middle']) + 1.5 < 1.5 + (3 * index):
                    if obstacle['to_middle'] > 0:
                        if (middle_number - index) not in disable_track_number_list:
                            disable_track_number_list.append(middle_number - index)
                        break
                    else:
                        if (middle_number + index) not in disable_track_number_list:
                            disable_track_number_list.append(middle_number + index)
                        break
        else:
            break
    if self.track_range == len(disable_track_number_list):
        del disable_track_number_list[len(disable_track_number_list) - 1]
    return disable_track_number_list


def get_limit_speed(sensing_info):
    max_val = 0
    for val in sensing_info.track_forward_angles:
        if max_val < abs(val):
            max_val = abs(val)
    speed = max(120 * math.pow(math.e, -0.01 * max_val), 80)
    return speed


if __name__ == '__main__':
    client = DrivingClient()
    client.run()
