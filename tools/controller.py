import rtde_control, rtde_receive
import numpy as np

class CalibrationController:
  
  def __init__(self, rtde_r, rtde_c):
    self.rtde_r = rtde_r
    self.rtde_c = rtde_c
    self.transformation = np.identity(3)
    self.task_frame = np.zeros(6)
    
  def get_tcp_pose(self):
    pose = self.rtde_r.getActualTCPPose()
    return pose
  
  def get_tcp_force(self):
    force = self.rtde_r.getActualTCPForce()
    return force
  
  def get_sensor_force(self):
    force = self.get_tcp_force()
    force[0:3] = np.linalg.inv(self.transformation) @ force[0:3]
    
    for i in range(len(force)):
      force[i] *= -1
    
    return force
  
  def get_sensor_pose(self):
    # pose_tcp = transform @ pose_sensor
    pose = self.get_tcp_pose()
    pose[0:3] = np.linalg.inv(self.transformation) @ pose[0:3]
    return pose
    
  def set_transform(self, transform):
    """Sets transformation from the plane of the sensor to the robot base frame

       So: pose_tcp = transform @ pose_sensor
       
       Can be easily found by describing the basis vectors of the sensor frame in function of the TCP frame
    
       The transformation should be created such that the sensor top plane is normal to the negative z-axis
       So the vector from top plane to PCB should be positive Z
       
       The X axis should be sideways (so calibration points are possible along two sides)
       The Y axis should be the bottom/top direction (only calibration point on bottom = negative Y is possible) 

    Args:
        transform (_type_): _description_
    """
    self.transformation = transform
    
    rx = np.arctan2(transform[2,1], transform[2,2])
    ry = np.arctan2(-transform[2,0], np.sqrt(transform[2,1]**2 + transform[2,2]**2))
    rz = np.arctan2(transform[1,0], transform[0,0])
    
    self.task_frame = [0, 0, 0, rx, ry, rz]
    
  def force_mode(self, selection_vector_xyz, wrench_xyz, limits_xyz):
    
    selection_vector = np.pad(selection_vector_xyz, (0, 3))
    wrench = np.pad(wrench_xyz, (0, 3))
    limits = np.pad(limits_xyz, (0, 3))
    limits[3:6] = 0.1
    
    self.rtde_c.forceMode(self.task_frame, selection_vector, wrench, 2, limits)
    

  def find_contact_point(self, xyz, speed = 0.01):
    """
    Args:
      xyz: direction vector in sensor frame
    """
  
    # Go to tcp frame
    xyz_tcp = np.dot(self.transformation, xyz)
  
    # Normalize vector and then scale with speed    
    direction = xyz_tcp / np.linalg.norm(xyz_tcp) * speed
    direction = np.pad(direction, (0, 3))

    self.rtde_c.moveUntilContact(direction)
    
    return self.get_sensor_pose()

  def move_absolute(self, given_xyz, velocity = 0.1, acceleration = 0.5):
    """
    Args:
      xyz: absolute position vector, defined in sensor frame
    """
    
    xyz = given_xyz[0:3]

    # Transform to tcp
    xyz_tcp = np.dot(self.transformation, xyz)
    
    # Copy into a tcp pose
    tcp_pose_0 = self.get_tcp_pose()
    tcp_pose_1 = np.array(tcp_pose_0.copy())
    tcp_pose_1[0:3] = xyz_tcp
    
    if len(given_xyz) > 3:
      tcp_pose_1[3:6] = given_xyz[3:6]
  
    path = [list(tcp_pose_0), list(tcp_pose_1)]

    # Append speeds, accelerations and blends
    for p in path:
      p.append(velocity)
      p.append(acceleration) # acceleration
      p.append(0.0) # blend

    # Send a linear path with blending in between - (currently uses separate script)
    self.rtde_c.moveL(path)

    return self.get_sensor_pose()

  def move_relative(self, dxyz, velocity = 0.1, acceleration = 0.5):
    """
    Args:
      dxyz: relative vector defined in sensor frame
    """

    # dxyz is given in sensor frame, transform to tcp
    dxyz_tcp = np.dot(self.transformation, dxyz)
    tcp_pose_0 = self.get_tcp_pose()
    tcp_pose_1 = np.array(tcp_pose_0.copy())
    tcp_pose_1 += np.pad(dxyz_tcp, (0, 3))
  
    path = [list(tcp_pose_0), list(tcp_pose_1)]

    # Append speeds, accelerations and blends
    for p in path:
      p.append(velocity) # velocity
      p.append(acceleration) # acceleration
      p.append(0.0) # blend

    # Send a linear path with blending in between - (currently uses separate script)
    self.rtde_c.moveL(path)
    
    return self.get_sensor_pose()
