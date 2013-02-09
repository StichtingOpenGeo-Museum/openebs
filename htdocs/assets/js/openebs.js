    var authorization = null;

       $(document).ready(function() {
        $.ajaxSetup({cache:false});
        initopenlayers();
        $(".limit").limit({ maxChars: 255, warnChars: 78, counter: "#counter" });
        $(".limit").limit({ maxChars: 255, warnChars: 78, counter: "#scenariocounter" });
        updateBerichten();

        $('#planningstarttime').timepicker({template: false, showSeconds: true, showMeridian: false, showInputs: true, minuteStep: 1});
        $('#planningendtime').timepicker({template: false, showSeconds: true, showMeridian: false, showInputs: true, minuteStep: 1});


$('.btn-group > .btn, .btn[data-toggle="button"]').click(function() {

        if($(this).attr('class-toggle') != undefined && !$(this).hasClass('disabled')){
            var btnGroup = $(this).parent('.btn-group');

            if(btnGroup.attr('data-toggle') == 'buttons-radio') {
                btnGroup.find('.btn').each(function() {
                    $(this).removeClass($(this).attr('class-toggle'));
                });
                $(this).addClass($(this).attr('class-toggle'));
            }

            if(btnGroup.attr('data-toggle') == 'buttons-checkbox' || $(this).attr('data-toggle') == 'button') {
                if($(this).hasClass('active')) {
                    $(this).removeClass($(this).attr('class-toggle'));
                } else {
                    $(this).addClass($(this).attr('class-toggle'));
                }
             }
          }
      });



       });

            $.getJSON('/settings.js', function(auth) {
                authorization = auth;
                if (authorization['scenario_create'] === true) { $("#auth_messagescenario").attr('style', ''); }
                $("#username").html(authorization['username']);
            });

       $('a[data-toggle="tab"]').on('show', function (e) {
         if ($(e.target).attr('href') == '#map') {
            $('#map').css('width', '100%');
         } else if ($(e.target).attr('href') == '#lijnen') {
		$('#map').css('width', ($(window).width() - $("#lijnen").width() + 15));
         } else {
            if ($(e.target).attr('href') == '#berichten') {
                updateBerichten();
            } else if ($(e.target).attr('href') == '#scenario') {
                updateScenario();
            }

            $('#map').css('width', '50%');
         }
       });

       $('a[data-toggle="tab"]#tab-lijnen').on('shown', function (e) {
       	$('#map').css('width', ($(window).width() - $("#lijnen").width() + 15));
       });

      $('#input-scenario').keyup(function() {
      	if (this.value.length == 0) {
	   $("#input04").removeAttr("disabled");
	   $("#input05").removeAttr("disabled");
	   $("#nieuw-submit").text('Publiceer');
	} else {
	   $("#input04").attr("disabled", "disabled");
	   $("#input05").attr("disabled", "disabled");
	   $("#nieuw-submit").text('Opslaan');
	}
      });

      function signout() {
        $.ajax({type: "GET", url: "https://uitloggen@openebs.nl", dataType: "html"})
        .fail(function (data) {
            document.location = 'https://google.com/';
        })
      }
