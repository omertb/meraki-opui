// Empty JS for your own code to be here

      $(document).ready(function(){
    $("#selectNewExistingForm").change(function(){
        $(this).find("option:selected").each(function(){
            var optionValue = $(this).attr("value");
            if(optionValue=='new'){
                $("#newNetForm").slideDown();
                $("#existingNetForm").slideUp();
            } else{
                $("#newNetForm").slideUp();
                $("#existingNetForm").slideDown();
                }
            });
        }).change();
    });

     $(document).ready(function(){
    $("#netTypeSelect").change(function(){
        $(this).find("option:selected").each(function(){
            var optionValue = $(this).attr("value");
            if(optionValue=='firewall'){
                $("#templateFormArea").slideDown();
            } else{
                $("#templateFormArea").slideUp();
                }
            });
        }).change();
    });


     var $table = $('#networksTable')
var $button = $('#buttonGetSelections')

       const sleep = (milliseconds) => {
  return new Promise(resolve => setTimeout(resolve, milliseconds))
}
    $(function() {
    $table.on('click-row.bs.table', function (e, row, $element) {
        delayedFunction();
    })
    })


  async function delayedFunction() {
      await sleep(1);
                  $table = $('#networksTable')
            var JSON_Selected = $table.bootstrapTable('getSelections');
            var i;
            var text = "";
            console.log(JSON.stringify(JSON_Selected));
            for (i = 0; i < JSON_Selected.length; i++) {
                text += "ID Number is: " + JSON_Selected[i]['rowNumber'] + "<br>"
            }
            document.getElementById("demo").innerHTML = text;
  }

