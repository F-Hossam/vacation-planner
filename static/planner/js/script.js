$(document).ready(function() {

    function add_hobbies(name){
        $('#hobbies').val($('#hobbies').val() + name + ', ');
    }
    
    function remove_hobbies(name){
        $('#hobbies').val($('#hobbies').val().replace(name + ', ', ''));
    }
    
    $('.add-hobbie-btn').click(function() {
        var hobbie_name = $(this).attr('id');
        var hobbie_child = $(this).children('.hobbie-btn-child');
        if (hobbie_child.hasClass("bg-gray-200")){
            hobbie_child.removeClass("bg-gray-200");
            hobbie_child.addClass("bg-green-300");
            add_hobbies(hobbie_name);
        }else{
            hobbie_child.removeClass("bg-green-300");
            hobbie_child.addClass("bg-gray-200");
            remove_hobbies(hobbie_name);
        }
    });
    
    $('#create-btn').click(function(){
        $('.loader-container').removeAttr("hidden");
    });

    $('#low-options-btn, #standard-options-btn, #again-btn, #expensive-options-btn').click(function(){
        $('.loader-container').removeAttr("hidden");
    });
});