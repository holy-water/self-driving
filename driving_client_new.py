from drive_controller import DrivingController
from datetime import datetime
import logging

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

        #
        #         # Editing area ends
        #         # ==========================================================#
        super().__init__()
        # 제한 속도 할당
        self.limit_speed = 100
        # 도로 범위 할당
        track_range = int((self.half_road_limit - 1.25) * 2 / 2.5)
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

        # 핸들 값 할당
        car_controls.steering = calculate_steering(self, sensing_info)
        # 속도 조절
        car_controls.throttle = 1 if sensing_info.speed < self.limit_speed else 0

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
    to_middle = (track_number - (int(self.track_range / 2) + 1)) * self.track_range * 0.6
    # 현재 중앙값에 맞는 핸들값 할당
    middle = -(sensing_info.to_middle + to_middle) / (self.track_range * self.track_range)
    # 현재 도로 각도에 맞는 핸들값 할당
    angle = -(sensing_info.moving_angle - sensing_info.track_forward_angles[0]) / 50
    # 코너에서 핸들값 가중치 할당
    angle_weight = calculate_angle_weight(sensing_info, angle)
    return middle + angle + angle_weight


def select_track_number(self, sensing_info):
    # 이전 도로 번호 할당
    track_number = self.previous_track_number
    # 중앙 도로 번호 할당
    middle_number = int(self.track_range / 2) + 1
    # 장애물이 있는 도로 번호 확인
    if len(sensing_info.track_forward_obstacles) > 0:
        disable_track_number_list = get_disable_track_number_list(sensing_info, middle_number)
        if len(disable_track_number_list) > 0:
            if self.previous_track_number in disable_track_number_list:
                mark = 1 if self.previous_track_number < middle_number else -1
                for index in range(1, middle_number):
                    if self.previous_track_number + (mark * index) not in disable_track_number_list:
                        track_number = self.previous_track_number + (mark * index)
                        break
                    elif self.previous_track_number - (mark * index) not in disable_track_number_list:
                        track_number = self.previous_track_number - (mark * index)
                        break
        print("disable_track_number_list : {}".format(disable_track_number_list))
    print("previous_track_number : {}".format(self.previous_track_number))
    print("track_number : {}".format(track_number))
    # 현재 도로 번호 저장
    self.previous_track_number = track_number
    return track_number


def get_disable_track_number_list(sensing_info, middle_number):
    disable_track_number_list = []
    for obstacle in sensing_info.track_forward_obstacles:
        if obstacle['dist'] < sensing_info.speed * 5 / 18 * 1.5:
            for index in range(middle_number):
                if abs(obstacle['to_middle']) == 0.04:
                    print("들어옴")
                if abs(obstacle['to_middle']) - 1 < 1.25 + (2.5 * index):
                    if abs(obstacle['to_middle']) == 0.04:
                        print("index -1: {}".format(index))
                    if obstacle['to_middle'] > 0:
                        disable_track_number_list.append(middle_number - index)
                        break
                    else:
                        disable_track_number_list.append(middle_number + index)
                        break
            for index in range(middle_number):
                if abs(obstacle['to_middle']) + 1 < 1.25 + (2.5 * index):
                    if abs(obstacle['to_middle']) == 0.04:
                        print("index +1: {}".format(index))
                    if obstacle['to_middle'] > 0:
                        disable_track_number_list.append(middle_number - index)
                        break
                    else:
                        disable_track_number_list.append(middle_number + index)
                        break
        else:
            break
    return disable_track_number_list


def calculate_angle_weight(sensing_info, angle):
    weight = 0
    for i in range(2):
        if abs(sensing_info.track_forward_angles[i]) > 23:
            weight = (angle * abs(sensing_info.track_forward_angles[i])) / 23
            if sensing_info.track_forward_angles[i] * angle < 0:
                weight *= -1
            break
    return weight


if __name__ == '__main__':
    client = DrivingClient()
    client.run()