import json
import requests

class APIOpenBD:
    '''
    OpenBD API
    '''
    def __init__(self):
        '''
        初期化
        '''
        pass

    def get_json(self, isbn:str) -> dict:
        '''
        Google Books API の呼び出しで戻ってきた書籍データから、必要な情報を抜き出して整形する

        Parameters
        ----------
        isbn : str
            登録する書籍のISBNコード
            '-'を除いた英数字の文字列
        Returns
        -------
        json : dic
            書籍データ
            呼び出しに失敗した場合はNone
        '''
        print(isbn)
        # WebAPIを呼び出してJSONを取得する
        json_api_data = self.__call_web_api(isbn)
        print(json_api_data)

        # 呼び出しが失敗した場合
        if json_api_data == None:
            return None
        print('json_api_data=' + json_api_data)

        # 検索結果が0だった場合
        # if json_api_data['totalItems'] == 0:
        #     return None
        # 呼び出しが成功した場合
        # 必要な情報だけを抜き出して新しいJSONを作成する
        # Elasticsearchの項目（'mapping.json'で定義）と項目を揃えること
        json_data = {}
        json_data['title'] = json_api_data[0]['summary']['title']
        json_data['authors'] = json_api_data[0]['summary']['author']
        json_data['publisher'] = json_api_data[0]['summary']['publisher']
        json_data['publishedDate'] = json_api_data[0]['summary']['pubdate']
        if 'TextContent' in json_api_data[0]['onix']['CollateralDetail']:
            for tc in json_api_data[0]['onix']['CollateralDetail']['TextContent']:
                if tc['TextType'] == '03':  # これが詳細らしい
                    # print('description='+ json_api_data[0]['onix']['CollateralDetail']['TextContent'][0]['Text'] )
                    # json_data['description'] = json_api_data[0]['onix']['CollateralDetail']['TextContent'][0]['Text']
                    print('description=' + tc['Text'] )
                    json_data['description'] = tc['Text']
                    break
        json_data['thumbnail'] = json_api_data[0]['summary']['cover']

        # isbnコードが込み入った形で格納されている
        json_data['isbn'] = json_api_data[0]['onix']['ProductIdentifier']['IDValue']

        return json_data
        
    def __call_web_api(self, isbn:str) -> dict:
        '''
        Google Books API を呼び出して、ISBNに対応するJSONデータを受け取る

        Parameters
        ----------
        isbn : str
            書籍のISBNコード
        Returns
        -------
        json_data : dic
            書籍のJSONデータ
            呼び出しに失敗した場合はNone
        '''
        print(isbn)
        # WebAPIのURLに引数文字列を追加
        url = 'https://api.openbd.jp/v1/get?isbn=' + isbn
        print(url)

        # WebAPIの呼び出し
        response = requests.get(url)

        # 呼び出しの成否をチェック
        status_code = response.status_code
        if status_code != 200:
            # 失敗した場合
            return None

        # 呼び出し成功した場合
        # 返ってきたJSON文字列を取得する
        json_text = response.text      

        # JSON文字列を辞書型に変換する
        json_data = json.loads(json_text)

        return json_data

if __name__ == "__main__":
    api = APIOpenBD()
    data = api.get_json('9784797389463')
    print(data)
