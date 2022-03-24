    //const 再代入できない変数
    const g_elementDivJoinScreen = document.getElementById("div_join_screen");
    const g_elementDivChatScreen = document.getElementById("div_chat_screen");
    const g_elementInputUserName = document.getElementById("input_username");
    const g_elementInputRoomName = document.getElementById( "input_roomname" );
    const g_elementTextUserName = document.getElementById( "text_username" );
    const g_elementTextRoomName = document.getElementById( "text_roomname" );
    const g_elementInputMessage = document.getElementById("input_message");
    const g_elementListMessage = document.getElementById("list_message");

    //WebSocletオブジェクト ws,wss websocket用のプロトコル　wssはセキュア通信
    // 変数 =　条件 ? True : False;
    let ws_scheme = window.location.protocol == "https:" ? "wss":"ws";
    const g_socket = new WebSocket(ws_scheme +"://"+ window.location.host + "/ws/chat/");
    console.log(window.location.host)


    //joinを押したら呼ばれる関数
    function onsubmitButton_JoinChat(){
        console.log("joinが押されました")
        //ユーザー名
        let strInputUserName = g_elementInputUserName.value;
        let strInputRoomName = g_elementInputRoomName.value;
        if(!strInputUserName){
            return;
        }
        g_elementTextUserName.value = strInputUserName
        g_elementTextRoomName.value = strInputRoomName

        console.log(g_elementTextUserName.value)
        // サーバーに"join"を送信
        //.stringify オブジェクトをJSON文字列として取得
        g_socket.send(JSON.stringify({"data_type":"join","username":strInputUserName,"roomname":strInputRoomName}));
        console.log(JSON.stringify({"data_type":"join","username":strInputUserName,"roomname":strInputRoomName}));

        //画面の切り替え "block"はblock(横幅いっぱい)
        // g_elementDivJoinScreen.style.display = "none";
        // g_elementDivChatScreen.style.display = "block";
    }
    // 「Leave Chat.」ボタンを押すと呼ばれる関数
    function onclickButton_LeaveChat(){
        //メッセージリストのクリア
        //firstChild g_elementListMessageの最初の子ノード
        while(g_elementListMessage.firstChild){
            g_elementListMessage.removeChild(g_elementListMessage.firstChild);
            }
            
            // ユーザー名
            g_elementTextUserName.value = "";

            //サーバーにleaveを送信
            g_socket.send(JSON.stringify({"data_type":"leave"}));

            //画面切り替え
            // g_elementDivChatScreen.style.display = "none";
            // g_elementDivJoinScreen.style.display = "flex";
    }
    
    // Sendを押したときの処理
    function onsubmitButton_Send(){
        console.log("Sendが実行されました")
        //送信用テキストhtml要素からメッセージ文字列の取得
        let strMessage = g_elementInputMessage.value;
        if(!strMessage){
            console.log("aaa")
            return;
        }
        //WebSocketを通したメッセージの送信
        g_socket.send(JSON.stringify({"message":strMessage}));
        console.log(strMessage)
        console.log(JSON.stringify({"message":strMessage}))
        //送信用テキストhtml要素の中身クリア
        g_elementInputMessage.value = "";
    }

    // WebSocketからメッセージ受信時の処理
    // アロー関数 (引数) =>{処理} 要するに無名関数
    g_socket.onmessage = (event) =>{

        //自身がまだ参加していないときは無視
        if(!g_elementTextUserName.value){
            return;
        }

        //テキストデータをjsonにデコード
        let data = JSON.parse(event.data);

        //メッセージの整形
        //let strMessage = data["message"];
        let strMessage = data["datetime"] + "-[" + data["username"] + "]-" + data["message"];

        //拡散されたメッセージをメッセージリストに追加
        //createElement liタグの要素作成
        let elementLi = document.createElement("li");
        elementLi.textContent = strMessage;
        g_elementListMessage.prepend(elementLi); //リストの一番上に追加
        console.log(g_elementListMessage)
        //g_elementInputMessage.append(elementLi); //リストの一番下に追加
    };
    //WebSocketクローズ処理
    g_socket.onclose = (event) =>{
        //ページを閉じたとき以外のSocketクローズは想定外
        console.error("Unexpected: Chat socket closed.");
    };