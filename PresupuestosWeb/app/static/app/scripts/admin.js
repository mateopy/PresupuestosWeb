/*
$(document).ready(function () {
  
    console.log("ola k ase");

});
*/

if (!$) {
    $ = django.jQuery;
}

$(document).ready(function () {
    $(".field-cantidad input").change(function () {
        id = $(this).parent().parent().attr('id');
        //console.log(id);
        actualizarTotal(id);
    });

    $(".field-precio input").change(function () {
        id = $(this).parent().parent().attr('id');
        //console.log(id);
        actualizarTotal(id);
    });

    function actualizarTotal(id) {
        cantidadSelector = '#id_' + id + '-cantidad';
        precioSelector = '#id_' + id + '-precio';
        subtotalselector = '#id_' + id + '-subtotal';
        
        cantidad = $(cantidadSelector).val();
        precio = $(precioSelector).val();

        subtotal = precio * cantidad;

        $(subtotalselector).val(subtotal);
    }
});

//field-precio


