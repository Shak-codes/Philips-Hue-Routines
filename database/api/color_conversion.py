import math
import numpy

x1, y1 = 0.6915, 0.3038
x2, y2 = 0.17, 0.7
x3, y3 = 0.1532, 0.0475


def area(p1, p2, p3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    return abs((x1 * (y2 - y3) + x2 * (y3 - y1)
                + x3 * (y1 - y2)) / 2.0)


def point_in_triangle(point, triangle):
    """Returns True if the point is inside the triangle
    and returns False if it falls outside.
    - The argument *point* is a tuple with two elements
    containing the X,Y coordinates respectively.
    - The argument *triangle* is a tuple with three elements each
    element consisting of a tuple of X,Y coordinates.

    It works like this:
    Walk clockwise or counterclockwise around the triangle
    and project the point onto the segment we are crossing
    by using the dot product.
    Finally, check that the vector created is on the same side
    for each of the triangle's segments.
    """
    # Unpack arguments
    x, y = point
    ax, ay = triangle[0]
    bx, by = triangle[1]
    cx, cy = triangle[2]
    # Segment A to B
    side_1 = (x - bx) * (ay - by) - (ax - bx) * (y - by)
    # Segment B to C
    side_2 = (x - cx) * (by - cy) - (bx - cx) * (y - cy)
    # Segment C to A
    side_3 = (x - ax) * (cy - ay) - (cx - ax) * (y - ay)
    # All the signs must be positive or all negative
    return (side_1 < 0.0) == (side_2 < 0.0) == (side_3 < 0.0)


def closest_point(p, p1, p2):
    x, y = p
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2-x1, y2-y1
    det = dx*dx + dy*dy
    a = (dy*(y-y1)+dx*(x-x1))/det
    return x1+a*dx, y1+a*dy


def rgb_to_Yxy(r: int, g: int, b: int):
    red = r / 255
    green = g / 255
    blue = b / 255

    red = math.pow((red + 0.055) / 1.055,
                   2.4) if red > 0.04045 else red / 12.92
    green = math.pow((green + 0.055) / 1.055,
                     2.4) if red > 0.04045 else green / 12.92
    blue = math.pow((blue + 0.055) / 1.055,
                    2.4) if red > 0.04045 else blue / 12.92

    X = red * 0.4124 + green * 0.3576 + blue * 0.1805
    Y = red * 0.2126 + green * 0.7152 + blue * 0.0722
    Z = red * 0.0193 + green * 0.1192 + blue * 0.9505

    x = X / (X + Y + Z)
    y = Y / (X + Y + Z)

    if point_in_triangle((x, y), [(x1, y1), (x2, y2), (x3, y3)]):
        return Y, x, y

    closest_points = [closest_point((x, y), (x1, y1), (x2, y2)),
                      closest_point((x, y), (x2, y2), (x3, y3)),
                      closest_point((x, y), (x1, y1), (x3, y3))]
    closest_point_idx = numpy.argmin(closest_points)
    return Y, closest_points[closest_point_idx]
