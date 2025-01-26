import scrapy
from itemloaders.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags


def clean_price(value):
    """Hàm làm sạch và định dạng giá."""
    value = value.replace(",", "").replace(".", "").replace("đ", "").strip()
    return int(value) if value.isdigit() else value


class RoutineItem(scrapy.Item):
    # Tên sản phẩm: Lấy giá trị đầu tiên, loại bỏ thẻ HTML
    name = scrapy.Field(
        input_processor=MapCompose(remove_tags, str.strip),
        output_processor=TakeFirst(),
    )
    
    # Giá sản phẩm: Làm sạch giá trị, chuyển đổi sang số nguyên
    price = scrapy.Field(
        input_processor=MapCompose(remove_tags, str.strip, clean_price),
        output_processor=TakeFirst(),
    )
    
