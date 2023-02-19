$(function () {
    var source = new EventSource("/stream");
    source.addEventListener('progress-item', function (event) {
        $('.progress-bar').css('width', event.data + '%').attr('aria-valuenow', event.data);
        $('.progress-bar-label').text(event.data + '%');
    }, false);
    source.addEventListener('last-item', function () {
        source.close();
        $('.progress-bar').css('width', '100%').attr('aria-valuenow', 100);
        $('.progress-bar-label').text('100%');
    }, false);

    $("#ajax").click(function () {
        $.post('/ajax', 'data=処理開始', null, "json").done(function (data, textStatus, jqXHR) {
            const result = JSON.parse(data);
            console.log(result.data)
            $("#result_img").html('<img id="img" src="static/outputs/' + result.id + '.jpg">');
            $("#result_smile_score").html("スマイルスコア：" + result.smileScore);
            $("#download_container").html(
                '<button type="submit" class="btn btn-primary">ダウンロード</button>'
            );
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert("処理失敗")
        });
    });
});