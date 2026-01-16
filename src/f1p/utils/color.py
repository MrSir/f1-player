import colorsys


def hex_to_rgb_saturation(hex_code):
    # 1. Convert hex to RGB (0-255 range)
    hex_code = hex_code.lstrip("#")
    lv = len(hex_code)
    rgb_255 = tuple(int(hex_code[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))

    # 2. Normalize RGB to the [0.0, 1.0] range
    r_norm, g_norm, b_norm = [x / 255.0 for x in rgb_255]

    # 3. Convert normalized RGB to HLS (Hue, Lightness, Saturation)
    # The result 's' is the saturation, ranging from 0.0 (grayscale) to 1.0 (full color)
    _, _, saturation = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)

    return {
        "hex": f"#{hex_code}",
        "rgb": rgb_255,
        "saturation_hls": saturation,
    }
