# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re


class AbicomPipeline:
    def process_item(self, item, spider):
        date = item['date']
        content_raw = item['content']

        curated_def_pct = [s for s in content_raw if s.strip().startswith('Defasagem média de')]
        percentage_pattern = r'([-+]?\d+\%)'
        percentage_matches = []

        # Iterate over each string in curated_def
        for s in curated_def_pct:
            matches = re.findall(percentage_pattern, s)
            percentage_matches.extend(matches)
        
        if percentage_matches:
            diesel_pct = float(percentage_matches[0].replace('%', ''))
            gasolina_pct = float(percentage_matches[-1].replace('%', ''))
        else:
            diesel_pct = None
            gasolina_pct = None

        joined_content = ''.join(content_raw)
        curated_def_brl = re.compile(r'média de[:]?[\n]?[ ]?([+-–]?R\$[0-9,]+)', re.DOTALL)
        media_pattern_list = curated_def_brl.findall(joined_content)
        diesel_brl = float(media_pattern_list[0].strip().replace('R$', '').replace(',', '.').replace('–', '-').replace('L', ''))
        gasolina_brl = float(media_pattern_list[1].strip().replace('R$', '').replace(',', '.').replace('–', '-').replace('L', ''))
        

        item['content'] = {
            'diesel_pct': diesel_pct,
            'diesel_brl': diesel_brl,
            'gasolina_pct': gasolina_pct,
            'gasolina_brl': gasolina_brl
        }

        return item
