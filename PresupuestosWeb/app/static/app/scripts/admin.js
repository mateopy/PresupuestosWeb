/*
$(document).ready(function () {
  
    console.log("ola k ase");

});
*/

if (!$) {
    $ = django.jQuery;
}

$(document).ready(function () {
    $('.field-subtotal input').prop('readonly', true);

    $(".field-cantidad input").change(function () {
        id = $(this).parent().parent().attr('id');
        console.log(id);
        actualizarTotal(id);
    });

    $(".field-precio input").change(function () {
        id = $(this).parent().parent().attr('id');
        console.log(id);
        actualizarTotal(id);
    });

    $(".field-articulo select").change(function () {

        const pk = $(this).val();
        const articulo_id = this.id.replace("-articulo", "-descripcion");

        //console.log(id);
        $.get("/app/get_articulo?id_articulo=" + pk, function (data) {

            if (data.descripcion) {
                $("#" + articulo_id).val(data.descripcion);
            }

        });
    });

    function actualizarTotal(id) {
        cantidadSelector = '#id_' + id + '-cantidad';
        precioSelector = '#id_' + id + '-precio';
        subtotalselector = '#id_' + id + '-subtotal';
        
        cantidad = $(cantidadSelector).val();
        precio = $(precioSelector).val();

        subtotal = precio * cantidad;
        console.log(cantidad, precio, subtotal);
        console.log(subtotalselector);

        $(subtotalselector).val(subtotal);
    }
});

//field-precio


