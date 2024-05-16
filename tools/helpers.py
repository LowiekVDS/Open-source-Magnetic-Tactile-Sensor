import numpy as np

def get_square_corners(a, b, c, width_x, width_y, tool_width):
    c1 = (a[0] - c[0]) * (a[0] - b[0]) + (a[1] - c[1]) * (a[1] - b[1])
    c2 = (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])
    t = c1 / c2
    
    corner1 = [a[0] + (b[0] - a[0])*t, a[1] + t * (b[1] - a[1])]
    
    dx1 = a[0] - corner1[0]
    dy1 = a[1] - corner1[1]
    norm = np.sqrt(dx1**2 + dy1**2)
    dx1 /= norm
    dy1 /= norm
    
    dx2 = c[0] - corner1[0]
    dy2 = c[1] - corner1[1]
    norm = np.sqrt(dx2**2 + dy2**2)
    dx2 /= norm
    dy2 /= norm
    
    # Correct corners for tool width
    corner1[0] += dx2 * tool_width
    corner1[1] += dy1 * tool_width
    
    corner2 = [corner1[0] + dx1 * width_x, corner1[1] + dy1 * width_y]
    corner3 = [corner1[0] + (dx1 + dx2) * width_x, corner1[1] + (dy1 + dy2) * width_y]    
    corner4 = [corner1[0] + dx2 * width_x, corner1[1] + dy2 * width_y]
  
    return np.array([corner4, corner1, corner2, corner3]), ((dx1, dy1), (dx2, dy2))
  
def calculate_grid_on_square(corners, offset, grid_size, pitch):

    # Calculate the direction of the sides
    dx_horiz, dy_horiz = corners[1] - corners[0]
    dx_vert, dy_vert = corners[3] - corners[0]

    # Morm dx, dy by pitch
    norm = np.sqrt(dx_horiz**2 + dy_horiz**2) / pitch
    dx_horiz /= norm
    dy_horiz /= norm
    norm = np.sqrt(dx_vert**2 + dy_vert**2) / pitch
    dx_vert /= norm
    dy_vert /= norm
    
    # Start point is just an offset from the first corner
    start_point = corners[0] + np.array([(dx_horiz + dx_vert) / pitch * offset[0], (dy_horiz + dy_vert) / pitch * offset[1]])
    
    grid = np.zeros((grid_size[1], grid_size[0], 2))
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            grid[j, i] = start_point + np.array([i * dx_horiz + j * dx_vert, i * dy_horiz + j * dy_vert])
    
    return grid

def rpy2rv(roll,pitch,yaw):
  
  alpha = yaw
  beta = pitch
  gamma = roll
  
  ca = np.cos(alpha)
  cb = np.cos(beta)
  cg = np.cos(gamma)
  sa = np.sin(alpha)
  sb = np.sin(beta)
  sg = np.sin(gamma)
  
  r11 = ca*cb
  r12 = ca*sb*sg-sa*cg
  r13 = ca*sb*cg+sa*sg
  r21 = sa*cb
  r22 = sa*sb*sg+ca*cg
  r23 = sa*sb*cg-ca*sg
  r31 = -sb
  r32 = cb*sg
  r33 = cb*cg
  
  theta = np.arccos((r11+r22+r33-1)/2)
  sth = np.sin(theta)
  kx = (r32-r23)/(2*sth)
  ky = (r13-r31)/(2*sth)
  kz = (r21-r12)/(2*sth)
  
  rv = np.zeros(3)
  rv[0] = theta*kx
  rv[1] = theta*ky
  rv[2] = theta*kz
  
  return rv

