(function () {
    const socket = new WebSocket('ws://localhost:55555');
    console.log("socket script")
    // 接続時のイベント
    socket.onopen = function (evt) {
        console.log("socket open")
        document.getElementById("good").style.display = "none"
        document.getElementById("bad").style.display = "none"
        document.getElementById("excellent").style.display = "none"
    };

    // 切断時のイベント
    socket.onclose = function (evt) {
        console.log('Disconnected');
    };

    // メッセージ受信時のイベント
    socket.onmessage = function (evt) {
        console.log("message受信");
        console.log(evt.data);
        if (evt.data === 'good') {
            document.getElementById("good").style.display = "block"
            document.getElementById("bad").style.display = "none"
            document.getElementById("excellent").style.display = "none"
        } else if (evt.data === 'bad') {
            document.getElementById("good").style.display = "none"
            document.getElementById("bad").style.display = "block"
            document.getElementById("excellent").style.display = "none"
        } else if (evt.data === 'excellent') {
            document.getElementById("good").style.display = "none"
            document.getElementById("bad").style.display = "none"
            document.getElementById("excellent").style.display = "block"
        }
    };

    // エラー発生時のイベント
    socket.onerror = function (evt) {
        console.log('Error: ' + evt.data);
    };

}());
