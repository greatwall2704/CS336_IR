import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import RoutineItem
from scrapy.loader import ItemLoader
import re


class ProductsSpider(CrawlSpider):
    name = "products"
    allowed_domains = ["routine.vn"]
    start_urls = ["https://routine.vn/categories/ao-nam?page=1"]
    
    # Biến toàn cục để đếm số sản phẩm đã xử lý
    product_count = 0
    max_products = 50  # Số lượng sản phẩm tối đa cần thu thập

    rules = (
        # Rule để thu thập tất cả các trang danh mục
        Rule(LinkExtractor(allow=(r"categories/ao-nam\?page=\d+")), follow=True),
        # Rule để thu thập các liên kết sản phẩm chi tiết
        Rule(LinkExtractor(allow=(r"products/")), callback="parse_item"),
    )

    def parse_item(self, response):
        # Kiểm tra số lượng sản phẩm đã thu thập
        if self.product_count >= self.max_products:
            self.logger.info("Reached the maximum product limit. Stopping crawler.")
            return None

        # Xác định div cha chứa thông tin sản phẩm
        parent_div = response.css('div.sc-7454bded-0.hXtIET.md\\:border-\\[1px\\].z-10.md\\:p-4.md\\:border-border')

        if not parent_div:
            self.logger.warning("Parent div not found!")
            return None

        # Tạo ItemLoader để load dữ liệu vào RoutineItem
        l = ItemLoader(item=RoutineItem(), selector=parent_div)

        # Trích xuất thông tin sản phẩm từ parent_div
        l.add_css("Name", 'h1.text-\\[22px\\].font-bold::text')
        l.add_css("Price", 'div.text-text-primary.font-semibold.text-\\[16px\\]::text')
        l.add_css("SKU", 'div.text-sm::text', re=r"SKU:\s*(.*)")
        l.add_css("Image_URL", 'picture img::attr(src)')
        
        # Tăng biến đếm sản phẩm
        self.product_count += 1

        # Trả về item đã thu thập
        return l.load_item()
