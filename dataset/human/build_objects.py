from utils.geometry import get_speed
from utils.misc import rand, repeat_scale
from utils.shape_net import get_random_shape, SHAPE_DIMENSIONS, ROTATE_SHAPE_CATEGORY
from utils.constants import eps

_object_map = dict()


def register_objects(func):
    _object_map[func.__name__] = func
    return func


def get_objects(case, cat_id, colors, materials):
    return _object_map[case](cat_id, colors, materials)


@register_objects
def disappear(cat_id, colors, materials):
    shape = get_random_shape(cat_id)
    color1, color2 = colors.pop(), colors.pop()
    material1, material2 = materials.pop(), materials.pop()
    size1, size2 = rand(.34, .36), rand(.34, .36)
    pos_z1 = SHAPE_DIMENSIONS[shape][2] * size1
    pos_z2 = SHAPE_DIMENSIONS[shape][2] * size2
    direction = 1 if rand(0, 1) > .5 and shape != "truck" else -1
    init_v1 = rand(1.1, 1.2) * direction
    init_v2 = rand(-1.2, -1.1) * direction
    init_x = rand(-1.5, -1.4)
    init_orn = [0, 0, 0] if cat_id not in ROTATE_SHAPE_CATEGORY else (0, 0, 90)

    object = dict(shape=shape, color=color1,
                  material=material1, init_pos=(rand(-.6, -.5), -3.8 * direction, pos_z1 + eps),
                  init_orn=init_orn,
                  scale=repeat_scale(size1), init_v=(0, init_v1, 0))
    through = dict(shape=shape, color=color2,
                   material=material2, init_pos=(init_x, 3.8 * direction, pos_z2 + eps),
                   init_orn=init_orn,
                   scale=repeat_scale(size2), init_v=(0, init_v2, 0))
    left = dict(shape=shape, color=color2,
                material=material2, init_pos=(init_x, 3.8 * direction, pos_z2 + eps),
                init_orn=init_orn,
                scale=repeat_scale(size2), init_v=(0, init_v2, 0), disappear_time=350)
    right = dict(shape=shape, color=color2,
                 material=material2, init_pos=(init_x, 0, pos_z2 + eps),
                 init_orn=init_orn,
                 scale=repeat_scale(size2), init_v=(0, init_v2, 0), appear_time=350)
    middle = dict(shape=shape, color=color2,
                  material=material2, init_pos=(init_x, 0, pos_z2 + eps), init_orn=init_orn,
                  scale=repeat_scale(size2), init_v=(0, 0, 0), disappear_time=350)
    case_objects = [[object, through], [object, left], [object, right], [object], [object, middle, right]]
    return case_objects


@register_objects
def disappear_fixed(cat_id, colors, materials):
    shape = get_random_shape(cat_id)
    color1, color2 = colors.pop(), colors.pop()
    material1, material2 = materials.pop(), materials.pop()
    size1, size2 = rand(.34, .36), rand(.34, .36)
    pos_z1 = SHAPE_DIMENSIONS[shape][2] * size1
    pos_z2 = SHAPE_DIMENSIONS[shape][2] * size2
    direction = 1 if rand(0, 1) > .5 and shape != "truck" else -1
    init_v1 = rand(1.1, 1.2) * direction
    init_v2 = rand(-1.2, -1.1) * direction
    init_x = rand(-1.5, -1.4)

    init_orn = [0, 0, 0] if cat_id not in ROTATE_SHAPE_CATEGORY else (0, 0, 90)

    object = dict(shape=shape, color=color1,
                  material=material1, init_pos=(rand(-.6, -.5), -3.8 * direction, pos_z1 + eps),
                  init_orn=init_orn,
                  scale=repeat_scale(size1), init_v=(0, init_v1, 0))
    through = dict(shape=shape, color=color2,
                   material=material2, init_pos=(init_x, 3.8 * direction, pos_z2 + eps),
                   init_orn=init_orn,
                   scale=repeat_scale(size2), init_v=(0, init_v2, 0))
    left = dict(shape=shape, color=color2,
                material=material2, init_pos=(init_x, 3.8 * direction, pos_z2 + eps),
                init_orn=init_orn,
                scale=repeat_scale(size2), init_v=(0, init_v2, 0), disappear_time=350)
    right = dict(shape=shape, color=color2,
                 material=material2, init_pos=(init_x, 0, pos_z2 + eps),
                 init_orn=init_orn,
                 scale=repeat_scale(size2), init_v=(0, init_v2, 0), appear_time=350)
    middle = dict(shape=shape, color=color2,
                  material=material2, init_pos=(init_x, 0, pos_z2 + eps), init_orn=init_orn,
                  scale=repeat_scale(size2), init_v=(0, 0, 0), appear_time=350)
    case_objects = [[object, through], [object, left], [object, right], [object], [object, left, middle]]
    return case_objects


