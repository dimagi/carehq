function ajax_get_form(endpoint_url, doc_id, form_name, target_div, edit_id) {
    //Helper function to help retrieve django backed forms via url, and place it into the target_div.
    //The Form itelf ought to know how to POST itself back.
    //adapted from http://stackoverflow.com/questions/133925/javascript-post-request-like-a-form-submit/133997#133997
    if (edit_id === undefined) {
        var form_url = endpoint_url + "?doc_id=" + doc_id + "&form_name=" + form_name;
    } else {
        var form_url = endpoint_url + "?doc_id=" + doc_id + "&form_name=" + form_name + "&edit_id=" + edit_id;
    }
    $.get(form_url, function (data) {
        var context = $(data);
        context.find('save attribute').click(function () {
        });
        console.log(data);
        $("#" + target_div).html(data).show("blind", {}, 300);
        /* Override the submit handler to the ajax_form. */
        $("#id_" + form_name).submit(function (event) {

            /* stop form from submitting normally */
            event.preventDefault();

            /* get some values from elements on the page: */
            var $form = $(this);
            var url = $form.attr('action');
            var values = $form.serializeArray();
            var submit_dict = {};
            for (var i = 0; i < values.length; i++) {
                submit_dict[values[i]['name']] = values[i]['value'];
            }
            console.log(submit_dict);
            /* Send the data using post and put the results in a div */
            $.ajax({
                        type:"POST",
                        url:url,
                        data:submit_dict,
                        statusCode:{
                            404:function () {
                            },
                            200:function (data) {
                                $("#tbl_" + form_name).html(data);
                            },
                            204:function (data) {
                                location.reload();
                            },
                            500:function (data) {
                                $('body').replaceWith(data.responseText);
                            }


                        },
                        success:function (data, textStatus, jqXHR) {
//                                   #alert("in success:" + textStatus);
//                                    console.log(jqXHR);
                        },
                        error:function (jqXHR, textStatus, errorThrown) {
                            alert(textStatus);
                        }
                    }
            );
        });
    });
}