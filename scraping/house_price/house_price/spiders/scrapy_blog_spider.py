import scrapy
from house_price.items import HousePriceDetail
from house_price.items import HousePriceList
from scrapy.exporters import CsvItemExporter
import time

class ScrapyBlogSpiderSpider(scrapy.Spider):
    name = 'scrapy_blog_spider'
    allowed_domains = ['suumo.jp']
    # 武蔵小杉の4万以上、12万以下
    start_urls = [
        "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ra=014&cb=4.0&ct=12.0&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&ek=022038720&rn=0220&page=1"
        ]

    def __init__(self, *args, **kwargs):
        super(ScrapyBlogSpiderSpider, self).__init__(*args, **kwargs)
        
        # ファイル出力関連
        self.file_list_page = open('../../../../input/list_page_data.csv', 'ab')
        self.file_detail_page = open('../../../../input/detail_page_data.csv', 'ab')
        self.exporter_list_page = CsvItemExporter(self.file_list_page)
        self.exporter_detail_page = CsvItemExporter(self.file_detail_page)
        self.exporter_list_page.start_exporting()
        self.exporter_detail_page.start_exporting()

        # 終了条件: URLのpage="x"について、x >= self.finishi_pageなら終了する
        self.finish_page_number = 100
        self.iter_number = 0


    def parse(self, response):
        """
        レスポンスに対するパース処理
        step1: リストページでのデータ取得
            step1.1: urlに含まれる詳細ボタンのURLを取得
            step1.2: リストページにある情報の取得
            step1.3: 詳細ボタンのURL数だけfor文で回して、HousePriceListクラスをyield
                step1.3.1: リストページにある情報を[HousePriceList]インスタンス作成
                step1.3.2: csvに出力する

        step2: 詳細ページでのデータ取得
            step2.1: 詳細ボタンのURL数だけfor文回す
                step2.1.1: 詳細ページのURLでスクレイピング

        step3: 次に探索するリストページのURLへ更新
        
        step4: 終了条件(100ページまでの物件を探し終えたら)終了処理を行う

        step5: 次ページのリクエスト実行
        """

        # ----- step1: リストページでのデータ取得
        # ----- step1.1: urlに含まれる詳細ボタンのURL取得
        detail_urls_list = response.css('a.js-cassette_link_href.cassetteitem_other-linktext::attr(href)').getall()
        # -----
        
        # ----- step1.2: リストページにある情報の取得
        list_page_data = {}
        # タイトルの取得
        # list_page_data["title"] = response.css('div.cassetteitem_content-title::text').getall()
        # 賃料の取得
        list_page_data["yatin"] = response.css('span.cassetteitem_other-emphasis.ui-text--bold::text').getall()
        # 管理費の取得
        list_page_data["kanrihi"] = response.css('span.cassetteitem_price.cassetteitem_price--administration::text').getall()
        # 敷金の取得
        list_page_data["shikikin"] = response.css('span.cassetteitem_price.cassetteitem_price--deposit::text').getall()
        # 礼金の取得
        list_page_data["reikin"] = response.css('span.cassetteitem_price.cassetteitem_price--gratuity::text').getall()
        # 間取りの取得
        list_page_data["madori"] = response.css('span.cassetteitem_madori::text').getall()
        # 面積の取得
        list_page_data["menseki"] = response.css('span.cassetteitem_menseki::text').getall()
        # ----- 

        # ----- step1.3: 詳細ボタンのURL数だけfor文で回して、HousePriceListクラスをyield
        for i in range(len(detail_urls_list)):
            
            # step1.3.1: リストページにある情報を[HousePriceList]インスタンス作成
            house_price_list = HousePriceList(
                # title=list_page_data["title"][i], 
                url="page=" + str(self.iter_number+1), 
                detail_url=response.urljoin(detail_urls_list[i]),
                yatin=list_page_data["yatin"][i],
                kanrihi=list_page_data["kanrihi"][i],
                shikikin=list_page_data["shikikin"][i],
                reikin=list_page_data["reikin"][i],
                madori=list_page_data["madori"][i],
                menseki=list_page_data["menseki"][i],
            )
            # step1.3.2: csvに出力する
            self.exporter_list_page.export_item(house_price_list)
        # -----
        # -----

        # ----- step2: 詳細ページでのデータ取得
        # step2.1: 詳細ボタンのURL数だけfor文回す
        for detail_url in detail_urls_list:

            # step2.1.1: 詳細ページのURLでスクレイピング
            yield scrapy.Request(response.urljoin(detail_url), callback=self.parse_detail)

            # sleepしないと順番があべこべになってしまうため、その防止
            time.sleep(32*(10**-3))
        # -----

        # ----- step3: 次に探索するリストページのURLへ更新
        next_list_url = response.request.url
        page_number = int(next_list_url.split("&page=")[1]) + 1
        next_list_url = next_list_url.split("&page=")[0] + "&page=" + str(page_number)
        # -----

        # ----- step4: 終了条件の確認
        self.iter_number += 1
        if self.iter_number >= self.finish_page_number:
            # self.exporter_list_page.finish_exporting()
            # self.exporter_detail_page.finish_exporting()
            # self.file_list_page.close()
            # self.file_detail_page.close()

            # 60秒待つ
            time.sleep(60000*(10**-3))
            return
        # -----


        # ----- step5: 次ページのリクエスト実行
        # URLが相対パスだった場合に絶対パスに変換する
        next_list_url = response.urljoin(next_list_url)

        yield scrapy.Request(next_list_url, callback=self.parse)
        # -----


    def parse_detail(self, response):
        """
        detailページのリクエストに対するパース処理
        
        step1: テーブル情報(tr)を取得する

        step2: テーブル情報のtrタグの数だけfor文ループ

            step2.1: thタグの個数が2以上なら下記を実行
                step2.1.1: trタグの中にある、thタグの回数だけfor文ループ
                step2.1.1.1: thタグのテキストを取得する
                step2.1.1.2: thタグのテキストがconverterにあれば、対になるtdタグのテキストをdictに保存する

            step2.2: thタグの個数が1なら下記を実行
                step2.2.1: thタグのテキストを取得する
                step2.2.2: thタグのテキストがconverterにあれば、対になるtdタグのテキストをdictに保存する

        step3: タイトルの情報を取得

        step4: 「部屋の特徴・設備」情報の取得

        step5: 「駅徒歩」情報の取得

        step6: 「所在地」情報の取得

        step7: [HousePriceDetail]のインスタンスを作成する

        step8: csvで出力する
        """

        # import pdb
        # pdb.set_trace()

        # 表の表示名と、HousePriceDetailの項目名の辞書
        converter = {
            "間取り詳細": "madori_detail", "階建": "kaidate", "損保": "sonpo", "入居": "nyukyo", "条件": "zyoken", "契約期間": "keiyaku_kikan", 
            "仲介手数料": "tyukai_tesuryo", "ほか初期費用": "syokihi", "ほか諸費用": "syohiyo", "構造": "kozo", "築年月": "tikunengetu", 
            "駐車場": "tyusyazyo", 
            }

        # HousePriceDetailに出力するデータを保存する
        detail_page_data = {v: None for v in converter.values()}

        # ----- step1: テーブル情報を取得する
        table_tbody_tr_list = response.css('table.data_table.table_gaiyou tr')
        # ----- 

        # ----- step2: テーブル情報のtrタグの数だけfor分ループ
        for tr in table_tbody_tr_list:
            num_of_th_list = len(tr.css("th::text").getall())
    
            # step2.1: thタグの個数が2以上なら下記を実行
            if num_of_th_list > 1:

                # step2.1: trタグの中にある、thタグの回数だけfor文ループ
                for i in range(num_of_th_list):

                    # step2.1.1: thのテキストを取得
                    th_text = tr.css("th::text").getall()[i].strip()
                    
                    # step1.2.1: thタグのテキストがconverterにあれば、tdタグのテキストをdictに保存する
                    if th_text in converter:
                        detail_page_data[converter[th_text]] = tr.css("td::text").getall()[i].strip()
                    else:
                        pass
            # step2.2: thタグの個数が1なら下記を実行
            else:
                
                # step2.2.1: thタグのテキストを取得する
                th_text = tr.css("th::text").get().strip()

                # step2.2.2: thタグのテキストがconverterにあれば、対になるtdタグのテキストをdictに保存する
                if th_text in converter:
                    detail_page_data[converter[th_text]] = tr.css("li::text").get().strip()
                else:
                    pass
        # -----

        # ----- step3: タイトルの情報を取得
        detail_page_data["title"] = response.css("h1.section_h1-header-title::text").get().strip()
        # -----
        
        # ----- step4: 「部屋の特徴・設備」情報の取得
        detail_page_data["others"] = response.xpath('//*[@id="bkdt-option"]/div/ul/li/text()').get().strip()
        # -----

        # ----- step5: 「駅徒歩」情報の取得
        detail_page_data["ekitoho"] = response.xpath('//*[@id="js-view_gallery"]/div[3]/table/tr[2]/td/div/text()').get().strip()
        # -----

        # ----- step6: 「所在地」情報の取得
        detail_page_data["syozaiti"] = response.xpath('//*[@id="js-view_gallery"]/div[3]/table/tr[1]/td/text()').get().strip()
        # -----

        # ----- step7: [HousePriceDetail]をyieldする
        house_price_detail = HousePriceDetail(
            title=detail_page_data["title"], 
            url=response.request.url, 
            madori_detail=detail_page_data["madori_detail"],
            ekitoho=detail_page_data["ekitoho"], 
            syozaiti=detail_page_data["syozaiti"],
            kaidate=detail_page_data["kaidate"], 
            sonpo=detail_page_data["sonpo"], 
            nyukyo=detail_page_data["nyukyo"],
            zyoken=detail_page_data["zyoken"],
            keiyaku_kikan=detail_page_data["keiyaku_kikan"],
            tyukai_tesuryo=detail_page_data["tyukai_tesuryo"],
            syokihi=detail_page_data["syokihi"],
            syohiyo=detail_page_data["syohiyo"],
            kozo=detail_page_data["kozo"],
            tikunengetu=detail_page_data["tikunengetu"],
            tyusyazyo=detail_page_data["tyusyazyo"],
            others=detail_page_data["others"], 
        )
        # -----

        # ----- step8: csvで出力する
        self.exporter_detail_page.export_item(house_price_detail)
        # -----

        return 

