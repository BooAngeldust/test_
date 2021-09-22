from PIL import ImageFont, Image, ImageOps


class Resources:

    __FONTS = {}
    __FONTS["small"]       = ImageFont.truetype("data/fonts/normal.ttf",16)
    __FONTS["medium"]      = ImageFont.truetype("data/fonts/normal.ttf",24)
    __FONTS["medium_bold"] = ImageFont.truetype("data/fonts/bold.ttf",24)
    __FONTS["large"]       = ImageFont.truetype("data/fonts/bold.ttf",32)
    __FONTS["extreme"]     = ImageFont.truetype("data/fonts/bold.ttf",48)

    __COLOURS = {}
    __COLOURS["blue"]        = (100, 100, 140)
    __COLOURS["pink"]        = (255, 192, 203)
    __COLOURS["light_blue"]  = (173, 216, 230)
    __COLOURS["green"]       = (19, 78, 19) 
    __COLOURS["white"]       = (200, 200, 200)
    __COLOURS["trans_white"] = (200, 200, 200, 140)

    __RESOURCES = {}
    __RESOURCES["dark_rect_map"]     = Image.open("data/images/resources/dark_rect_map.png")
    __RESOURCES["bar_side_l"]        = Image.open("data/images/resources/bar_side.png")
    __RESOURCES["bar_side_r"]        = ImageOps.mirror(Image.open("data/images/resources/bar_side.png"))
    __RESOURCES["bar_middle"]        = Image.open("data/images/resources/bar_middle.png")
    __RESOURCES["medal_gold"]        = Image.open("data/images/resources/medal_gold.png")
    __RESOURCES["medal_silver"]      = Image.open("data/images/resources/medal_silver.png")
    __RESOURCES["medal_bronze"]      = Image.open("data/images/resources/medal_bronze.png")
    __RESOURCES["bg_insane"]         = Image.open("data/images/resources/bg_insane.png")
    __RESOURCES["bg_hard"]           = Image.open("data/images/resources/bg_hard.png")
    __RESOURCES["bg_main"]           = Image.open("data/images/resources/bg_main.png")
    __RESOURCES["bg_easy"]           = Image.open("data/images/resources/bg_easy.png")
    __RESOURCES["dark_rect_profile"] = Image.open("data/images/resources/dark_rect_profile.png")
    __RESOURCES["points_bg"]         = Image.open('data/images/resources/points_background.png')

    @staticmethod
    def GetFonts() -> dict:
        return Resources.__FONTS.copy()

    @staticmethod
    def GetColours() -> dict:
        return Resources.__COLOURS.copy()

    @staticmethod
    def GetResources() -> dict:
        return Resources.__RESOURCES.copy()