var start = 0, offset = 15, limit = offset, current = 1, end = 1;//总共页数
var count;
var pagePanel = $('<div class="paging-panel"></div>');
var back = $('<a>上一页</a>');
var next = $('<a>下一页</a>');
var jump = $('<a><input type="text" style="width:35px;margin-right: 5px" >跳页</a>');
var countInfo = $('<span></span>')
var pageInfo = $('<span></span>');
var page;
(function () {
    back.click(function () {
        if (current <= 1) return
        else {
            current--;
            start -= offset;

            if (limit == count) limit = (end - 1) * offset;
            else limit -= offset;
            page();
            addPagingPanel();
        }
    })
    next.click(function () {
        if (current >= end)return
        else {
            current++;
            start += offset;
            if ((limit + offset) > count) limit = count
            else limit += offset;
            page();
            addPagingPanel();
        }
    });
    jump.click(function () {
        var input = jump.find('input');
        var index = input.val();
        if (index < 1 || index > end) return;
        current = index;
        start = (current - 1) * offset;
        if (index == end) {
            limit = count;
        }
        else {
            limit = current * offset;
        }
        input.val('');
        page();
        addPagingPanel();
    });


    /*消息提示框
     * */
    $('.tip-panel').animate({
        opacity: "hide"
    }, 4000);
})();
if (window.location.href.indexOf('/shuxin-manager/comment') != -1) {
    $.ajax({
        method: 'post',
        url: '/shuxin-manager/get_post_count',
        success: function (data) {
            count = data;
            addPagingPanel()
        }
    })
}
if (window.location.href.indexOf('/shuxin-manager/user') != -1) {
    limit = offset = 70;
    $.ajax({
        method: 'post',
        url: '/shuxin-manager/get_user_count',
        success: function (data) {
            count = data;
            addPagingPanel();
        }
    })
}

function addPagingPanel() {
    end = Math.ceil(count / offset);
    pageInfo.empty().append(current + '/' + end);
    countInfo.empty().append('&emsp;总共' + count + '条,本页<b><font style="color:blue;">' + limit + '</font></b>条');
    pagePanel.append(back, next, jump, pageInfo, countInfo);
    $('.footer').before(pagePanel)
}

