{% block customscripts %}
  <script type="text/javascript">
    $(document).ready(function(){
          $('input[name^=form-]').prop('disabled', true);
          $('select[name^=form-]').prop('disabled', true);
          /*$('[id^="edit_"]').one('click', function(){*/
            $('[id^="edit_"]').click(function(){
              $edit_id = $(this).attr('id');
              $id_num = $edit_id.substring(5,6);
              //alert($id_num);

              //$(this).hide();
              /*$(this).prop('value', 'Save');
              $(this).attr('value','save'); */
               $(this).html('Save');
               $(this).attr('id','save_'+$id_num);
              $(this).after($('<button id="cancel_'+$id_num+'"' + ' class="btn btn-sm btn-danger" type="reset" name="cancel">Cancel</button>'));
              /*$(this).append('<button id="dynamic_cancel" class="btn btn-sm btn-danger" type="reset" name="cancel">Cancel</button>')*/


          });
          $(document).on("click", '[id^="cancel_"]' , function(){
            $cancel_id = $(this).attr('id');
            $id_num = $cancel_id.substring(7,8);
            
            $('#edit_'+$id_num).html('Edit');
            $(this).hide();
            //$(this).html('OK');
            //alert($(this).attr('id'));
            //$('#cancel_4').html('OK');
          });

        });
  </script>
  {% endblock %}