@register_objects
def overturn(cat_id, colors, materials):
    shape = get_random_shape(cat_id)
    color1 = colors.pop()
    material1 = materials.pop()
    size1 = rand(.34, .36)
    pos_z1 = SHAPE_DIMENSIONS[shape][2] * size1
    init_y = rand(-.1, .1)
    init_x = rand(-.8, -.9)
    init_orn = (0, 0, 0) if cat_id not in ROTATE_SHAPE_CATEGORY else (0, 0, 90)

    origin = dict(shape=shape, color=color1,
                  material=material1, init_pos=(init_x, init_y, pos_z1 + eps), init_orn=init_orn,
                  scale=repeat_scale(size1), init_v=(0, 0, 0), disappear_time=300)
    final = dict(shape=shape, color=color1,
                 material=material1, init_pos=(init_x, init_y, pos_z1 + eps), init_orn=init_orn,
                 scale=repeat_scale(size1), init_v=(0, 0, 0), appear_time=600)
    case_objects = []
    for i in range(4):
        case_objects.append([origin] if i < 2 else [origin, final])
    return case_objects


@register_objects
def discontinuous(cat_id, colors, materials):
    shape = get_random_shape(cat_id)
    color1 = colors.pop()
    material1 = materials.pop()
    size1 = rand(.3, .32)
    pos_z1 = SHAPE_DIMENSIONS[shape][2] * size1
    direction = 1 if rand(0, 1) > .5 and shape != "truck" else -1
    init_x = rand(-.7, -.6)

    y_1 = rand(-2.22, -2.2)
    y_2 = rand(2.2, 2.22)

    init_orn = [0, 0, 0] if cat_id not in ROTATE_SHAPE_CATEGORY else (0, 0, 90)

    left_to_leftmost = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                            scale=repeat_scale(size1),
                            init_pos=(init_x, -1.1 * direction, pos_z1 + eps),
                            init_v=(0, get_speed(-1.1, y_1, 1.5) * direction, 0),
                            disappear_time=150)
    leftmost = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                    scale=repeat_scale(size1),
                    init_pos=(init_x, y_1 * direction, pos_z1 + eps),
                    init_v=(0, 0, 0), appear_time=150, disappear_time=200)
    leftmost_to_rightmost = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                                 scale=repeat_scale(size1),
                                 init_pos=(init_x, y_1 * direction, pos_z1 + eps),
                                 init_v=(0, get_speed(y_1, y_2, 5.) * direction, 0),
                                 appear_time=200, disappear_time=700)
    leftmost_to_left = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                            scale=repeat_scale(size1),
                            init_pos=(init_x, y_1 * direction, pos_z1 + eps),
                            init_v=(0, get_speed(y_1, -1.1, 1.) * direction, 0),
                            appear_time=200, disappear_time=300)
    right_to_rightmost = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                              scale=repeat_scale(size1),
                              init_pos=(init_x, 1.1 * direction, pos_z1 + eps),
                              init_v=(0, get_speed(1.1, y_2, 1.) * direction, 0),
                              appear_time=600, disappear_time=700)
    rightmost = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                     scale=repeat_scale(size1),
                     init_pos=(init_x, y_2 * direction, pos_z1 + eps),
                     init_v=(0, 0, 0),
                     appear_time=700, disappear_time=750)
    rightmost_to_right = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                              scale=repeat_scale(size1),
                              init_pos=(init_x, y_2 * direction, pos_z1 + eps),
                              init_v=(0, get_speed(y_2, 1.1, 1.5) * direction, 0),
                              appear_time=750, disappear_time=900)
    left = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                scale=repeat_scale(size1),
                init_pos=(init_x, -1.1 * direction, pos_z1 + eps),
                init_v=(0, 0, 0), appear_time=900)
    right = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                 scale=repeat_scale(size1),
                 init_pos=(init_x, 1.1 * direction, pos_z1 + eps),
                 init_v=(0, 0, 0), appear_time=900)
    visible_objects = [left_to_leftmost, leftmost, leftmost_to_rightmost, rightmost, rightmost_to_right]
    invisible_objects = [left_to_leftmost, leftmost, leftmost_to_left, right_to_rightmost, rightmost,
                         rightmost_to_right]
    case_objects = []
    for i in range(4):
        case_object = []
        case_object.extend(invisible_objects if i < 2 else visible_objects)
        case_object.extend([left, right] if i % 2 == 0 else [right])
        case_objects.append(case_object)
    case_objects.extend(case_objects[:2])
    return case_objects


