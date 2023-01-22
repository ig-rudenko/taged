$( function() {

$( "#search" ).autocomplete({
  source: function( request, response ) {
    $.ajax( {
      url: "/ajax/autocomplete",
      data: { term: request.term },
      success: function( data ) {
          response( data.data );
      }
    } );
  },
  minLength: 4,
} );
} );