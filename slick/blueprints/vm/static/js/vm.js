function vmAction(vmId, action) {
    var href = $('#' + action + '_' + vmId).attr('href')
    if (action == 'reload') {
	var message = 'This will erase the VM and restore it to the base OS!';
    } else if (action == 'soft_reboot') {
	var message = 'This will attempt to reboot the VM using the normal operating system method.';
    } else if (action == 'hard_reboot') {
	var message = 'This will simulate a power cycle of the VM!';
    } else if (action == 'cancel') {
	var message = 'This will immediately cancel the VM, destroying all data on the system!';
    } else if (action == 'stop') {
	var message = 'This will stop the VM, prevending it from being used.';
    } else if (action == 'start') {
	var message = 'This will start the VM.';
    } else {
	var message = 'You are attempting to perform an unknown action.';
    }

    var hostname = $('#provision_' + vmId).find('.vm_hostname').html();
    bootbox.confirm("<h3 class='text-danger'>" + hostname + "</h3>" + message + "<br><br>Are you sure you want to continue?", function(result) {
        if (result) {
          $.get(href).done(function(data) {
              result = $.parseJSON(data);

              var messageType = 'error';
              if (result.success) {
                messageType = 'success';
                provisionList.push(vmId);
              }

              add_notification(result.message, messageType);
            });
        }
      }); 
}

