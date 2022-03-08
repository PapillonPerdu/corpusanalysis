#d'après source : https://www.w3schools.com/howto/howto_css_modals.asp
from IPython.display import display, HTML
import pandas as pd
import numpy as np

htm='''
  <script>
 
    var dialog;
    function saveCitation() {
      alert('coucou!');
    }
 
    dialog = $( "#npb-dialog" ).dialog({
      autoOpen: false,
      height: 400,
      width: 350,
      modal: true,
      buttons: {
        "Enregistrer": saveCitation,
        Cancel: function() {
          dialog.dialog( "close" );
        }
      },
      close: function() {
      }
    });
    $("#nbp-dialog").append('<div id="nbp-titre"></div>')
    $("#nbp-dialog").append('<textarea id="nbp-citations" rows="20" cols="100" ></textarea>');
 
  
  </script>
 
<div id="nbp-dialog" title="">
</div>
 
'''
display(HTML(htm))

js = '''<script> 



function show_citation(nom,variable,value,citation){
if (citation == ''){citation = 'Pas de citation...';}
$('#nbp-titre').html(nom+'/'+variable+' : '+value);
 $('#nbp-citations').html(citation);
 
}

function click_on_val(event,nom,variable,value,citation,instanceName){
    if (event.shiftKey && event.ctrlKey){
    change_citation(nom,variable,instanceName);
    }
    else if (event.ctrlKey){
        change_value(nom,variable,value,instanceName);}
    else {
        show_citation(nom,variable,value,citation);}
    }

function change_value(nom,variable,value,instanceName){
    var newVal = prompt("Remplacer "+nom+"/"+variable+" : "+value+" par : ", value);
    if (newVal != value){
        var command = instanceName+".write_val(\'"+nom+"\',\'"+variable+"\',\'" + newVal + "')";
        console.info(command)
        var kernel = IPython.notebook.kernel;
        kernel.execute(command);}
}

function change_citation(nom,variable,instanceName){
    var command = instanceName+".change_citation(\'"+nom+"\',\'"+variable+ "')";
    var kernel = IPython.notebook.kernel;
    kernel.execute(command);}
    
function hide_modalBox(){
   $('button.close').click(); }
</script>'''
display(HTML(js))
