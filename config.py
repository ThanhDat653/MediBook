import os


class Config():
    LOCAL_DIR = os.getcwd()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UI_DIR = os.path.join(BASE_DIR, "ui")

    JSON_PATH = os.path.join(BASE_DIR, "data", "data.json")
        
    MENU_COLLAPSED_WIDTH = 50
    MENU_FULL_WIDTH = 150
    TOGGLE_ANIMATION_DURATION = 500

    DROP_SHADOW_OFFSET = (5,5)
    DROP_SHADOW_BLUR_RADIUS = 40

    HOME_IMG_SIZE = (980, 700)

    HOME_PAGE_INDEX = 0
    RANK_PAGE_INDEX = 1
    CRUD_MENU_INDEX= 2
    TVSHOW_PAGE_INDEX = 3
    USER_PAGE_INDEX = 4
    SEARCH_ANIME_INDEX = 5
