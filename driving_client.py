from drive_controller import DrivingController
from datetime import datetime
import logging

# 제한 속도
SPEED_LIMIT = 70

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
        # Editing area ends
        # ==========================================================#
        super().__init__()

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

        # 1. 박았는지 상태 체크
        # 1-1. 장애물에 박았을 때
        if is_collided(self, sensing_info):
            car_controls.steering = -1 * avoid_obstacles(self, sensing_info)
            car_controls.throttle = -1
        # 1-2. 도로 밖 팬스에 박았을 때
        else:
            # 2. 피해야할 대상이 있는지 확인
            # 2-1. 피해야할 장애물이 있는지 확인
            if is_avoid_obstacles(sensing_info):
                car_controls.steering = avoid_obstacles(self, sensing_info)
            # 2-2. 피해야할 상대 자동차가 있는지 확인

            # 3. 직선, 코너 주행 확인
            else:
                speed = max(sensing_info.speed, 50)
                angle = -(sensing_info.moving_angle - sensing_info.track_forward_angles[0]) / speed
                middle = -sensing_info.to_middle / (speed / 5)

                # 각 앵글값 및 미들값으로 구한 핸들값 중 더 큰 값을 선택
                car_controls.steering = angle if abs(angle) > abs(middle) else middle

            # 4. 상대 차량이 있다면 추월 가능한지

            # 제한 속도 이상이면 악셀값 조정
            car_controls.throttle = 0 if sensing_info.speed > SPEED_LIMIT else 1
            car_controls.brake = 0

        logging.debug("steering:{}, throttle:{}, brake:{}".format(car_controls.steering, car_controls.throttle, car_controls.brake))

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


# 1-1. 장애물에 박았을 때
def is_collided(self, sensing_info):
    if len(sensing_info.track_forward_obstacles) > 0:
        if self.collision_flag:
            if sensing_info.track_forward_obstacles[0]['dist'] < 10 and sensing_info.speed < 10:
                return True
        if sensing_info.collided:
            self.collision_flag = True
            return True
    self.collision_flag = False
    return False


# 피해야할 장애물이 있는지 확인
def is_avoid_obstacles(sensing_info):
    # 전방에 장애물이 하나이상 있는지 확인
    if len(sensing_info.track_forward_obstacles) > 0:
        # 가장 가까운 장애물과의 거리 확인
        if 5 < sensing_info.track_forward_obstacles[0]['dist'] < sensing_info.speed * 0.4:
            # 피하지 않아도 되는지 확인
            if abs(sensing_info.track_forward_obstacles[0]['to_middle'] - sensing_info.to_middle) > 2.5:
                return False
            return True
    return False


# 기본적으로 장애물의 반대로 이동, 중간에 위치할 경우 왼쪽 or 오른쪽 구석으로 이동
def avoid_obstacles(self, sensing_info):
    steering = -sensing_info.track_forward_obstacles[0]['to_middle'] / 25
    if abs(sensing_info.track_forward_obstacles[0]['to_middle']) < 2.5:
        steering = (sensing_info.to_middle - (self.half_road_limit / 3)) / 10
    return steering


if __name__ == '__main__':
    client = DrivingClient()
    client.run()
