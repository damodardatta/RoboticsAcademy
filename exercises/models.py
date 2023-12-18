"""
models.py
"""

import json
from django.db import models


StatusChoice = (
    ('ACTIVE', "ACTIVE"),
    ('INACTIVE', "INACTIVE"),
    ('PROTOTYPE', "PROTOTYPE")
)

VisualizationType = (
    ('none', "None"),
    ('console', "Console"),
    ('gazebo_gra', "Gazebo GRA"),
    ('gazebo_rae', "Gazebo RAE"),
    ('physic_gra', "Physic GRA"),
    ('physic_rae', "Physic RAE")
)

WorldType = (
    ('none', "None"),
    ('gazebo', "Gazebo"),
    ('drones', "Gazebo Drones"),
    ('physical', "Physical")
)

RosVersion = (
    ('ROS1', "ROS1"),
    ('ROS2', "ROS2")
)


class World(models.Model):
    """
    Modelo World para RoboticsCademy
    """
    name = models.CharField(max_length=100, blank=False, unique=True)
    launch_file_path = models.CharField(max_length=200, blank=False)
    ros_version = models.CharField(
        max_length=4, choices=RosVersion, default="none")
    visualization = models.CharField(
        max_length=50,
        choices=VisualizationType,
        default="none",
        blank=False
    )
    world = models.CharField(
        max_length=50,
        choices=WorldType,
        default="none",
        blank=False
    )

    def __str__(self):
        return str(self.name)

# Create your models here.


class Exercise(models.Model):
    """
    RoboticsCademy Exercise model
    """
    exercise_id = models.CharField(max_length=40, blank=False, unique=True)
    name = models.CharField(max_length=40, blank=False, unique=True)
    description = models.CharField(max_length=400, blank=False)
    tags = models.CharField(
        max_length=2000,
        default=json.dumps({'tags': ""})
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoice,
        default="ACTIVE"
    )
    worlds = models.ManyToManyField(World, default=None)
    template = models.CharField(max_length=200, blank=True, default="")

    def __str__(self):
        return str(self.name)

    @property
    def context(self):
        """
        Build and return context
        """
        configurations = []

        for world in self.worlds.all():
            config = {
                "name": world.name,
                "launch_file_path": world.launch_file_path,
                "ros_version": world.ros_version,
                "visualization": world.visualization,
                "world": world.world,
                "template": self.template,
                "exercise_id":self.exercise_id
            }
            configurations.append(config)

        context = {
            'exercise_base': "exercise_base_2_RA.html",
            'exercise_id': self.exercise_id,
            'exercise_config': configurations,
        }
        return context
