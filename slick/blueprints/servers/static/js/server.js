function serverAction(serverId, action) {
    var href = $('#' + action + '_' + serverId).attr('href')
    if (action == 'reload') {
      var message = 'This will erase the server and restore it to the base OS!';
    } else if (action == 'soft_reboot') {
      var message = 'This will attempt to reboot the server using the normal operating system method.';
    } else if (action == 'hard_reboot') {
      var message = 'This will simulate a power cycle of the server!';
    } else {
      var message = 'You are attempting to perform an unknown action.';
    }

    var hostname = $('#server_' + serverId).find('.server_hostname').html();
    bootbox.confirm("<h3 class='text-danger'>" + hostname + "</h3>" + message + "<br><br>Are you sure you want to continue?", function(result) {
        if (result) {
          $.get(href).done(function(data) {
              result = $.parseJSON(data);

              var messageType = 'error';
              if (result.success) {
                messageType = 'success';
                provisionList.push(serverId);
              }

              add_notification(result.message, messageType);
            });
        }
      }); 
}
