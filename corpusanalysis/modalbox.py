from IPython.display import display, HTML
import pandas as pd
import numpy as np

# avec l'aide de : https://gitter.im/jupyter/notebook?at=5ccacda23d78aa6c03d0107d
#https://stackoverflow.com/questions/65823331/cannot-call-python-function-from-javascript-in-notebook
js = ''' 
<style>
.expander {
    height: 1em;
    overflow: hidden;
    cursor: pointer;
}

.expanded {
    cursor: pointer;
}


.mystyle {
    font-size: 11pt; 
    font-family: Arial;
    border-collapse: collapse; 
    border: 1px solid silver;

}

.mystyle thead th {
    text-align: center;
    color:red;}

.mystyle td, th {
    padding: 5px;
    text-align: center;
    vertical-align: top;
    color:black;}

.mystyle tr:nth-child(even) {
    background: #E0E0E0;
}

</style>
<script>

function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#x27;");
 }

 function unescapeHtml(unsafe) {
    return unsafe
         .replace(/&amp;/g, "&")
         .replace(/&lt;/g, "<")
         .replace(/&gt;/g, ">")
         .replace(/&quot;/g, '"')
         .replace(/&#x27;/g, "'");
 }

function show_citation(nom, variable, value, citation,instanceName, target){
    if (citation == '') {citation = 'Pas de citation...';}
    Jupyter.keyboard_manager.disable();
    var dialog_body = $('<div/>').append($("<br/>")).append($('<textarea/>').attr('id','citations').addClass('nbp-textarea').text(unescapeHtml(citation)));
    require(
        ["base/js/dialog"],
        function(dialog)
    {
        dialog.modal({
            title: nom + '/' + variable + ' : ' + value,
            body: dialog_body,
            sanitize: false,
             buttons: {
                            Save: {
                                class: 'btn-danger',
                                click: function() {
                                    var citation = $('#citations')[0].value;
                                    change_citation(escapeHtml(nom), escapeHtml(variable),escapeHtml( citation), instanceName, target);
                                }

                            },
                            Cancel: {
                                click: function() {
                                    Jupyter.keyboard_manager.enable();
                                }

                            }
                        }
        });
    }
    );
}

function click_on_val(event, nom, variable, value, citation, instanceName){
    var target=event.target;
    var value = $(target).html();
    var color=$(target).css('color');
   if (event.ctrlKey){
        change_value(nom, variable, value, instanceName,target);}
    else if (color != 'rgb(0, 0, 0)') {
        alert('Quotations have been changed. The cell must be reloaded.');}
     else{   
        show_citation(nom, variable, value, citation,instanceName,target);}
    }

function change_value(nom, variable, value, instanceName,target)
    {
        var newVal = prompt("Replace " + nom + "/" + variable + " : " + value + " by : ", value);
    if (newVal != value && newVal !== '' && newVal !== null)
    {
        var command = instanceName + ".write_val(\'\'\'" + nom + "\'\'\',\'\'\'" + variable + "\'\'\',\'\'\'" + escapeHtml(newVal) + "\'\'\')";
        var kernel = IPython.notebook.kernel;
        console.info(command);
        kernel.execute(command);
        target.innerHTML=newVal}
    }

function change_citation(nom, variable, citation, instanceName, target){
    var command = instanceName + ".write_quotation(\'\'\'" + nom + "\'\'\',\'\'\'" + variable+ "\'\'\',\'\'\'" +  escapeHtml(citation) + "\'\'\')";
    var  kernel = IPython.notebook.kernel;
    console.info(command);
    kernel.execute(command);
    console.info(target);
    $(target).css('color','red');
    }


function show_var_definition(variable, definition,instanceName){
    if (definition == '') {definition = 'Pas de définition...';}
    Jupyter.keyboard_manager.disable();
    var dialog_body = $('<div/>').append(
                        $("<br/>")
                    ).append(
                        $('<textarea/>').attr('id','nbp-var-definition').attr('class','nbp-textarea').text(unescapeHtml(definition))
                        );
    require(
        ["base/js/dialog"],
        function(dialog)
    {
        dialog.modal({
            title: 'Définition de : ' + variable,
            body: dialog_body,
            sanitize: false,
             buttons: {
                            'New Var Before' : {
                                click: function() {
                                    add_variable(escapeHtml(variable),'before',instanceName);
                                }

                            },
                            Save: {
                                class: 'btn-danger',
                                click: function() {
                                    var definition = $('#nbp-var-definition')[0].value;
                                    change_var_definition( escapeHtml(variable),escapeHtml(definition),instanceName);
                                }

                            },
                             'New Var After' : {
                                click: function() {
                                    add_variable(escapeHtml(variable),'after',instanceName);
                                }

                            },
                            Cancel: {
                                click: function() {
                                    Jupyter.keyboard_manager.enable();
                                }

                            }
                        }
        });
    }
    );
}

function change_var_definition(variable, definition, instanceName){
    var command = instanceName + ".write_var_definition(\'\'\'" + variable + "\'\'\',\'\'\'" + definition + "\'\'\')";
    var  kernel = IPython.notebook.kernel;
    console.info(command);
    kernel.execute(command);
    }



function click_on_var(event, variable, definition, instanceName){
        show_var_definition(variable, definition, instanceName);  
}


function show_nom_definition(nom, definition,instanceName){
    if (definition == '') {definition = 'Pas de définition...';}
    Jupyter.keyboard_manager.disable();
    var dialog_body = $('<div/>').append(
                        $("<br/>")
                    ).append(
                        $('<textarea/>').attr('id','nbp-nom-definition').attr('class','nbp-textarea').text(unescapeHtml(definition))
                        );
    require(
        ["base/js/dialog"],
        function(dialog)
    {
        dialog.modal({
            title: 'Définition de : ' + nom,
            body: dialog_body,
            sanitize: false,
             buttons: {
                            'New Name Before' : {
                                click: function() {
                                    add_nom(escapeHtml(nom),'before',instanceName);
                                }

                            },
                            Save: {
                                class: 'btn-danger',
                                click: function() {
                                    var definition = $('#nbp-nom-definition')[0].value;
                                    change_nom_definition(escapeHtml(nom), escapeHtml(definition), instanceName);
                                }

                            },
                            'New Name After' : {
                                click: function() {
                                    add_nom(escapeHtml(nom),'after',instanceName);
                                }

                            },
                            Cancel: {
                                click: function() {
                                    Jupyter.keyboard_manager.enable();
                                }

                            }
                        }
        });
    }
    );
}

function change_nom_definition(nom, definition, instanceName){
    var command = instanceName + ".write_name_definition(\'\'\'" + nom + "\'\'\',\'\'\'" + definition + "\'\'\')";
    var  kernel = IPython.notebook.kernel;
    console.info(command);
    kernel.execute(command);
    }

function add_variable(variable, position, instanceName){
    newVar = prompt('New variable name : ');
    if (newVar != variable && newVar !== '' && newVar !== null){
        var command = instanceName + ".add_var(\'\'\'" + newVar + "\'\'\',\'\'\'" + variable +"\'\'\',\'\'\'" + position + "\'\'\')";
        var  kernel = IPython.notebook.kernel;
        console.info(command);
        kernel.execute(command);}
    }

function add_nom(nom, position, instanceName){
    newNom = prompt('New name : ');
    if (newNom != nom  && newNom !== '' && newNom !== null){
        idThm = prompt('id Thamous : ');
        if (idThm) { 
            table=prompt('table Thamous : ', 'biblio');
            if (table) {
                projet = prompt('project Thamous : ');}
            }
        if (! idThm || ! table) {
         idThm='';
         table='';
         projet='';}
        var command = instanceName + ".add_name(\'\'\'" + newNom + "\'\'\',\'\'\'" + nom +"\'\'\',position=\'\'\'after\'\'\',id=\'\'\'" + idThm + "\'\'\',table=\'\'\'"+table+"\'\'\',project=\'\'\'" +projet+"\'\'\')";
        var  kernel = IPython.notebook.kernel;
        console.info(command);
        kernel.execute(command);}
    }


function click_on_nom(event, nom, definition, instanceName){
        show_nom_definition(nom, definition, instanceName);  
}

function click_on_var_type_value(event, type, variable, instanceName){
    var target = event.target;
    if (event.ctrlKey){
        toggle_var_type_value(type, variable, instanceName,target);}
        }
        
        
function toggle_var_type_value(type, variable, instanceName, target){
    var newVal = ($(target).html() == '*' ? '' : '*');
    var newValhtml = (newVal== '*' ? '*' : '-');
    var command = instanceName + ".write_var_type_val(\'\'\'"+type+"\'\'\',\'\'\'"+variable+"\'\'\',\'\'\'"+newVal+"\'\'\')";
    var kernel=IPython.notebook.kernel;
    kernel.execute(command);
    console.info(command);
    target.innerHTML=newValhtml;

    }
    
function click_on_nom_type_value(event, type, nom, instanceName){
    var target = event.target;
    if (event.ctrlKey){
        toggle_nom_type_value(type, nom, instanceName,target);}
        }
        
function toggle_nom_type_value(type, nom, instanceName, target){
    var newVal = ($(target).html() == '*' ? '' : '*');
    var newValhtml = (newVal== '*' ? '*' : '-');
    var command = instanceName + ".write_name_type_val(\'\'\'"+type+"\'\'\',\'\'\'"+nom+"\'\'\',\'\'\'"+newVal+"\'\'\')";
    var kernel=IPython.notebook.kernel;
    kernel.execute(command);
    console.info(command);
    target.innerHTML=newValhtml;

    }
</script> '''
display(HTML(js))