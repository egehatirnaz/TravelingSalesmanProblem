import math
def circle_line_segment_intersection(circle_center, circle_radius, pt1, pt2):
    A, B, C, r = pt1, pt2, circle_center, circle_radius

    # Each vector as a complex number.
    OA = complex(*A)
    OB = complex(*B)
    OC = complex(*C)

    # Now let's translate into a coordinate system where A is the origin
    AB = OB - OA
    AC = OC - OA

    # if either A or B is actually in the circle,  then mark it as a detection
    BC = OC - OB
    if abs(BC) < r or abs(AC) < r: return True

    # Project C onto the line to find P, the point on the line that is closest to the circle centre
    AB_normalized = AB / abs(AB)
    AP_distance = AC.real * AB_normalized.real + AC.imag * AB_normalized.imag  # dot product (scalar result)
    AP = AP_distance * AB_normalized  # actual position of P relative to A (vector result)

    # If AB intersects the circle, and neither A nor B itself is in the circle,
    # then P, the point on the extended line that is closest to the circle centre, must be...

    # (1) ...within the segment AB:
    AP_proportion = AP_distance / abs(AB)  # scalar value: how far along AB is P?
    in_segment = 0 <= AP_proportion <= 1

    # ...and (2) within the circle:
    CP = AP - AC
    in_circle = abs(CP) < r

    detected = in_circle and in_segment
    return detected


def storm_check(ax, ay, bx, by, cx, cy, cr):
    check = circle_line_segment_intersection((cx, cy), cr, (ax, ay), (bx, by))
    return check


def main():
    x1, y1 = -2.715083694, -5.788439845
    x2, y2 = 83.75028451, -54.67444337

    cx, cy, cr = 111.0127535, -73.07613868, 14.4428022
    #cx, cy, cr = 51.68174387, -23.05492725, 17.1440682

    # Tests
    print(storm_check(x1, y1, x2, y2, cx, cy, cr))  # True. (route between #1-#25 and hits storm of row 15)


if __name__ == '__main__':
    main()