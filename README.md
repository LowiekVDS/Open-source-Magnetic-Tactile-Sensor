### TL;DR

[Paper](https://arxiv.org/abs/2405.18582), also see [this repo](https://github.com/LowiekVDS/masters-thesis) for expanded design.

# Open-source Magnetic Tactile Sensing

<img align="right" width="200" src="https://github.com/LowiekVDS/Open-source-Magnetic-Tactile-Sensor/blob/main/img/collapsed.png">

This repo contains the design files for a magnetic tactile fingertip presented at the [ViTac workshop](https://shanluo.github.io/ViTacWorkshops/) at ICRA2024, you can read the paper [here](https://arxiv.org/abs/2405.18582).
The fingertip has four taxels in a 2-by-2 grid. We developed a calibration method to be used with a robotic arm with integrated F/T sensor. In the paper, the fingertip is mounted to (a gripper the arm and pushed against an external probe to collect calibration data. It is crucial that the mounting of the fingertip to the robot is rigid. We have noticed that this is not sufficiently the case when mounting the fingertip to a Robotiq 2F-85 gripper. A Schunk EGK-40 gave better results. 

This work was expanded upon by designing a 4-by-8 grid as well, together with a more reliable calibration method where the sensor is mounted to the table, see [this repo](https://github.com/LowiekVDS/masters-thesis).
