import math

def point_iso(x, y, z, scale=1.5):
    cos30 = math.cos(math.radians(30))
    sin30 = math.sin(math.radians(30))

    px = (x - y) * cos30
    py = (x + y) * sin30 - z

    # Offset to center on screen
    return px * scale + 600, py * scale + 500

def draw_poly(points, color, stroke="none", stroke_width=0):
    pts_str = " ".join([f"{p[0]},{p[1]}" for p in points])
    return f'<polygon points="{pts_str}" fill="{color}" stroke="{stroke}" stroke-width="{stroke_width}"/>'

def draw_cube(x, y, z, dx, dy, dz, color_top, color_left, color_right):
    # Returns SVG polygons for a cube
    p1 = point_iso(x, y, z)
    p2 = point_iso(x+dx, y, z)
    p3 = point_iso(x+dx, y+dy, z)
    p4 = point_iso(x, y+dy, z)

    p5 = point_iso(x, y, z+dz)
    p6 = point_iso(x+dx, y, z+dz)
    p7 = point_iso(x+dx, y+dy, z+dz)
    p8 = point_iso(x, y+dy, z+dz)

    # Top face
    top = draw_poly([p5, p6, p7, p8], color_top)

    # Front-Left face: constant x=x+dx, y goes from y to y+dy
    front_left = draw_poly([p2, p3, p7, p6], color_left)

    # Front-Right face: constant y=y+dy, x goes from x to x+dx
    front_right = draw_poly([p4, p3, p7, p8], color_right)

    return top + "\n" + front_left + "\n" + front_right

