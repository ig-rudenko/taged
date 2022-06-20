hashCode = s => String(s.split('').reduce((a,b)=>{a=((a<<5)-a)+b.charCodeAt(0);return a&a},0))

function create_tags(tags, tags_name) {
	if (tags_name === 'tags-off') {
		var tags_class = 'tag-in tag-off'
	} else {
		var tags_class = 'tag-in'
	}
	$('#tag-start-'+tags_name).after(`<div id="tags_all-`+tags_name+`"><div id="tags-`+tags_name+`"></div></div>`)
	for (let i=0;i<tags.length;i++) {

		if (i !== 0) {
			$('#'+hashCode(tags[i-1].value+tags_name)).after(
				`<a class="`+tags_class+`" id="`+ hashCode(tags[i].value+tags_name) +`">`+tags[i].value+`</a>`)
		} else {
			$('#tags-'+tags_name).after(`<a class="`+tags_class+`" id="`+ hashCode(tags[i].value+tags_name) +`">`+tags[i].value+`</a>`)
		}
	}
}
(function($) {
	function setChecked(target) {
		var checked = $(target).find("input[type='checkbox']:checked");


		// Определяем имя блока тегов
		var tags_name = $(target).find("input[type='checkbox']")[0].name
		console.log(tags_name)

		// Удаляем созданные теги
		if (document.getElementById('tags_all-'+tags_name)) {
			document.getElementById('tags_all-'+tags_name).remove()
        }

		// Создаем теги заново
        create_tags(checked, tags_name)

		// Создаем подпись
		if (tags_name === 'tags-off') {
			var desc = '– tag'
		} else {
			var desc = '+ tag'
		}
		if (checked.length) {
			$(target).find('select option:first').html(desc + ': ' + checked.length);
		} else {
			$(target).find('select option:first').html(desc);
		}
	}

	$.fn.checkselect = function() {
		this.wrapInner('<div class="checkselect-popup"></div>');
		this.prepend(
			'<div class="checkselect-control">' +
				'<select class="form-control"><option></option></select>' +
				'<div class="checkselect-over"></div>' +
			'</div>'
		);

		this.each(function(){
			setChecked(this);
		});
		this.find('input[type="checkbox"]').click(function(){
			setChecked($(this).parents('.checkselect'));
		});

		this.parent().find('.checkselect-control').on('click', function(){
			$popup = $(this).next();
			$('.checkselect-popup').not($popup).css('display', 'none');
			if ($popup.is(':hidden')) {
				$popup.css('display', 'block');
				$(this).find('select').focus();
			} else {
				$popup.css('display', 'none');
			}
		});

		$('html, body').on('click', function(e){
			if ($(e.target).closest('.checkselect').length === 0){
				$('.checkselect-popup').css('display', 'none');
			}
		});
	};
})(jQuery);

$('.checkselect').checkselect();
