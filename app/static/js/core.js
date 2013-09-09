$('form').parsley({ 
    successClass: 'has-success', 
    errorClass: 'has-error',
    errors: {
        classHandler: function (element) {
            return $(element).parent();
        },
        container: function (element) {
            var $container = element.parent().find(".help-block");
            if ($container.length === 0) {
		$container = $("<span class='help-block'></span>").insertAfter(element);
            };
            return $container;
        },
        errorsWrapper: '<ul class="list-unstyled"></ul>'
    }});

$(document).ready(function() {
    $('a[data-confirm]').click(function(ev) {
        href = $(this).attr('href');
	
        ev.preventDefault();
        bootbox.confirm($(this).attr('data-confirm'), function(result) {
            if (result) {
                window.location.replace(href);
            }
        });
    });

    window.setTimeout(function() {
	$(".alert-success").fadeTo(1000, 0).slideUp(1000, function(){
	    $(this).remove(); 
	});
    }, 2000);
});

function add_notification(message, type) {
    var div = $('#notifications');
    var alert_class = 'alert-danger';

    if (type == 'success') {
	alert_class = 'alert-success';
	window.setTimeout(function() {
	    $(".alert-success").fadeTo(1000, 0).slideUp(1000, function(){
		$(this).remove(); 
	    });
	}, 2000);
    }

    div.append('<div class="alert ' + alert_class + ' fade in"><a class="close" data-dismiss="alert" href="#" aria-hidden="true">&times;</a>' + message + '<br/></div>');
}
