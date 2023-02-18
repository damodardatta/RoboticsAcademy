from __future__ import annotations

import os
import time
import traceback
from queue import Queue
from uuid import uuid4
from src.manager.vnc.docker_thread import DockerThread

from transitions import Machine

from src.ram_logging.log_manager import LogManager

from src.comms.consumer_message import ManagerConsumerMessageException
from src.libs.process_utils import get_class, get_class_from_file
from src.manager.application.robotics_python_application_interface import IRoboticsPythonApplication
from src.manager.launcher.launcher_engine import LauncherEngine
from src.manager.vnc.console_view import ConsoleView
from src.manager.vnc.gzb_view import GzbView
from src.manager.lint.linter import Lint


class Manager:
    states = [
        "idle",
        "connected",
        "ready",
        "running",
        "paused"
    ]

    transitions = [
        # Transitions for state idle
        {'trigger': 'connect', 'source': 'idle', 'dest': 'connected', },
        # Transitions for state connected
        {'trigger': 'launch', 'source': 'connected', 'dest': 'ready', 'before': 'on_launch'},
        # Transitions for state ready
        {'trigger': 'terminate', 'source': 'ready', 'dest': 'connected', 'before': 'on_terminate'},
        {'trigger': 'load', 'source': ['ready', 'running', 'paused'], 'dest': 'ready', 'before': 'load_code'},
        {'trigger': 'run', 'source': 'ready', 'dest': 'running', 'conditions': 'code_loaded', 'after': 'on_run'},
        # Transitions for state running
        {'trigger': 'stop', 'source': 'running', 'dest': 'ready'},
        {'trigger': 'pause', 'source': 'running', 'dest': 'paused', 'before': 'on_pause'},
        # Transitions for state paused
        {'trigger': 'resume', 'source': 'paused', 'dest': 'running', 'before': 'on_resume'},
        {'trigger': 'stop', 'source': 'paused', 'dest': 'ready'},
        # Global transitions
        {'trigger': 'reset', 'source': '*', 'dest': 'ready' ,'before': 'on_reset'}
    ]

    def __init__(self, host: str, port: int):
        self.__code_loaded = False
        self.exercise_id = None
        self.machine = Machine(model=self, states=Manager.states, transitions=Manager.transitions,
                               initial='idle', send_event=True, after_state_change=self.state_change)
        from src.comms.new_consumer import ManagerConsumer

        self.queue = Queue()

        # TODO: review, hardcoded values
        self.consumer = ManagerConsumer(host, port, self.queue)
        self.launcher = None
        self.application = None
        self.linter = None
        

    def state_change(self, event):
        LogManager.logger.info(f"State changed to {self.state}")
        if self.consumer is not None:
            self.consumer.send_message({'state': self.state}, command="state-changed")

    def update(self, data):
        LogManager.logger.debug(f"Sending update to client")
        if self.consumer is not None:
            self.consumer.send_message({'update': data}, command="update")

    def on_reset(self, event):
        cmd = "/opt/ros/noetic/bin/rosservice call gazebo/reset_world"
        rosservice_thread = DockerThread(cmd)
        rosservice_thread.call()


    def on_launch(self, event):
        """
        Transition executed on launch trigger activ
        """
        
        gzb_viewer = GzbView(":0", 5900, 6080)
        console_viewer = ConsoleView(":1", 5901, 1108)
        print('vnc started')
        time.sleep(2)
        console_viewer.start_console(1920, 1080)
        print("> Console started")

        def terminated_callback(name, code):
            # TODO: Prototype, review this callback
            LogManager.logger.info(f"Manager: Launcher {name} died with code {code}")
            if self.state != 'ready':
                self.terminate()

        configuration = event.kwargs.get('data', {})
     
       
        # generate exercise_folder environment variable
        self.exercise_id = configuration['exercise_id']
        os.environ["EXERCISE_FOLDER"] = f"{os.environ.get('EXERCISES_STATIC_FILES')}/{self.exercise_id}"
        self.linter = Lint(self.exercise_id)

        # Check if application and launchers configuration is missing
        # TODO: Maybe encapsulate configuration as a data class with validation?
        application_configuration = configuration.get('application', None)
        if application_configuration is None:
            raise Exception("Application configuration missing")

        # check if launchers configuration is missing
        launchers_configuration = configuration.get('launch', None)
        if launchers_configuration is None:
            raise Exception("Launch configuration missing")

        LogManager.logger.info(f"Launch transition started, configuration: {configuration}")

        # configuration['terminated_callback'] = terminated_callback
        self.launcher = LauncherEngine(**configuration)
        self.launcher.run()
        gzb_viewer.start_gzserver(configuration["launch"]["0"]["launch_file"])
        gzb_viewer.start_gzclient(configuration["launch"]["0"]["launch_file"], configuration['width'], configuration['height'])

       
        # TODO: launch application
        application_file = application_configuration['entry_point']
        params = application_configuration.get('params', None)
        application_module = os.path.expandvars(application_file)
        application_class = get_class_from_file(application_module, "Exercise")

        if not issubclass(application_class, IRoboticsPythonApplication):
            self.launcher.terminate()
            raise Exception("The application must be an instance of IRoboticsPythonApplication")

        params['update_callback'] = self.update
        self.application = application_class(**params)

        cmd = "/opt/ros/noetic/bin/rosservice call gazebo/pause_physics"
        rosservice_thread = DockerThread(cmd)
        rosservice_thread.call()
       
        
    def on_terminate(self, event):
        try:
            self.application.terminate()
            self.launcher.terminate()
        except Exception as e:
            LogManager.logger.exception(f"Exception terminating instance")
            print(traceback.format_exc())

    def on_enter_connected(self, event):
        LogManager.logger.info("Connect state entered")

    def on_run(self, event):
        cmd = "/opt/ros/noetic/bin/rosservice call gazebo/unpause_physics"
        rosservice_thread = DockerThread(cmd)
        rosservice_thread.call()
     

    def on_enter_ready(self, event):
        configuration = event.kwargs.get('data', {})
        LogManager.logger.info(f"Start state entered, configuration: {configuration}")

    def load_code(self, event):
        cmd = "/opt/ros/noetic/bin/rosservice call gazebo/pause_physics"
        rosservice_thread = DockerThread(cmd)
        rosservice_thread.call()
        
        try:
            LogManager.logger.info("Internal transition load_code executed")
            message_data = event.kwargs.get('data', {})
            errors = self.linter.evaluate_code(message_data['code'])
            if errors is "":
                self.application.load_code(message_data['code'])
                self.__code_loaded = True
            else:
                raise Exception
        except Exception as e:
            self.__code_loaded = False
        
        self.consumer.send_message({'linter': errors}, command="linter")
        

    def code_loaded(self, event):
        return self.__code_loaded

    def process_messsage(self, message):
        self.trigger(message.command, data=message.data or None)
        response = {"message": f"Exercise state changed to {self.state}"}
        self.consumer.send_message(message.response(response))

    def on_pause(self, msg):
        cmd = "/opt/ros/noetic/bin/rosservice call gazebo/pause_physics"
        rosservice_thread = DockerThread(cmd)
        rosservice_thread.call()

    def on_resume(self, msg):
        cmd = "/opt/ros/noetic/bin/rosservice call gazebo/unpause_physics"
        rosservice_thread = DockerThread(cmd)
        rosservice_thread.call()

    def start(self):
        """
        Starts the RAM
        RAM must be run in main thread to be able to handle signaling other processes, for instance ROS launcher.
        """
        LogManager.logger.info(f"Starting RAM consumer in {self.consumer.server}:{self.consumer.port}")
       
        self.consumer.start()
        # TODO: change loop end condition
        while True:
            message = None
            try:
                if self.queue.empty():
                    time.sleep(0.1)
                else:
                    message = self.queue.get()
                    self.process_messsage(message)
            except Exception as e:
                if message is not None:
                    ex = ManagerConsumerMessageException(id=message.id, message=str(e))
                else:
                    ex = ManagerConsumerMessageException(id=str(uuid4()), message=str(e))
                self.consumer.send_message(ex)
                LogManager.logger.error(e, exc_info=True)
                

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str, help="Host to listen to  (0.0.0.0 or all hosts)")
    parser.add_argument("port", type=int, help="Port to listen to")
    args = parser.parse_args()

    RAM = Manager(args.host, args.port)
    RAM.start()