@register_objects
def delay(cat_id, colors, materials):
    shape = get_random_shape(cat_id)
    color1 = colors.pop()
    material1 = materials.pop()
    size1 = rand(.3, .32)
    pos_z1 = SHAPE_DIMENSIONS[shape][2] * size1
    direction = 1 if rand(0, 1) > .5 and shape != "truck" else -1
    init_x = rand(-.7, -.6)

    if cat_id not in ROTATE_SHAPE_CATEGORY:
        init_orn = [0, 0, 0]
        y_1 = rand(-2.22, -2.2) - size1 + SHAPE_DIMENSIONS[shape][1] * size1
        y_2 = rand(2.2, 2.22) + size1 - SHAPE_DIMENSIONS[shape][1] * size1
    else:
        init_orn = (0, 0, 90)
        y_1 = rand(-2.22, -2.2) - size1 + SHAPE_DIMENSIONS[shape][0] * size1
        y_2 = rand(2.2, 2.22) + size1 - SHAPE_DIMENSIONS[shape][0] * size1

    left_to_leftmost = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                            scale=repeat_scale(size1),
                            init_pos=(init_x, -1.1 * direction, pos_z1 + eps),
                            init_v=(0, get_speed(-1.1, y_1, 1.5) * direction, 0),
                            disappear_time=150)
    leftmost = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                    scale=repeat_scale(size1),
                    init_pos=(init_x, y_1 * direction, pos_z1 + eps),
                    init_v=(0, 0, 0), appear_time=150, disappear_time=200)
    leftmost_to_left = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                            scale=repeat_scale(size1),
                            init_pos=(init_x, y_1 * direction, pos_z1 + eps),
                            init_v=(0, get_speed(y_1, -1.1, 1.) * direction, 0),
                            appear_time=200, disappear_time=300)
    right_to_rightmost = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                              scale=repeat_scale(size1),
                              init_pos=(init_x, 1.1 * direction, pos_z1 + eps),
                              init_v=(0, get_speed(1.1, y_2, 1.) * direction, 0),
                              appear_time=300, disappear_time=400)
    rightmost = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                     scale=repeat_scale(size1),
                     init_pos=(init_x, y_2 * direction, pos_z1 + eps),
                     init_v=(0, 0, 0),
                     appear_time=400, disappear_time=450)
    rightmost_to_right = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                              scale=repeat_scale(size1),
                              init_pos=(init_x, y_2 * direction, pos_z1 + eps),
                              init_v=(0, get_speed(y_2, 1.1, 1.5) * direction, 0),
                              appear_time=450, disappear_time=600)
    left = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                scale=repeat_scale(size1),
                init_pos=(init_x, -1.1 * direction, pos_z1 + eps),
                init_v=(0, 0, 0), appear_time=600)
    right = dict(shape=shape, color=color1, material=material1, init_orn=init_orn,
                 scale=repeat_scale(size1),
                 init_pos=(init_x, 1.1 * direction, pos_z1 + eps),
                 init_v=(0, 0, 0), appear_time=600)
    invisible_objects = [left_to_leftmost, leftmost, leftmost_to_left, right_to_rightmost, rightmost,
                         rightmost_to_right]
    return [invisible_objects + [left, right], invisible_objects + [right]]


@register_objects
def block(cat_id, colors, materials):
    shape = get_random_shape(cat_id)
    color1, color2 = colors.pop(), colors.pop()
    material1, material2 = materials.pop(), materials.pop()
    size1 = rand(.3, .32)
    pos_z1 = SHAPE_DIMENSIONS[shape][2] * size1
    direction = 1 if rand(0, 1) > .5 and shape != "truck" else -1
    init_x = rand(-.6, -.5)
    init_orn = [0, 0, 0] if cat_id not in ROTATE_SHAPE_CATEGORY else (0, 0, 90)

    direction_block = 1 if rand(0, 1) > .5 else -1

    origin = dict(shape=shape, color=color1, material=material1, init_orn=init_orn, scale=repeat_scale(size1),
                  init_pos=(init_x, -4 * direction, pos_z1 + eps),
                  init_v=(0, 1.2 * direction, 0), disappear_time=520)
    left = dict(shape=shape, color=color1, material=material1, init_orn=init_orn, scale=repeat_scale(size1),
                init_pos=(init_x, -.7 * direction, pos_z1 + eps),
                init_v=(0, 0, 0), appear_time=520)
    right = dict(shape=shape, color=color1, material=material1, init_orn=init_orn, scale=repeat_scale(size1),
                 init_pos=(init_x, .7 * direction, pos_z1 + eps),
                 init_v=(0, 0, 0), appear_time=520)
    block = dict(shape="cube", color=color2, material=material2, init_orn=(0, 0, rand(10, 15) * direction_block),
                 scale=[1.2, .15, .8], init_pos=(-1.3, 0, .8), init_v=(0, 0, 0), mass=0)

    return [[origin, block, left], [origin, block, right]]
