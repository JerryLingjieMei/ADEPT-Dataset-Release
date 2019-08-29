from utils.constants import OCCLUDER_HALF_WIDTH
from utils.misc import rand

_occluder_map = dict()


def register_occluders(func):
    _occluder_map[func.__name__] = func
    return func


def get_occluders(case, colors, materials, **kwargs):
    return _occluder_map[case](colors, materials, **kwargs)


@register_occluders
def disappear(colors, materials):
    color = colors.pop()
    material = materials.pop()
    init_t = int(rand(10, 20))
    final_t = int(rand(10, 20))
    width = rand(.8, .9)
    height = width * rand(.8, .85)
    init_orn = (0, 0, rand(-15, 15))
    joint_pattern = [(90, 90, init_t),
                     (90, 0, 350 - init_t),
                     (0, 90, 350 - final_t),
                     (90, 90, final_t)]

    occluder = dict(shape="cube", color=color, joint="revolute",
                    material=material, init_pos=(.2, rand(-.1, .1), 0), init_orn=init_orn,
                    scale=(OCCLUDER_HALF_WIDTH, width, height),
                    joint_pattern=joint_pattern)
    return [[occluder] for _ in range(5)]


@register_occluders
def disappear_fixed(colors, materials):
    color = colors.pop()
    material = materials.pop()
    final_t = int(rand(10, 20))
    width = rand(.8, .9)
    height = width * rand(.8, .85)
    init_orn = (0, 0, rand(-15, 15))
    occluder = dict(shape="cube", color=color, joint="revolute",
                    material=material, init_pos=(.2, rand(-.2, .2), 0), init_orn=init_orn,
                    scale=(OCCLUDER_HALF_WIDTH, width, height),
                    joint_pattern=[(0, 0, 700),
                                   (0, 90, 250 - final_t),
                                   (90, 90, final_t)])
    return [[occluder] for _ in range(5)]


@register_occluders
def overturn(colors, materials):
    color = colors.pop()
    material = materials.pop()
    theta = rand(45, 50)
    width = rand(.9, 1.)
    height = width * rand(.9, .95)
    init_orn = (0, 0, rand(-15, 15))

    case_occluders = []
    for i in range(4):
        if i == 0:
            joint_pattern = [(90, 90, 50), (90, -90, 350), (-90, -90, 50)]
        elif i == 1:
            joint_pattern = [(90, 90, 50), (90, -theta, 350), (-theta, -theta, 50)]
        elif i == 2:
            joint_pattern = [(90, 90, 50), (90, -theta, 350), (-theta, -theta, 50), (-theta, 90, 350), (90, 90, 50)]
        else:
            joint_pattern = [(90, 90, 50), (90, -90, 350), (-90, -90, 50), (-90, 90, 350), (90, 90, 50)]
        occluder = dict(shape="cube", color=color, joint="revolute",
                        material=material, init_pos=(.2, rand(-.1, .1), 0), init_orn=init_orn,
                        scale=(OCCLUDER_HALF_WIDTH, width, height),
                        joint_pattern=joint_pattern)
        case_occluders.append([occluder])
    return case_occluders


@register_occluders
def discontinuous(colors, materials):
    color1, color2 = colors.pop(), colors.pop()
    material1, material2 = materials.pop(), materials.pop()
    width = rand(.44, .46)
    height = rand(.6, .65)
    init_orn1 = (0, 0, rand(-10, 10))
    init_orn2 = (0, 0, rand(-10, 10))
    init_y = rand(.9, .95)

    left = dict(shape="cube", color=color1, joint="revolute",
                material=material1, init_orn=init_orn1,
                init_pos=(.2, -init_y, 0), scale=(OCCLUDER_HALF_WIDTH, width, height),
                joint_pattern=[(0, 0, 900), (0, 90, 150), (90, 90, 50)])
    right = dict(shape="cube", color=color2, joint="revolute",
                 material=material2, init_orn=init_orn2,
                 init_pos=(.2, init_y, 0), scale=(OCCLUDER_HALF_WIDTH, width, height),
                 joint_pattern=[(0, 0, 900), (0, 90, 150), (90, 90, 50)])

    init_orn3 = (0, 0, rand(-10, 10))

    big = dict(shape="cube", color=color1, joint="revolute",
               material=material1, init_orn=init_orn3,
               init_pos=(.2, 0, 0), scale=(OCCLUDER_HALF_WIDTH, rand(1.35, 1.4), rand(.6, .65)),
               joint_pattern=[(0, 0, 900), (0, 90, 150), (90, 90, 50)])
    return [[left, right] for _ in range(4)] + [[big] for _ in range(2)]


@register_occluders
def delay(colors, materials):
    color1 = colors.pop()
    material1 = materials.pop()
    init_orn1 = (0, 0, rand(-10, 10))

    big = dict(shape="cube", color=color1, joint="revolute",
               material=material1, init_orn=init_orn1,
               init_pos=(.2, 0, 0), scale=(OCCLUDER_HALF_WIDTH, rand(1.4, 1.45), rand(.8, .9)),
               joint_pattern=[(0, 0, 600), (0, 90, 200), (90, 90, 50)])

    return [[big] for _ in range(2)]


@register_occluders
def block(colors, materials):
    color1 = colors.pop()
    material1 = materials.pop()
    width = rand(1.05, 1.15)
    height = rand(.6, .65)
    init_orn1 = (0, 0, rand(-10, 10))

    occluder = dict(shape="cube", color=color1, joint="revolute",
                    material=material1, init_orn=init_orn1,
                    init_pos=(.2, 0, 0), scale=(OCCLUDER_HALF_WIDTH, width, height),
                    joint_pattern=[(90, 90, 50), (90, 0, 150), (0, 0, 300), (0, 90, 150), (90, 90, 50)])

    return [[occluder] for _ in range(2)]
