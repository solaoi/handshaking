"""
coding: utf-8
"""

import subprocess
import sys
import threading
from time import sleep

import pigpio
from websocket_server import WebsocketServer

MOTOR_PIN = 4
MOTOR_DEFAULT_POSITION = 650
MOTOR_MOVED_POSITION = 1650

INITIAL_PIN = 14
SECOND_PIN = 15
LAST_PIN = 17

pi = None
socketServer = None
last_used_pin = 0
is_motor_moved = False


def set_motor_position(position):
    """
    モーターの位置を指定の位置へ
    """
    pi.set_servo_pulsewidth(MOTOR_PIN, position)


def play_sound_with(action):
    """
    アクションに応じて音を再生する
    """
    if action == 'correct':
        subprocess.run(['mpg321', 'assets/sound/button_true.mp3'], check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return True
    if action == 'fault':
        subprocess.run(['mpg321', 'assets/sound/button_false.mp3'], check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return True
    if action == 'end-game':
        subprocess.run(['mpg321', 'assets/sound/end_game.mp3'], check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return True

    raise ValueError


def is_end_game(gpio):
    """
    ゲームクリアかどうか
    """
    return last_used_pin == LAST_PIN and gpio == SECOND_PIN and is_motor_moved


def is_correct_action(gpio):
    """
    タッチごとに正解かどうか
    """
    return is_initial_touch(gpio) or is_ordered_touch(gpio)


def is_initial_touch(gpio):
    """
    初回タッチかどうか
    """
    return gpio == INITIAL_PIN and gpio != last_used_pin


def is_ordered_touch(gpio):
    """
    順番通りのタッチかどうか
    """
    return gpio - last_used_pin == 1


def sensor_touched(gpio, level, tick):
    """
    センサータッチ時の処理
    """
    global pi
    global last_used_pin
    global is_motor_moved

    print(gpio, level, tick)

    if is_correct_action(gpio):
        socketServer.send_message_to_all("good")

        if gpio == SECOND_PIN:
            set_motor_position(MOTOR_MOVED_POSITION)
            is_motor_moved = True

        play_sound_with('correct')
        last_used_pin = gpio

        return True

    if is_end_game(gpio):
        socketServer.send_message_to_all("excellent")
        play_sound_with('end-game')
        last_used_pin = 0
        set_motor_position(MOTOR_DEFAULT_POSITION)
        is_motor_moved = False

        sleep(5)
        socketServer.send_message_to_all("reset")

        return True

    socketServer.send_message_to_all("bad")
    play_sound_with('fault')
    last_used_pin = 0

    if is_motor_moved:
        set_motor_position(MOTOR_DEFAULT_POSITION)
        is_motor_moved = False

    sleep(2)
    socketServer.send_message_to_all("reset")

    return True


class Websocket(threading.Thread):
    def __init__(self, port, host, servers):
        super(Websocket, self).__init__()
        self.setDaemon(True)
        self.port = port
        self.host = host
        self.servers = servers

    def run(self):
        server = WebsocketServer(self.port, self.host)
        self.servers.append(server)
        server.run_forever()


def main():
    """
    main処理
    """
    global pi
    global socketServer
    pi = pigpio.pi()

    set_motor_position(MOTOR_DEFAULT_POSITION)

    for pin in range(INITIAL_PIN, LAST_PIN + 1):
        pi.set_mode(pin, pigpio.INPUT)
        pi.set_pull_up_down(pin, pigpio.PUD_UP)

    for pin in range(INITIAL_PIN, LAST_PIN + 1):
        pi.callback(pin, pigpio.FALLING_EDGE, sensor_touched)

    websocket_server = Websocket(55555, '127.0.0.1', servers=[])
    websocket_server.start()

    # WebSocketサーバーが起動するまでwait
    while not websocket_server.servers:
        sleep(1)

    socketServer = websocket_server.servers[0]

    while True:
        try:
            sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == '__main__':
    main()
