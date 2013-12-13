var checkProvisions = false;
var provisionList = Array();

setInterval(function() {
    for (var i=0; i<provisionList.length; i++) {
      var objId = provisionList[i];
      $.get(statusUrl + '/' + objId).done(function(data) {
          result = $.parseJSON(data);
          if (!result) {
            $('#provision_' + objId).remove();
            provisionList.splice(index, 1);
          }
          $('#provision_' + objId).html(result.row_html);
          if (result.active) {
            var index = provisionList.indexOf(objId);
            provisionList.splice(index, 1);
          }
        });
    }
}, 5000);

function dnsRegister(objId) {
  var href = $('#quick_' + objId).attr('href');

  $.get(href).done(function(data) {
      result = $.parseJSON(data);

      var messageType = 'error';
      if (result.success) {
        messageType = 'success';
      }

      add_notification(result.message, messageType);
    });
}

