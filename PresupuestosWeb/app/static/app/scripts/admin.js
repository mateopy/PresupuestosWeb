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
        actualizarTotal();
    });

    $(".field-precio input").change(function () {
        actualizarTotal();
    });

    function actualizarTotal() {
        precio = $(".field-precio input").val();
        cantidad = $(".field-cantidad input").val();
        total = precio * cantidad;
        $(".field-subtotal input").val(total);
    }
});

//field-precio