def main():
    svg = []
    svg.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1000" width="1200" height="1000">')

    # Background
    svg.append('<rect width="1200" height="1000" fill="#fafafa"/>')

    # Room size: x=450, y=500, z=250
    room_x, room_y, room_z = 450, 500, 250

    # Floor
    p_f1 = point_iso(0, 0, 0)
    p_f2 = point_iso(room_x, 0, 0)
    p_f3 = point_iso(room_x, room_y, 0)
    p_f4 = point_iso(0, room_y, 0)
    svg.append(draw_poly([p_f1, p_f2, p_f3, p_f4], "#E8DCC4", stroke="#CDB891", stroke_width=2))

    # Back Left Wall (constant y=0, x from 0 to 450)
    p_bl1 = point_iso(0, 0, 0)
    p_bl2 = point_iso(room_x, 0, 0)
    p_bl3 = point_iso(room_x, 0, room_z)
    p_bl4 = point_iso(0, 0, room_z)
    svg.append(draw_poly([p_bl1, p_bl2, p_bl3, p_bl4], "#F0EAE1", stroke="#D9D0C1", stroke_width=1))

    # Back Right Wall (constant x=0, y from 0 to 500)
    p_br1 = point_iso(0, 0, 0)
    p_br2 = point_iso(0, room_y, 0)
    p_br3 = point_iso(0, room_y, room_z)
    p_br4 = point_iso(0, 0, room_z)
    svg.append(draw_poly([p_br1, p_br2, p_br3, p_br4], "#E6DECE", stroke="#D9D0C1", stroke_width=1))

    # Window on Back Left Wall
    w1 = point_iso(150, 0, 80)
    w2 = point_iso(400, 0, 80)
    w3 = point_iso(400, 0, 200)
    w4 = point_iso(150, 0, 200)
    svg.append(draw_poly([w1, w2, w3, w4], "#A8DADC", stroke="#457B9D", stroke_width=2))

    # Balcony Door on Back Left Wall
    d1 = point_iso(10, 0, 0)
    d2 = point_iso(100, 0, 0)
    d3 = point_iso(100, 0, 200)
    d4 = point_iso(10, 0, 200)
    svg.append(draw_poly([d1, d2, d3, d4], "#F1FAEE", stroke="#457B9D", stroke_width=2))

    # Objects list for improved z-sorting
    # To fix painter's algo bugs (pillows under bed, rug over sofa),
    # we need to sort accurately based on min(x) + min(y) and considering z heights.
    # By assigning a priority/z-index directly based on logical stacking, we can get better results.

    objects = []

    def add_cube(x, y, z, dx, dy, dz, ct, cl, cr, name="", z_index_override=None):
        # Base sort order on x + y for basic depth, plus z to ensure things on top stay on top.
        # Allow override for tricky things like the rug.
        if z_index_override is not None:
            sort_val = z_index_override
        else:
            sort_val = (x + y) * 10 + z

        poly_str = draw_cube(x, y, z, dx, dy, dz, ct, cl, cr)
        objects.append((sort_val, poly_str, name))

    def add_flat(poly_str, sort_val, name=""):
        objects.append((sort_val, poly_str, name))

    # Rug (z_index=0 to ensure it's under everything but above floor)
    rx, ry = 150, 150
    p_r1 = point_iso(rx, ry, 1)
    p_r2 = point_iso(rx+200, ry, 1)
    p_r3 = point_iso(rx+200, ry+150, 1)
    p_r4 = point_iso(rx, ry+150, 1)
    add_flat(draw_poly([p_r1, p_r2, p_r3, p_r4], "#F4A261"), 0, "Rug")

    # Bed
    add_cube(330, 250, 0, 120, 200, 40, "#E9C46A", "#D4A373", "#BC8A5F", "Bed Base", z_index_override=5800)
    add_cube(335, 290, 40, 110, 155, 10, "#FAEDCD", "#EBE0C0", "#D6CBB0", "Mattress/Duvet", z_index_override=5810)
    add_cube(345, 260, 50, 40, 25, 10, "#E76F51", "#D05D43", "#B54D35", "Pillow1", z_index_override=5820)
    add_cube(395, 260, 50, 40, 25, 10, "#E76F51", "#D05D43", "#B54D35", "Pillow2", z_index_override=5820)

    # Wardrobe
    add_cube(190, 440, 0, 120, 60, 180, "#D4A373", "#BC8A5F", "#A07049", "Wardrobe", z_index_override=6300)

    # Dresser
    add_cube(350, 460, 0, 80, 40, 80, "#D4A373", "#BC8A5F", "#A07049", "Dresser", z_index_override=8100)

    # Desk
    add_cube(250, 6, 0, 160, 70, 75, "#D4A373", "#BC8A5F", "#A07049", "Desk", z_index_override=2500)
    add_cube(270, 10, 75, 50, 10, 35, "#2B2B2B", "#1A1A1A", "#0F0F0F", "Monitor1", z_index_override=2510)
    add_cube(330, 10, 75, 50, 10, 35, "#2B2B2B", "#1A1A1A", "#0F0F0F", "Monitor2", z_index_override=2510)

    # Chair
    add_cube(310, 85, 0, 40, 40, 45, "#457B9D", "#346685", "#285470", "Chair Base", z_index_override=3900)
    add_cube(315, 80, 45, 30, 10, 45, "#1D3557", "#132540", "#0D1B30", "Chair Back", z_index_override=3910)

    # TV Console
    add_cube(0, 200, 0, 30, 120, 45, "#D4A373", "#BC8A5F", "#A07049", "TV Console", z_index_override=2000)
    add_cube(10, 220, 45, 10, 80, 60, "#2B2B2B", "#1A1A1A", "#0F0F0F", "TV", z_index_override=2010)

    # Sofa
    add_cube(150, 200, 0, 70, 140, 40, "#E76F51", "#D05D43", "#B54D35", "Sofa Base", z_index_override=3500)
    add_cube(150, 200, 40, 20, 140, 35, "#E76F51", "#D05D43", "#B54D35", "Sofa Back", z_index_override=3510)
    add_cube(170, 210, 40, 50, 60, 15, "#F4A261", "#E08F50", "#C87C40", "Cushion1", z_index_override=3520)
    add_cube(170, 270, 40, 50, 60, 15, "#F4A261", "#E08F50", "#C87C40", "Cushion2", z_index_override=3520)

    # Coffee Table
    add_cube(80, 250, 0, 40, 40, 30, "#D4A373", "#BC8A5F", "#A07049", "Coffee Table", z_index_override=3300)

    # Plant 1
    add_cube(410, 15, 0, 30, 30, 60, "#2A9D8F", "#218276", "#19665B", "Plant1", z_index_override=4200)

    # Plant 2
    add_cube(20, 140, 0, 25, 25, 50, "#2A9D8F", "#218276", "#19665B", "Plant2", z_index_override=1600)

    # Sort objects by our custom z_index logic
    objects.sort(key=lambda item: item[0])

    for _, poly_str, _ in objects:
        svg.append(poly_str)

    svg.append('</svg>')

    with open("room_visualization.svg", "w") as f:
        f.write("\n".join(svg))

if __name__ == "__main__":
    main()
