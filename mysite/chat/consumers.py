from grp import struct_group
import json
from urllib import request
#from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer #非同期処理
#from asgiref.sync import async_to_sync  # async_to_sync() : 非同期関数を同期的に実行する際に使用する。
import datetime

# ChatConsumerクラス: WebSocketからの受け取ったものを処理するクラス これは同期処理
#channel_layer関連は非同期なので、同期処理のためasync_to_syncで変換

USERNAME_SYSTEM = '*system*'


class ChatConsumer(AsyncWebsocketConsumer):
    #ルーム管理 クラス変数
    rooms = None
    def __init__(self,*args,**kwargs):
        print("ChatConsumer呼び出し")
        super().__init__(*args,**kwargs)
        #クラス変数の初期化
        if ChatConsumer.rooms is None:
            ChatConsumer.rooms = {}
        self.strGroupName = ""
        self.strUserName = ""
    
    #websocket接続時の処理
    async def connect(self):
        #gruupに参加
        #self.strGroupName = 'chat'
        #async_to_sync(self.channel_layer.group_add) 非同期のself.channel_layer.group_addを同期関数に変換
        #async_to_sync(self.channel_layer.group_add)(self.strGroupName, self.channel_name)
        #await self.channel_layer.group_add( self.strGroupName, self.channel_name )
        
        # WebSocket接続を受け入れます
        # ・connect()でaccept()を呼び出さないと、接続は拒否されて閉じられます。
        # 　たとえば、要求しているユーザーが要求されたアクションを実行する権限を持っていないために、接続を拒否したい場合があります。
        # 　接続を受け入れる場合は、connect()の最後のアクションとしてaccept()を呼び出します。
        await self.accept()

    #websocket切断時の処理
    async def disconnect(self,close_code):
        # グループから離脱
        #await self.channel_layer.group_discard(self.strGroupName, self.channel_name)
        #チャットから離脱
        await self.leave_chat()
    
    # WebSocketからのデータ受信時の処理
    # （ブラウザ側のJavaScript関数のsocketChat.send()の結果、WebSocketを介してデータがChatConsumerに送信され、本関数で受信処理します）
    async def receive(self,text_data):
        print("receive関数実行")
        # 受信データをJSONデータに復元
        text_data_json = json.loads(text_data)
        print(f"json:f{json.dumps(text_data_json)}")
        #チャット参加時の処理
        if('join' == text_data_json.get('data_type')):
            #ユーザー名をクラスメンバ変数に設定
            self.strUserName = text_data_json['username']
            #ルーム名の設定
            strRoomName = text_data_json['roomname']
            #参加
            await self.join_chat(strRoomName)

        #チャット離脱時
        elif('leave' == text_data_json.get('data_type')):
            #離脱
            await self.leave_chat()
        
        else:
            # メッセージの取り出し
            strMessage = text_data_json['message']
            # グループ内の全コンシューマーにメッセージ拡散送信（受信関数を'type'で指定）
            data = {
                'type': 'chat_message', #受信処理関数名
                'message':strMessage, #メッセージ
                'username':self.strUserName,
                'datetime':datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')
                }
            await self.channel_layer.group_send(self.strGroupName,data)
    
    #拡散メッセージ受信時の処理
    #(self.channel_layer.group_send()の結果、グループ内の全コンシューマーにメッセージ拡散され、各コンシューマーは本関数で受信処理します)
    async def chat_message(self,data):
        data_json = {
            'message':data['message'],
            'username':data['username'],
            'datetime':data['datetime'],
        }
        # WebSocketにメッセージを送信します。
        # （送信されたメッセージは、ブラウザ側のJavaScript関数のsocketChat.onmessage()で受信処理されます）
        # JSONデータをテキストデータにエンコードして送ります。
        await self.send(text_data=json.dumps(data_json))
    
    #チャットへの参加
    async def join_chat(self,strRoomName):
        print("join_chat関数開始")
        #グループに参加
        self.strGroupName = f'chat_{strRoomName}'
        print(f' self.strGroupName{ self.strGroupName}')
        await self.channel_layer.group_add(self.strGroupName, self.channel_name)

        #参加者の更新 dict.get() 存在しないときは（引数を指定しないと）Noneが返る
        room = ChatConsumer.rooms.get(self.strGroupName)
        if(room == None):
            # ルーム管理にルーム追加
            ChatConsumer.rooms[self.strGroupName] = {'participants_count':1}
        else:
            ChatConsumer.rooms[self.strGroupName]['participants_count'] += 1
        print(ChatConsumer.rooms)
        #システムメッセージの作成 
        #f関数内では、辞書のキー指定時に同じ引用符を使わない（"と'を使い分ける）
        strMessage = f'{self.strUserName}joined there are {ChatConsumer.rooms[self.strGroupName]["participants_count"]} part'
        # グループ内の全コンシューマーにメッセージ拡散送信（受信関数を'type'で指定）
        data = {
            'type': 'chat_message', #受信処理関数名
            'message':strMessage, #メッセージ
            'username':USERNAME_SYSTEM,
            'datetime':datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')
            }
        await self.channel_layer.group_send(self.strGroupName,data)


    
    #チャットから離脱
    async def leave_chat(self):
        if(self.strGroupName == ''):
            return
        
        #参加者の更新 dict.get() 存在しないときは（引数を指定しないと）Noneが返る
        ChatConsumer.rooms[self.strGroupName]['participants_count'] -= 1
        #システムメッセージの作成 
        #f関数内では、辞書のキーに" "をつけない
        strMessage = f'{self.strUserName}left there are {ChatConsumer.rooms[self.strGroupName]["participants_count"]} part'
        # グループ内の全コンシューマーにメッセージ拡散送信（受信関数を'type'で指定）
        data = {
            'type': 'chat_message', #受信処理関数名
            'message':strMessage, #メッセージ
            'username':USERNAME_SYSTEM,
            'datetime':datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')
            }

        #グループから離脱
        await self.channel_layer.group_discard(self.strGroupName,self.channel_name)

        #メンバーがゼロになったらルーム削除
        if(ChatConsumer.rooms[self.strGroupName]['participants_count'] == 0):
            del ChatConsumer.rooms[self.strGroupName]

        #ルーム名を空に
        self.strGroupName = ''



    

