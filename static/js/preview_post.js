$(document).ready(
  function (){
      // Наведение на объект
      $('.post-link').mouseover(function (){
          let post_id = $(this).attr('id');
          let content_post = $('#content-'+post_id)

          if (content_post.html()) {
              // Скрываем все открытые элементы
              $('.pre_post_visible').removeClass('pre_post_visible').addClass('pre_post_hidden')
              // Показываем
              content_post.removeClass('pre_post_hidden').addClass('pre_post_visible');
          } else {
              // Загружаем, если нет
              $.ajax( {
                url: "/ajax/extend_post/" + post_id,
                success: function( data ) {
                    // Скрываем все открытые элементы
                    $('.pre_post_visible').removeClass('pre_post_visible').addClass('pre_post_hidden')
                    // Затем показываем
                    content_post.html(data.post).removeClass('pre_post_hidden').addClass('pre_post_visible');
                }
              } );
          }
      }).mouseleave(function (){
          // Скрываем все открытые элементы
          $('.pre_post_visible').removeClass('pre_post_visible').addClass('pre_post_hidden')
      })
  }
);